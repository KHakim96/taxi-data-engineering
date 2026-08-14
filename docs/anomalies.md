- **`total_rows`** — Total number of taxi trip records in Bronze. **213.1 million**.
- **`null_fare`** — Trips where `fare` is missing. **21,191**.
- **`null_trip_total`** — Trips where `trip_total` is missing. **21,191**.
- **`null_trip_miles`** — Trips where distance is missing. **2,945**.
- **`null_trip_seconds`** — Trips where duration is missing. **1.31 million**.

### Basic ranges

- **`min_fare`** — Lowest fare. **$0**.
- **`max_fare`** — Highest fare. **$9,999.99**.
- **`min_trip_total`** — Lowest total trip cost. **$0**.
- **`max_trip_total`** — Highest total trip cost. **$9,999.99**.
- **`min_trip_miles`** — Shortest recorded distance. **0 miles**.
- **`max_trip_miles`** — Longest recorded distance. **3,460 miles**.
- **`min_trip_seconds`** — Shortest recorded trip duration. **0 seconds**.
- **`max_trip_seconds`** — Longest recorded trip duration. **86,400 sec = 24 hours**.

### Negative-value checks

- **`negative_fare`** — Negative fares. **0**.
- **`negative_trip_total`** — Negative trip totals. **0**.
- **`negative_trip_miles`** — Negative distances. **0**.
- **`negative_trip_seconds`** — Negative durations. **0**.

So there are **no negative values** in these fields.

### Zero-value checks

- **`zero_mile_trips`** — Trips recorded with **0 miles**. **44.3 million**.
- **`zero_second_trips`** — Trips recorded with **0 seconds**. **10.8 million**.

These aren't automatically errors, but they're worth understanding.

### Fare percentiles

Percentiles tell you what a typical trip looks like.

- **`fare_p50`** — Median fare. **$8.25**. Half the trips are below this.
- **`fare_p90`** — 90% of trips are below **$34.75**.
- **`fare_p95`** — 95% are below **$42.75**.
- **`fare_p99`** — 99% are below **$53**.

This is important because the maximum is **$9,999.99**, while 99% are only up to about **$53**.

### Trip-total percentiles

- **`trip_total_p50`** — Median total paid. **$9.85**.
- **`trip_total_p90`** — 90% below **$41.25**.
- **`trip_total_p95`** — 95% below **$51.90**.
- **`trip_total_p99`** — 99% below **$69**.

### Distance percentiles

- **`miles_p50`** — Median trip = **1.2 miles**.
- **`miles_p90`** — 90% below **12.2 miles**.
- **`miles_p95`** — 95% below **17.3 miles**.
- **`miles_p99`** — 99% below **20.93 miles**.

### Duration percentiles

- **`seconds_p50`** — Median trip = **558 sec ≈ 9.3 min**.
- **`seconds_p90`** — 90% below **1,751 sec ≈ 29.2 min**.
- **`seconds_p95`** — 95% below **2,400 sec = 40 min**.
- **`seconds_p99`** — 99% below **3,720 sec = 62 min**.

### Fare per mile

This means:

> `fare ÷ trip_miles`

- **`fare_per_mile_p50`** — Median ≈ **$4.72/mile**.
- **`fare_per_mile_p90`** — 90% below **$12.50/mile**.
- **`fare_per_mile_p95`** — 95% below **$47.81/mile**.
- **`fare_per_mile_p99`** — 99% below **$97/mile**.
- **`max_fare_per_mile`** — Maximum = **$900,076/mile**.

That huge maximum indicates extreme ratios, especially when distance is tiny.

### Fare per minute

This means:

> `fare ÷ trip duration in minutes`

- **`fare_per_minute_p50`** — Median ≈ **$0.96/min**.
- **`fare_per_minute_p90`** — 90% below **$1.56/min**.
- **`fare_per_minute_p95`** — 95% below **$1.95/min**.
- **`fare_per_minute_p99`** — 99% below **$19.05/min**.
- **`max_fare_per_minute`** — Maximum = **$181,818/min**.

Again, huge extreme values exist.

### High-fare counts

- **`fare_ge_100`** — **174,622** trips have fare ≥ $100.
- **`fare_ge_500`** — **21,685** trips ≥ $500.
- **`fare_ge_1000`** — **15,114** trips ≥ $1,000.
- **`fare_ge_2000`** — **12,006** trips ≥ $2,000.
- **`fare_ge_5000`** — **6,765** trips ≥ $5,000.
- **`fare_ge_9000`** — **1,219** trips ≥ $9,000.

### High `trip_total` counts

Same idea, but using the final trip amount:

- **`total_ge_100`** — **529,103** trips ≥ $100.
- **`total_ge_500`** — **27,156** ≥ $500.
- **`total_ge_1000`** — **19,634** ≥ $1,000.
- **`total_ge_5000`** — **8,053** ≥ $5,000.
- **`total_ge_9000`** — **1,280** ≥ $9,000.

### Candidate anomaly patterns

- **`high_fare_short_trip`** — **11,585** trips where:
  - fare ≥ $1,000
  - distance < 1 mile
  - duration < 30 minutes

  This is your **strongest anomaly pattern**.

- **`extreme_fare_short_distance`** — **6,368** trips where:
  - fare ≥ $5,000
  - distance < 5 miles.

- **`extreme_fare_per_mile`** — **26,156** trips where fare/mile > $1,000.

  This is a **supporting signal**, not a rule I'd automatically use to remove data.

- **`extreme_fare_per_minute`** — **777,754** trips where fare/minute > $100.

  This is too broad by itself, so don't use it as an exclusion rule.

### Revenue impact

- **`total_fare`** — Total fare across all trips: **$2.944 billion**.
- **`fare_from_ge_1000`** — Fare coming from trips ≥ $1,000: **$67.52M**.
- **`fare_from_ge_5000`** — Fare from trips ≥ $5,000: **$47.47M**.
- **`fare_from_ge_9000`** — Fare from trips ≥ $9,000: **$11.07M**.

### Candidate anomaly population

- **`unique_candidate_anomalies`** — **34,042** trips matching your candidate anomaly rules.
- **`pct_fare_from_ge_1000`** — Trips ≥ $1,000 contribute **2.29% of total fare revenue**.
- **`pct_fare_from_ge_5000`** — Trips ≥ $5,000 contribute **1.61%** of total fare revenue.
- **`pct_fare_from_ge_9000`** — Trips ≥ $9,000 contribute **0.38%**.
- **`pct_candidate_anomalies`** — Candidate anomaly records are **0.016% of all trips**.

### The key story from this profiling

```text
213.1M trips
      ↓
99% of fares ≤ ~$53
      ↓
BUT max fare = $9,999.99
      ↓
Extreme tail exists
      ↓
Some extreme fares occur on very short trips
      ↓
Candidate anomaly rules identify 34,042 records
      ↓
Only ~0.016% of trips
      ↓
But extreme fares have meaningful revenue impact