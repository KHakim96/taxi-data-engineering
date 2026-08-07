# Bronze Layer Data Profiling Report

## Dataset

Source:
bigquery-public-data.chicago_taxi_trips.taxi_trips

Bronze Table:
bronze.raw_taxi_trips

Profiling Date:
2026-08-07

---

# Dataset Overview

| Metric | Value |
|--------|----------------|
| Total Rows | 213,111,447 |
| Unique Trip IDs | 211,655,459 |
| Duplicate Trip IDs | 1,455,988 |
| Maximum Duplicate Count | 2 |
| Date Range | 2013-01-01 to 2023-12-31 |

---

# Null Analysis

| Column | Null Count |
|---------|-----------:|
| unique_key | 0 |
| taxi_id | 0 |
| trip_start_timestamp | 0 |
| trip_end_timestamp | 18,547 |
| trip_seconds | 1,306,979 |
| trip_miles | 2,945 |
| fare | 21,191 |
| tips | 21,191 |
| trip_total | 21,191 |
| payment_type | 0 |
| company | 33,593,074 |

---

# Statistics

## Trip Seconds

Minimum : 0

Maximum : 86400

Average : 819.91

## Trip Miles

Minimum : 0

Maximum : 3460

Average : 3.49

## Fare

Minimum : 0

Maximum : 9999.99

Average : 13.82

## Tips

Minimum : 0

Maximum : 999.99

Average : 1.49

## Trip Total

Minimum : 0

Maximum : 9999.99

Average : 16.43

---

# Outlier Analysis

| Metric | Count |
|---------|------:|
| Zero Trip Seconds | 10,794,797 |
| Zero Trip Miles | 44,332,285 |
| Zero Fare | 289,160 |
| Zero Trip Total | 282,316 |
| Trips >100 Miles | 92,378 |
| Fare >1000 | 15,067 |
| Trip Total >1000 | 19,608 |
| Trips >4 Hours | 110,025 |

---

# Findings

- Dataset contains over 213 million records.
- Duplicate unique_key values exist and require investigation before deduplication.
- Missing company values account for approximately 15.8% of the dataset.
- Zero values exist for duration, distance and fare.
- Extremely large values exist for trip distance and fare.
- Business rules will be implemented in the Silver layer based on these findings.

---

# Silver Layer Objectives

- Investigate duplicate trip IDs.
- Handle NULL values appropriately.
- Standardize data types.
- Flag suspicious outliers.
- Preserve business-critical records whenever possible.
- Produce a clean, analytics-ready dataset.