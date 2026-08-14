# Chicago Taxi Shift Research

**Purpose:** determine a defensible real-world business rule for "taxi shifts" before touching `definitions/gold/shift_summary.sqlx`.
**Dataset context:** Chicago Taxi Trips 2013–2023 (`data.cityofchicago.org`, `wrvz-psew`).
**Method:** two independent research lanes (official/regulatory; industry/academic/historical), cross-checked, deduplicated into `sources_evidence.json` (28 sources). Raw re-crawl possible with `chicago_taxi_shift_research.py --self-test|--dry-run|<crawl>` in this directory.
**Research date:** 2026-08-15. No pipeline files were modified.

---

## 1. Executive conclusion

**Chicago has NO official, legally mandated taxi shift schedule — no fixed clock-time shift exists anywhere in Chicago law or BACP rules.** What Chicago *does* codify (MCC §9-112-230/-250, effective 2012, in force for the entire 2013–2023 dataset window) is a **duration structure**: leases are sold as "12 hour shift" / "24 hour shift" units, a chauffeur may not drive more than **12 consecutive hours** in any 24-hour period, and must rest **8 consecutive hours** before a 12-hour lease. The City's own Uniform Taxicab Lease Agreement leaves "Daily Shift: ___ Start Time (HH:MM)" **blank** — shift start times are negotiated per lease (Rule TX9.02 requires only that a weekly lease keep the *same* time all 7 days). Chicago survey evidence (UIC 2009: mean 13.05 h/shift, 74.5% ≥12 h; City-commissioned Nelson\Nygaard 2014 study of 10.6M 2013 trips: 40% of drivers work 11+ h/day) confirms ~12-hour shifts as the real work unit. The specific **05:00–17:00 / 17:00–05:00** windows are well documented only for **NYC** (lease boundaries 5 AM/5 PM; measured handoffs 4–5 PM), plus multi-city empirical studies showing changeovers cluster ~4–6 AM / ~4–6 PM. Therefore the most defensible analytical definition for this project is **NOT a claimed "Chicago driver shift"** but a **per-vehicle (`taxi_id`) trip-based sessionization** (a "vehicle operational shift" / operating block), anchored to the statutory 12 h / 8 h rest structure, with any day/night clock split (05:00–16:59 / 17:00–04:59) presented as a **labeled analytical assumption benchmarked to NYC lease convention**, not as a Chicago fact.

## 2. Official / regulatory evidence

Full verbatim passages, URLs, and dates: `sources_evidence.json` (sources #1–#10).

| # | Organization / instrument | URL | Title | Date | Relevant evidence (verbatim, abbreviated) | Proves | Does NOT prove |
|---|---|---|---|---|---|---|---|
| 1 | City of Chicago — MCC §9-112-230 | codelibrary.amlegal.com/.../0-0-0-2648494 | Tiered lease rate structure | enacted 1/18/2012; am. 2012, 2014, 2024 | "$74 per 12 hour shift… $101 per 24 hour shift… seven consecutive 12 hour shifts" | The regulatory lease unit IS the 12 h / 24 h shift (B/C/E) | Any clock-time boundary |
| 2 | City of Chicago — MCC §9-112-250 | codelibrary.amlegal.com/.../0-0-0-2648800 | Restriction on consecutive hours | 1/18/2012, in force ~Jul 2012 | "no chauffeur operates a taxicab for more than 12 consecutive hours within a 24 hour period"; "rest… 8 consecutive hours prior to the start of a 12 hour lease" | Legal max work period = 12 h; mandatory rest = 8 h (B); a 24 h lease is NOT 24 h of driving | Any schedule of start times |
| 3 | City of Chicago — MCC §9-112-010 | codelibrary.amlegal.com/.../0-0-0-2648318 | Definitions | current | No definition of "shift" anywhere | **Negative:** "shift" is not a defined legal term | — |
| 4 | BACP Medallion Holder Rules | chicago.gov/.../rulesandregulationsfortaxicabmedallionholders.pdf | Rules for Taxicab Medallion License Holders | eff. 4/17/2006, am. 2006–07 | "'12-hour lease' means a taxicab lease for a duration of 12 hours"; rate table 12-Hour $57.00 / 24-Hour $78.50 | 12/24 h lease structure **predates** 2012 reform (continuity into 2013) | Clock times |
| 5 | BACP Medallion Holder Rules (2015) | chicago.gov/.../amendtxmedlicholderrulrgsfinalsig9232015.pdf | Taxicab Medallion License Holder Rules | 9/23/2015 | "…two times for every twelve hour shift worked" | "Twelve hour shift" remains the standard unit mid-window | Clock times |
| 6 | BACP Taxi Industry Notice 12-004 | chicago.gov/.../taxiindustrynotice12-004newtaxipublicvehicleord.pdf | New Taxicab and Public Vehicle Ordinances | 12/14/2011 | "no more than 12 consecutive hours of driving each day… in line with federal motor vehicle safety laws" | 12 h cap is a driver-safety hours-of-service limit (B) | A fixed schedule |
| 7 | Chicago Data Portal | data.cityofchicago.org/.../wrvz-psew (+ Socrata metadata API) | Taxi Trips (2013–2023) metadata | upd. 2024 | "Taxi ID is consistent for any given taxi **medallion** number"; "times are rounded to the nearest **15 minutes**"; `taxi_id` = "A unique identifier for the taxi" (~9,806 IDs, ~211.6M rows) | `taxi_id` = **vehicle** identifier (C); 15-min rounding caps boundary precision | Any driver- or shift-level semantics |
| 8 | BACP Uniform Taxicab Lease Agreement + Rule TX9.02 | chicago.gov/.../publicchauffeur.html (mirror: abcdocz.com/doc/39116) | Uniform Taxicab Lease Agreement (eff. 1/1/2020) | 2020 (structure since 2012) | "Daily Shift: ___ Start Time (HH:MM)" (blank); "TX9.02 – 12 hour weekly leases must be for the identical shift time for all 7 consecutive days" | **Strongest evidence of no city-mandated changeover**: clock time is contractual, per lease | What times operators actually chose |
| 9 | BACP Public Chauffeur Rules | chicago.gov/.../BACP-Public-Chauffeur-Rules-3-1-25-Signed.pdf | Public Chauffeur Rules (2016 / 2025 eds.) | 2016; 2025 | No hours-of-service or shift-schedule content | **Negative:** licensing rules impose no shift mandate | — |
| 10 | State of Illinois (ICC) | icc.illinois.gov | Jurisdiction check | current | ICC regulates livery/limo, not Chicago taxicabs (home rule) | **Negative:** no state shift statute exists; MCC Title 9 governs | — |

## 3. Industry evidence

Full detail: `sources_evidence.json` (#11–#28). Strongest items:

| # | Source | Date | Evidence (verbatim, abbreviated) | Proves | Does NOT prove |
|---|---|---|---|---|---|
| 11 | Frechette, Lizzeri & Salz (AER 2019) — **NYC comparative** | 2019 (data 2009–13) | "most day shifts start around 5AM and most night shifts around 5PM"; "shift changes occur from 5AM to 7AM and 3PM to 5PM" | NYC 5/5 lease boundary + 4–5 PM measured handoff (B/C/E) | Anything about Chicago |
| 12 | Farber (QJE 2015 / NBER w20604) — **NYC** | 2015 | "usually a 12-hour shift"; day starts 4–9:59 AM (44.5%), night 2–7:59 PM (42.4%) | 12 h two-shift structure + empirical day/night start-hour segmentation (E) | Chicago applicability |
| 13 | Schmidt (JMP) — **NYC** | 2019 | "day shift (5 AM to 5 PM) or the night shift (5 PM to 5 AM)" | Most explicit 05:00–17:00/17:00–05:00 statement found — **NYC only** | Chicago applicability |
| 14 | Buchholz, Shum & Xu — **NYC** | data 2012–13 | "return cars… by 4-5pm for the evening shift… by 4-5am" | Measured handoff windows 4–5 PM / 4–5 AM (C) | Chicago applicability |
| 15 | NYT — **NYC** | 1/12/2011 | "From 4 to 5 p.m., the traditional hour for cabs to change shifts… active taxicabs falls by nearly 20 percent"; "two drivers a day, each working a 12-hour shift" | Documented "witching hour"; rationale (each shift gets a rush hour) | Chicago applicability |
| 16 | Bruno, Schneidman & Hewitt (UIC) — **CHICAGO** | 2009 (n=711) | "The average shift is more than 13 hours… 74.54 percent working 12 hours or more per shift" | Chicago shift durations cluster ≥12 h (B) | Changeover times |
| 17 | Nelson\Nygaard Taxi Fare Rate Study — **CHICAGO, city-commissioned** | Aug 2014 (data Jan–Aug 2013) | 10.6M trips from 3,900 taxis; "40 percent of drivers… work 11 or more hours a day"; 20% part-time ≤7 h | Large 11+ h cohorts confirmed **inside the dataset window**, from the same data lineage (B/E) | Changeover times |
| 18 | CBS Chicago — **CHICAGO** | 7/2/2012 | "no more than 12 hours a day, excluding breaks"; "8 hours a day, just to break even" | 12 h cap took effect 2012 (A/B). "8 hours" = break-even economics, **not** a shift structure | An 8-hour shift schedule |
| 19–21 | Tribune 1990; Checker Taxi v. NPWU (N.D. Ill. 1986); Luedke ethnography 2010 — **CHICAGO** | 1990; 1986; 2010 | "12-hour, 24-hour or weekly periods"; "day, night or twenty-four hour basis"; "12 hours, 24 hours, a week" | Chicago day/night/24 h lease triad is decades old (B/C) | Changeover times |
| 23–24 | Wuhan (IJGI 2020) & Fuzhou (2021) trace-data studies — **method comparative** | 2020; 2021 | shift-change peaks "1:00–4:00 a.m. and 4:00–5:00 p.m."; "4:00–6:00… and 16:00–18:00" | Empirical changeover clustering ~4–6 AM / ~4–6 PM across cities; shift detection **from trip data** is established methodology (E) | Chicago timing |
| 28 | AutoMarketplace blog — **NYC, supplementary only** | 2025 | "abandoned traditional day-night shift splits due to lost trips during driver handoffs" | Late-era (2019–2023) erosion of two-shift discipline is *possible* — anecdotal, lowest authority | Chicago practice |

## 4. Shift-window evidence

| Proposed shift rule | Evidence | Authority | Confidence |
|---|---|---|---|
| 05:00–17:00 / 17:00–05:00 | Schmidt (#13) explicit NYC lease window; Frechette (#11) "start around 5AM/5PM"; Farber (#12) day starts 4–9:59 AM. **No Chicago source.** | Academic (peer-reviewed), but **NYC-comparative only** | **Medium** as industry benchmark; **Low** as a Chicago-specific fact |
| 06:00–18:00 / 18:00–06:00 | Single anecdotal 1979 NYC driver memoir (excluded from source list as below evidence threshold) | Anecdotal | **Low** — not defensible |
| 8-hour shifts | None as a *shift structure*. "8 hours" appears only as (a) statutory **rest** period (MCC §9-112-250(b)) and (b) break-even economics (CBS #18) | Regulatory (rest, not shift) | **Low** as a shift rule — would misstate the statute |
| 12-hour shifts | MCC §9-112-230/-250 (#1, #2); BACP rules 2006/2015 (#4, #5); Uniform Lease Agreement (#8); Bruno 13.05 h mean (#16); Nelson\Nygaard 40% ≥11 h (#17); Luedke (#21); comparative: Farber, Camerer, Schaller | **Legal/regulatory (Chicago) + academic (Chicago) + academic (NYC)** | **High** — the only structure with direct Chicago support |
| No fixed window (negotiated per lease) | Lease form blank "Start Time (HH:MM)" + Rule TX9.02 (#8); MCC §9-112-010 defines no "shift" (#3); chauffeur rules silent (#9) | **Regulatory (Chicago), negative finding** | **High** |

## 5. Legal vs operational vs analytical

| Concept | Evidence | Applies to | Can we use it in this project? |
|---|---|---|---|
| Legal operating hours | No operating-hours restriction in MCC 9-112; 24/7 service implied by 12 h + 12 h lease stacking (#1, #2) | Taxis as vehicles | Only as context — says nothing about shifts |
| Driver work shift | 12 h max + 8 h rest (§9-112-250); ~12–13 h actual (Bruno #16; Nelson\Nygaard #17) | Individual chauffeurs | **No** — no driver ID in dataset (see §10) |
| Vehicle operational shift | 12/24 h lease structure (#1, #4, #8); two drivers per vehicle per day (NYC #11, #15; Chicago day/night leases #19, #20) | Medallion/vehicle | **Yes, as inferred construct** — sessionize per `taxi_id` |
| Day/night operational window | NYC 5 AM/5 PM leases (#11, #13); handoffs 4–5 PM / 4–6 AM (#11, #14, #15, #23, #24); Chicago: time is contractual (#8) | Lease schedules | **Only as a labeled analytical assumption** for a day/night flag |
| Analytical shift | Wuhan/Fuzhou methodology: detect shift changes from trip data (#23, #24) | The dataset itself | **Yes — recommended**: this is our definition to make and defend |

## 6. Historical applicability

| Period | Regime | Applies to dataset? |
|---|---|---|
| pre-2012 | 12/24 h leases already standard (BACP 2006 rules #4; Tribune 1990 #19; Checker 1986 #20) — but **no driving-hours cap** | Baseline only (pre-window) |
| Jul 2012 – 2023 | MCC §9-112-230/-250 in force: 12 h consecutive cap + 8 h rest + tiered lease caps | **Covers the entire 2013–2023 window** — the core rule never changed |
| Jan 25, 2015 | Lease rate caps **reduced** (§9-112-230 amendment) | Economics only; no shift-structure change |
| Sep–Dec 2015 | Rules reissued (#5); lease "chaining" prohibition | No shift-structure change |
| 2018 | Industry relief/reform laws (#26) | No shift-structure change |
| 2020 | Uniform Lease Agreement standardizes 12/24 h forms (#8) | Structure continues |
| 2019–2023 (caveat) | Possible erosion of two-shift discipline under TNC pressure — **anecdotal NYC evidence only** (#28); no Chicago documentation found | Flag as uncertainty for late-window years |

**Do not apply any 2024–2026 amendments as if they described 2013:** nothing in them changed shift structure anyway, but cite the 2012 enactment for dataset-era claims.

## 7. Recommended business rule

**Option D + E (combined, and this is one rule): trip-based sessionization per vehicle, framed as an analytical "operational shift" — not a claimed driver shift.**

1. **Sessionize on `taxi_id`** using the existing gap rule (new block when gap from previous trip end ≥ 8 h). The 8-hour threshold is now *evidence-anchored*: MCC §9-112-250(b) mandates **8 consecutive hours of rest** before a 12-hour lease, so an 8 h gap in a vehicle's trip stream is the statutory signature of a lease-to-lease boundary — the most Chicago-specific threshold available.
2. **Frame and name it honestly**: output measures a **vehicle operating block** ("Vehicle Operational Shift"), because `taxi_id` = medallion (Data Portal metadata, #7). A ~24 h block with a short mid-day gap is most consistent with **two 12-hour drivers sharing the vehicle** (the dominant lease structure), not one overworker — the current `Overworker` label over-claims.
3. **Optional secondary dimension — day/night flag**: `05:00–16:59 = Day, 17:00–04:59 = Night` on `trip_hour`, with a model comment stating it is an **analytical assumption** benchmarked to NYC lease convention (#11, #13) and multi-city changeover clustering (#14, #15, #23, #24) — *not* a documented Chicago schedule. A `04:00–15:59 / 16:00–03:59` sensitivity variant is defensible if the 4–5 PM "witching hour" matters to the analysis.

Rejected: Option A/B/C as *primary* rules (fixed windows have no Chicago legal basis; §8 of the lease form explicitly leaves times contractual); the 8-hour option misreads rest as shift.

## 8. Confidence level

- **HIGH** — that Chicago has no official clock-time shift schedule (code text + blank lease form + TX9.02 + two negative findings, independently converged by both research lanes).
- **HIGH** — that the 12-hour shift / 8-hour-rest structure is the real Chicago operating unit (statute + two Chicago studies + decades of lease practice).
- **MEDIUM** — the 05:00/17:00 day/night *label* (strong NYC benchmark, zero direct Chicago timing evidence; empirical changeover windows are broad, 4–6 AM / 4–6 PM).
- **LOW** — any claim that a fixed window is "the Chicago taxi shift."

## 9. Interview-safe explanation

> "I researched this rather than assuming it: Chicago regulates taxi *durations*, not schedules — the Municipal Code leases medallions in 12-hour shifts and caps driving at 12 consecutive hours with 8 hours of rest, but the City's own lease form leaves the shift start time blank, so there's no official changeover hour. Since the dataset's `taxi_id` is a medallion-level vehicle identifier with no driver field, true driver shifts can't be reconstructed. So I defined an analytical *vehicle operational shift*: trips grouped per taxi with an 8-hour inactivity gap as the block boundary, which deliberately mirrors the statutory 8-hour rest period, and I label any day/night split as an assumption benchmarked to the documented NYC 5 AM/5 PM lease convention — not as a Chicago fact."

## 10. Dataset-specific analysis

Inspected: `definitions/silver/stg_taxi_trips.sqlx`, `definitions/gold/shift_summary.sqlx`.

| Field (silver) | Present | Supports |
|---|---|---|
| `taxi_id` | yes | Vehicle proxy for sessionization — **not** a driver ID |
| `trip_start_datetime` / `trip_end_datetime` (America/Chicago local) | yes (lines 24–25) | Gap computation and any fixed-window labeling; local time is sufficient |
| `trip_hour` (`EXTRACT(HOUR FROM trip_start_datetime)`) | yes (line 47) | Direct day/night flag if adopted |
| `trip_seconds`, `trip_date`, `trip_year` | yes | Duration sanity, partitioning |
| Driver identifier | **absent** | **Driver-level shift cannot be reliably reconstructed from this dataset.** |

Constraints found: Data Portal rounds timestamps to **15 minutes** (#7) — negligible for 12 h windows, minor for gap thresholds; the current gold model already implements exactly the Option-D mechanics (8 h gap = `gap_minutes >= 480`), so the recommendation is a *reframing + relabeling + optional flag*, not new logic. One mechanical note: `DATETIME_DIFF` on local wall-clock times behaves oddly across DST transitions (2 h/0 h nights) — acceptable, worth a comment.

---

## FINAL ANSWER

**Does Chicago actually have a standard taxi shift schedule?**

**NO** — not a clock-time schedule. It has a legally codified *duration* structure: 12-hour shift leases (24-hour option) with a 12-consecutive-hour driving cap and 8-hour mandatory rest (MCC §9-112-230/-250, 2012–present). Shift start times are contractual (blank on the City's own lease form).

**Best-supported shift rule:**

Per-`taxi_id` trip sessionization with a **≥ 8-hour inactivity gap** as the block boundary (the statutory rest period), interpreted as a **Vehicle Operational Shift** — optionally with a Day (05:00–16:59) / Night (17:00–04:59) *analytical* flag.

**Recommended terminology:**

**"Vehicle Operational Shift"** (analytical construct). Never "Driver Shift." Use "day/night window" only as a labeled assumption.

**Can this dataset measure true driver shifts?**

**NO** — `taxi_id` is a medallion/vehicle identifier (Data Portal metadata); two drivers commonly share one vehicle across 12-hour leases.

**Recommended project-level analytical definition:**

A Vehicle Operational Shift = a maximal sequence of trips by one `taxi_id` where consecutive trips are separated by < 8 hours (gap measured `trip_end_datetime → next trip_start_datetime`, Chicago local time); blocks > 24 h are flagged as data/multi-driver anomalies, 12–24 h blocks labeled "extended/multi-driver (ambiguous)".

**Confidence:**

HIGH on the negative finding and the 12 h/8 h structure; MEDIUM on the 05:00/17:00 day-night label.

**Biggest evidence supporting the decision:**

1. MCC §9-112-250 (2012, in force for the whole dataset window): "no chauffeur operates a taxicab for more than 12 consecutive hours within a 24 hour period… rest… 8 consecutive hours prior to the start of a 12 hour lease."
2. City of Chicago Uniform Taxicab Lease Agreement + Rule TX9.02: shift start time is a **blank contractual field** — no city-mandated changeover exists.
3. Chicago studies (UIC 2009: mean 13.05 h/shift; Nelson\Nygaard 2014 on 10.6 M 2013 trips: 40% of drivers ≥ 11 h/day) + NYC comparative record (5 AM/5 PM leases, 4–5 PM handoffs) confirm ~12-hour two-shift operations without fixing a Chicago clock time.

**Biggest limitation:**

No Chicago source documents an actual changeover clock time, so any fixed day/night window applied to this dataset remains an assumption imported from NYC practice and multi-city empirical clustering.

**Recommended next modification to `shift_summary.sqlx`** (described only — DO NOT implement yet):

1. Reword the model `description`: replace "Reconstructs driver shifts…" with "Reconstructs **vehicle operational shifts** (analytical construct): trips per `taxi_id` separated by < 8 h. The 8-hour gap mirrors the statutory 8-hour rest before a 12-hour lease (MCC §9-112-250, 2012). Driver-level shifts cannot be reconstructed (no driver identifier; `taxi_id` = medallion)."
2. Add a comment at the `gap_minutes >= 480` line citing MCC §9-112-250(b) as the threshold's justification.
3. Reclassify `shift_classification`: `< 12 h → 'Single-Driver Block (typical)'`; `12–24 h → 'Extended / Multi-Driver (ambiguous)'` (a 12+12 h two-driver lease is at least as likely as overwork); `> 24 h → 'Shared Vehicle Fleet / Anomaly'`.
4. Optional: add `shift_start_hour` and `day_night_flag` (`05:00–16:59 = 'Day', 17:00–04:59 = 'Night'`) with a comment marking it an analytical assumption benchmarked to NYC lease convention, not a Chicago mandate.
