#!/usr/bin/env python3
"""
Chicago taxi shift/work-hour research crawler.

Dependency-free, respectful web crawler (stdlib only) that collects evidence
about Chicago taxi shift / work-hour / operating-hour practices for a
data-engineering portfolio project. It runs a set of DuckDuckGo HTML queries,
fetches promising result pages (honoring robots.txt, per-host rate limits and
a download cap), extracts readable text, and records evidence passages that
mention shift/hour/medallion/chauffeur/BACP/lease.

Context: "shift" is ambiguous. It can mean (A) legal/regulatory operating
hours a taxi may be on the street, (B) a driver's actual work shift (lease
shift, 12-hour day/night), (C) a vehicle's operational shift as dispatched,
or (D) a dispatch/garage schedule, or (E) an analytical shift used in data
analysis (e.g. partitioning trips by 12h windows). This tool deliberately
gathers broad evidence across all of these so a downstream analysis can
classify which meaning each source reflects.

Usage:
    python3 chicago_taxi_shift_research.py                # run the crawl
    python3 chicago_taxi_shift_research.py --dry-run      # list queries + targets, no network
    python3 chicago_taxi_shift_research.py --self-test    # offline checks, no network
    python3 chicago_taxi_shift_research.py --refresh --max-pages 40
    python3 chicago_taxi_shift_research.py --output-dir /tmp/out --cache-dir /tmp/cache
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.robotparser
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEARCH_QUERIES = [
    "Chicago taxi driver shift hours",
    "Chicago taxi shifts",
    "Chicago cab driver shifts",
    "Chicago taxi 12 hour shift",
    "Chicago cab 12 hour shift",
    "Chicago taxi day shift night shift",
    "Chicago taxi driver work hours",
    "Chicago taxi driver hours",
    "Chicago taxi operating hours",
    "Chicago taxi medallion shift",
    "Chicago taxi shift schedule",
    "Chicago cab shift schedule",
    "Chicago taxi driver lease shift",
    "Chicago taxi work session",
    "Chicago taxi day night operations",
    "Chicago taxi fleet shift",
    "Chicago taxi driver hours ordinance",
    "Chicago taxi labor shift ordinance",
    "Chicago BACP taxi hours",
    "Chicago municipal code taxi driver hours",
    "Chicago cab driver shifts 2014",
    "Chicago taxi driver hours 2019",
]

DDG_ENDPOINT = "https://html.duckduckgo.com/html/"
USER_AGENT = "taxi-shift-research-bot/1.0 (academic portfolio research; contact: none)"
TIMEOUT = 15
MAX_RETRIES = 3
RATE_LIMIT_SAME_HOST = 2.0
RATE_LIMIT_GLOBAL = 1.0
MAX_RESULTS_PER_QUERY = 8
MAX_BYTES_PER_PAGE = 2 * 1024 * 1024  # 2MB
MAX_EVIDENCE_PER_PAGE = 12
MAX_EVIDENCE_CHARS = 400

# Regex for keyword groups used in evidence extraction.
EVIDENCE_PATTERN = re.compile(
    r"\bshift|hour|medallion|chauffeur|BACP|lease", re.IGNORECASE
)
# Rough sentence splitter: end punctuation followed by space + capital.
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")

TRACKING_PARAMS = re.compile(r"^(utm_|fbclid|gclid)", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class FetchResult:
    url: str
    final_url: str
    title: str
    meta_description: str
    publication_date_hint: str
    fetch_timestamp_utc: str
    cached: bool
    http_status: int
    source_category: str
    authority_level: str
    search_query_found_for: list = field(default_factory=list)
    evidence_passages: list = field(default_factory=list)


@dataclass
class Summary:
    started_utc: str = ""
    finished_utc: str = ""
    queries_run: int = 0
    urls_seen: int = 0
    pages_fetched: int = 0
    pages_skipped_robots: int = 0
    pages_failed: int = 0
    notes: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

# substring -> (category, authority)  checked in order.
CLASSIFIER_RULES = [
    # code / legal sources first (most authoritative legal text)
    ("amlegal.com", ("code", "regulatory")),
    ("municode.com", ("code", "regulatory")),
    ("municipal code", ("code", "regulatory")),
    ("ordinance", ("code", "regulatory")),
    # government
    ("data.cityofchicago.org", ("portal", "data-provider")),
    ("cityofchicago.org", ("city", "official")),
    ("ilga.gov", ("state", "official")),
    ("illinois.gov", ("state", "official")),
    (".gov", ("state", "official")),
    # academic
    (".edu", ("academic", "secondary")),
    ("journal", ("academic", "secondary")),
    ("study", ("academic", "secondary")),
    ("research", ("academic", "secondary")),
    # taxi industry / companies
    ("yellowcab", ("company", "primary-industry")),
    ("flashcab", ("company", "primary-industry")),
    ("checker", ("company", "primary-industry")),
    ("taxi association", ("association", "primary-industry")),
    ("cab association", ("association", "primary-industry")),
    ("bacta", ("association", "primary-industry")),
    # industry news / trade press
    ("taxicabmagazine", ("industry", "secondary")),
    ("taxi industry", ("industry", "secondary")),
    # forum / anecdotal
    ("reddit.com", ("forum", "anecdotal")),
    ("forum.", ("forum", "anecdotal")),
    ("blog.", ("forum", "anecdotal")),
    # news
    ("nytimes", ("news", "tertiary")),
    ("chicagotribune", ("news", "tertiary")),
    ("suntimes", ("news", "tertiary")),
    ("chicagosuntimes", ("news", "tertiary")),
    ("bloomberg", ("news", "tertiary")),
    ("reuters", ("news", "tertiary")),
    ("patch.com", ("news", "tertiary")),
    ("wttw", ("news", "tertiary")),
    ("blockclubchicago", ("news", "tertiary")),
    ("abc7", ("news", "tertiary")),
    ("cbs", ("news", "tertiary")),
    ("wbez", ("news", "tertiary")),
    ("chicagobusiness", ("news", "tertiary")),
    ("crains", ("news", "tertiary")),
]


def classify(url: str, title: str) -> tuple[str, str]:
    """Return (category, authority) based on URL/title substrings."""
    url_l = url.lower()
    title_l = (title or "").lower()
    for needle, (category, authority) in CLASSIFIER_RULES:
        if needle in url_l or needle in title_l:
            # Company heuristic: explicit "taxi"+"company" in title.
            if ("company" in title_l or "cab company" in title_l) and (
                "taxi" in title_l or "cab" in title_l
            ):
                return ("company", "primary-industry")
            return (category, authority)
    # Defaults
    if "chicago" in url_l or "chicago" in title_l:
        return ("portal", "secondary")
    return ("other", "tertiary")


# ---------------------------------------------------------------------------
# URL utilities
# ---------------------------------------------------------------------------


def normalize_url(url: str) -> str:
    """Lowercase scheme+host, drop fragment, strip tracking params."""
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return url.lower()
    scheme = parsed.scheme.lower()
    host = parsed.hostname.lower() if parsed.hostname else ""
    # Rebuild path/query without tracking params.
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query = [(k, v) for k, v in query if not TRACKING_PARAMS.match(k)]
    clean_query = urllib.parse.urlencode(query)
    netloc = host
    if parsed.port:
        netloc = f"{host}:{parsed.port}"
    return urllib.parse.urlunsplit((scheme, netloc, parsed.path, clean_query, ""))


def cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# HTML parsing
# ---------------------------------------------------------------------------


class TextExtractor(HTMLParser):
    """Collect text and metadata, dropping script/style/noscript."""

    SKIP_TAGS = {"script", "style", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text_parts: list[str] = []
        self.skip_depth = 0
        self.title = ""
        self.meta_description = ""
        self.publication_date_hint = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            d = dict(attrs)
            name = (d.get("name") or d.get("property") or "").lower()
            # valueless attrs (e.g. <meta name=description>) come back as None
            content = d.get("content") or ""
            if name == "description":
                if not self.meta_description:
                    self.meta_description = content.strip()
            if name in (
                "article:published_time",
                "og:published_time",
                "og:updated_time",
                "date",
                "date-published",
                "pubdate",
            ):
                self.publication_date_hint = content.strip()

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self._in_title and not self.title:
            self.title = data.strip()
        text = data.strip()
        if text:
            self.text_parts.append(text)


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_text(html: str) -> TextExtractor:
    p = TextExtractor()
    try:
        p.feed(html)
    except Exception:
        pass
    return p


def extract_evidence(full_text: str, title: str, description: str) -> list[str]:
    """Find sentences mentioning shift/hour/medallion/etc, up to a cap."""
    if title:
        full_text = f"{title}. {full_text}"
    if description:
        full_text = f"{description}. {full_text}"
    candidates = SENTENCE_SPLIT.split(full_text)
    matches = []
    for sentence in candidates:
        if EVIDENCE_PATTERN.search(sentence):
            snippet = collapse_whitespace(sentence)[:MAX_EVIDENCE_CHARS]
            if snippet:
                matches.append(snippet)
        if len(matches) >= MAX_EVIDENCE_PER_PAGE:
            break
    return matches


# ---------------------------------------------------------------------------
# Fetching with robots/rate-limit/retry
# ---------------------------------------------------------------------------


class Fetcher:
    def __init__(self, delay: float, cache_dir: Path, refresh: bool):
        self.delay = delay
        self.cache_dir = cache_dir
        self.refresh = refresh
        self.robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last_req_time: dict[str, float] = {}
        self._last_any_time = 0.0

    def _rate_limit(self, host: str):
        now = time.monotonic()
        host_delay = self._last_req_time.get(host, 0.0) + self.delay - now
        global_delay = self._last_any_time + RATE_LIMIT_GLOBAL - now
        wait = max(host_delay, global_delay, 0.0)
        if wait > 0:
            time.sleep(wait)

    def robots_allowed(self, host: str, path: str) -> bool:
        rp = self.robots.get(host)
        if rp is None:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"https://{host}/robots.txt")
            try:
                rp.read()
            except Exception:
                # On failure, assume allowed (be permissive on parse errors).
                pass
            self.robots[host] = rp
        return rp.can_fetch(USER_AGENT, path)

    def fetch(self, url: str) -> tuple[str, int, bool] | None:
        """Return (final_url, http_status, cached) or None on skip/failure."""
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme not in ("http", "https"):
            return None
        host = parsed.hostname or ""
        path = parsed.path or "/"

        if not self.robots_allowed(host, path):
            return None

        key = cache_key(url)
        cache_file = self.cache_dir / f"{key}.html"
        if cache_file.exists() and not self.refresh:
            try:
                html = cache_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                html = ""
            if html:
                return (url, 200, True)

        self._rate_limit(host)
        body = b""
        status = 0
        backoff = [2.0, 4.0]
        for attempt in range(MAX_RETRIES):
            self._last_any_time = time.monotonic()
            self._last_req_time[host] = self._last_any_time
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    status = resp.getcode() or 200
                    ctype = (resp.headers.get("Content-Type") or "").lower()
                    if "text/html" not in ctype and "text/plain" not in ctype:
                        return None  # skip binary/other content types
                    body = resp.read(MAX_BYTES_PER_PAGE + 1)
                    if len(body) > MAX_BYTES_PER_PAGE:
                        body = body[:MAX_BYTES_PER_PAGE]
                    final_url = resp.geturl()
                    break
            except urllib.error.HTTPError as e:
                status = e.code
                if status == 429:
                    # Back off once (30s), then give up on this URL.
                    time.sleep(30.0)
                    return None
                if status >= 500:
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(backoff[attempt])
                        continue
                    return None
                return None
            except Exception:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(backoff[attempt])
                    continue
                return None
        else:
            return None

        if not body:
            return None

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            cache_file.write_text(body.decode("utf-8", errors="replace"), encoding="utf-8")
        except OSError:
            pass
        return (final_url, status, False)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class DDGResultParser(HTMLParser):
    """Extract result (title, url) pairs from the DuckDuckGo HTML page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.results: list[tuple[str, str]] = []
        self._href = None
        self._in_title = False
        self._title = ""

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get("class") or ""
        if tag == "a" and "result__a" in cls:
            self._href = d.get("href")
            self._in_title = True
            self._title = ""

    def handle_endtag(self, tag):
        if tag == "a" and self._in_title:
            if self._href:
                self.results.append((self._title.strip(), self._href))
            self._in_title = False
            self._href = None

    def handle_data(self, data):
        if self._in_title:
            self._title += data


def duckduckgo_search(query: str, fetcher: Fetcher) -> list[str]:
    """Return list of normalized URLs for a query (respecting robots/rate limits)."""
    params = urllib.parse.urlencode({"q": query})
    search_url = f"{DDG_ENDPOINT}?{params}"
    fetched = fetcher.fetch(search_url)
    if not fetched:
        return []
    _, _, cached = fetched
    html = ""
    key = cache_key(search_url)
    cache_file = fetcher.cache_dir / f"{key}.html"
    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8", errors="replace")
    parser = DDGResultParser()
    try:
        parser.feed(html)
    except Exception:
        pass
    urls = []
    for title, href in parser.results:
        # DDG wraps real URLs in a redirect parameter.
        real = extract_ddg_target(href)
        if real and real.startswith(("http://", "https://")):
            urls.append(normalize_url(real))
    return urls


def extract_ddg_target(href: str) -> str | None:
    """Pull the underlying URL out of a DDG redirect link if present."""
    parsed = urllib.parse.urlsplit(href)
    qs = urllib.parse.parse_qs(parsed.query)
    if "uddg" in qs:
        return urllib.parse.unquote(qs["uddg"][0])
    return href


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_crawl(args) -> tuple[list[FetchResult], Summary]:
    summary = Summary(started_utc=datetime.now(timezone.utc).isoformat())
    cache_dir = Path(args.cache_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    fetcher = Fetcher(args.delay, cache_dir, args.refresh)
    seen: dict[str, FetchResult] = {}
    all_urls: dict[str, list[str]] = {}  # normalized url -> queries found in

    for query in SEARCH_QUERIES:
        summary.queries_run += 1
        print(f"[query] {query}")
        found = duckduckgo_search(query, fetcher)[:MAX_RESULTS_PER_QUERY]
        for url in found:
            all_urls.setdefault(url, [])
            if query not in all_urls[url]:
                all_urls[url].append(query)

    summary.urls_seen = len(all_urls)

    page_cap = args.max_pages
    for url, queries in all_urls.items():
        if summary.pages_fetched >= page_cap:
            summary.notes.append("hit --max-pages cap")
            break
        if url in seen:
            # Merge query into existing record; don't re-fetch.
            existing = seen[url]
            for q in queries:
                if q not in existing.search_query_found_for:
                    existing.search_query_found_for.append(q)
            continue

        fetched = fetcher.fetch(url)
        if fetched is None:
            summary.pages_skipped_robots += 1
            continue
        final_url, status, cached = fetched
        html = ""
        key = cache_key(url)
        cache_file = cache_dir / f"{key}.html"
        if cache_file.exists():
            html = cache_file.read_text(encoding="utf-8", errors="replace")
        if not html:
            summary.pages_failed += 1
            continue

        summary.pages_fetched += 1
        extractor = extract_text(html)
        full_text = collapse_whitespace(" ".join(extractor.text_parts))
        category, authority = classify(url, extractor.title)
        evidence = extract_evidence(full_text, extractor.title, extractor.meta_description)

        record = FetchResult(
            url=url,
            final_url=final_url,
            title=extractor.title,
            meta_description=extractor.meta_description,
            publication_date_hint=extractor.publication_date_hint,
            fetch_timestamp_utc=datetime.now(timezone.utc).isoformat(),
            cached=cached,
            http_status=status,
            source_category=category,
            authority_level=authority,
            search_query_found_for=list(queries),
            evidence_passages=evidence,
        )
        seen[url] = record
        print(f"[fetch] {status}{' (cached)' if cached else ''} {url}")

    summary.finished_utc = datetime.now(timezone.utc).isoformat()
    records = list(seen.values())
    write_outputs(records, summary, output_dir)
    return records, summary


def write_outputs(records: list[FetchResult], summary: Summary, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "sources.json", "w", encoding="utf-8") as f:
        json.dump([r.__dict__ for r in records], f, indent=2)

    fields = [
        "url", "final_url", "title", "meta_description", "publication_date_hint",
        "fetch_timestamp_utc", "cached", "http_status", "source_category",
        "authority_level", "search_query_found_for", "evidence_passages",
    ]
    with open(output_dir / "sources.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            row = r.__dict__
            row["search_query_found_for"] = " | ".join(r.search_query_found_for)
            row["evidence_passages"] = " || ".join(r.evidence_passages)
            writer.writerow(row)

    with open(output_dir / "crawl_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary.__dict__, f, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    script_dir = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(
        description="Respectful Chicago taxi shift research crawler (stdlib only)."
    )
    p.add_argument("--max-pages", type=int, default=80)
    p.add_argument("--delay", type=float, default=RATE_LIMIT_SAME_HOST)
    p.add_argument("--refresh", action="store_true", help="ignore cache")
    p.add_argument("--output-dir", default=str(script_dir / "output"))
    p.add_argument("--cache-dir", default=str(script_dir / "cache"))
    p.add_argument("--dry-run", action="store_true",
                   help="list queries and targets without network")
    p.add_argument("--self-test", action="store_true",
                   help="run offline checks and exit")
    return p


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _self_test():
    # classify()
    assert classify("https://www.cityofchicago.org/x", "") == ("city", "official")
    assert classify("https://data.cityofchicago.org/x", "") == ("portal", "data-provider")
    assert classify("https://www.amlegal.com/codes/chicago", "municipal code") == (
        "code", "regulatory")
    assert classify("https://www.ilga.gov/legislation", "") == ("state", "official")
    assert classify("https://research.uic.edu/shift-study", "Journal of Taxi Research") == (
        "academic", "secondary")
    assert classify("https://yellowcabchicago.com", "Yellow Cab company shifts") == (
        "company", "primary-industry")
    assert classify("https://www.reddit.com/r/chicago", "shift") == ("forum", "anecdotal")
    assert classify("https://www.nytimes.com/2020/taxi", "") == ("news", "tertiary")
    assert classify("https://someunknown.com/page", "Chicago stuff") == (
        "portal", "secondary")

    # normalize_url()
    assert normalize_url("HTTP://Example.COM:80/path?utm_source=x&a=1#frag") == (
        "http://example.com:80/path?a=1")
    assert normalize_url("https://x.com/?fbclid=abc") == "https://x.com/"

    # evidence extraction
    text = ("Drivers often work a 12 hour shift. "
            "The medallion is leased from the garage. "
            "Unrelated sentence about weather. "
            "BACP regulates operating hours in Chicago.")
    ev = extract_evidence(text, "", "")
    assert len(ev) == 3, ev
    assert any("12 hour shift" in e for e in ev)
    assert any("medallion" in e for e in ev)
    assert any("BACP" in e for e in ev)

    # cache_key determinism + stability
    assert cache_key("https://a.com/x") == cache_key("https://a.com/x")

    print("self-test OK")


def main():
    args = build_parser().parse_args()

    if args.self_test:
        _self_test()
        return

    if args.dry_run:
        print("Queries (dry-run):")
        for q in SEARCH_QUERIES:
            print(f"  - {q}")
        print("Would fetch up to %d pages each into output/." % MAX_RESULTS_PER_QUERY)
        return

    records, summary = run_crawl(args)
    print(f"Done: {summary.pages_fetched} fetched, {summary.pages_skipped_robots} skipped "
          f"(robots), {summary.pages_failed} failed, {len(records)} records.")


if __name__ == "__main__":
    main()
