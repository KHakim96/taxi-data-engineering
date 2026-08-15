# Business Rules — Vehicle-Day Utilization

Approved: 2026-08-16 (forensic review of the former shift/overworker logic).
Applies to: `silver.stg_taxi_trips` → `gold.vehicle_activity_day` → `gold.overworkers`.

---

## 1. What we are measuring

**Vehicle-Day Utilization**: how much time a taxi *vehicle* is actively operating,
per vehicle per Chicago-local calendar day, and whether that active time exceeds
what **one legal driver** would be permitted to drive.

This is a **vehicle-level utilization and capacity metric**. It is **NOT**
driver overtime, driver hours, or driver behavior.

## 2. Entity and grain

- **Entity:** vehicle (medallion). `taxi_id` is a medallion-level identifier per
  Chicago Data Portal metadata ("Taxi ID is consistent for any given taxi
  medallion number"). The dataset contains **no driver identifier**.
- **Grain:** one row per `taxi_id` × America/Chicago calendar `activity_date`.

## 3. Active-time calculation

1. For each trusted trip, build the interval
   `trip_start_datetime → trip_end_datetime_exact`, where
   `trip_end_datetime_exact = DATETIME_ADD(trip_start_datetime, INTERVAL trip_seconds SECOND)`
   in Chicago-local wall-clock time. The exact reconstruction is used because
   source timestamps are rounded to the nearest 15 minutes.
2. Merge overlapping intervals with a sweep-line (+1 at start, −1 at exact end,
   collapse identical timestamps, running sum, keep periods where the
   concurrent-trip count > 0). The result is a set of **non-overlapping
   activity intervals** — the interval UNION.
3. Clip each merged interval at local-midnight boundaries so each calendar day
   owns only its own activity.
4. `active_minutes` = sum of the disjoint clipped interval durations.
   **`SUM(trip_seconds)` is never used for active time** — it double-counts
   overlapping trips and inflated durations.

### Overlap handling
Overlaps (partial, nested, duplicate timestamps, same-end clusters) are merged
into the union — counted once. They are recording artifacts, not simultaneous
driving. `max_concurrent_trips` records the deepest overlap for diagnostics.

### Gap handling
Gaps between trips are **not** active time. No sessionization is applied for
the primary metric; the former 8-hour-gap session boundary exists only as a
historical concept and is not used.

### Long-trip handling
Plausible long trips (including >12h at reasonable speed) are retained and
count in full. Only **duration-implausible** records are excluded (below).

## 4. Plausibility filtering (Silver flags, Gold exclusion)

Flagged in Silver — never deleted:

| reason | rule | treatment |
|---|---|---|
| `IMPLAUSIBLE_SPEED` | `trip_seconds >= 7200 AND trip_miles / (trip_seconds/3600) < 3` (≥2h at <3 mph) | Excluded from trusted Gold utilization/fact; count surfaced in `implausible_records_excluded` |
| `ZERO_DURATION` | `trip_seconds = 0` | Informational; contributes no interval |
| `LONG_TRIP` | `trip_seconds > 43200` | Informational; retained and counted if plausible |

Evidence: 98.9% of >12h records are <3 mph (median 1.3 miles) — meter/device
artifacts. The previous Silver hard delete (`trip_seconds <= 43200`) was
removed; it destroyed 46,843 records including plausible long trips.

## 5. Capacity classification

- `active_hours <= 12.0` → **"Within single-driver capacity"**
- `active_hours > 12.0` → **"Exceeds single-driver legal capacity (multi-driver and/or overwork — indeterminate)"**

The 12-hour threshold is the Chicago chauffeur limit (MCC §9-112-250: no
chauffeur operates a taxicab more than 12 consecutive hours in a 24-hour
period), used as the **capacity ceiling of one legal driver** — not as proof
of any individual's hours.

## 6. Optional day/night flag

`day_night_flag` (Day = majority of active time in 05:00–16:59; else Night) is
an **ANALYTICAL ASSUMPTION** benchmarked to NYC lease convention and
multi-city changeover clustering. Chicago lease start times are contractual
(blank on the City's uniform lease form); no Chicago changeover hour exists.

## 7. Limitations (must accompany any use of this metric)

1. **No driver attribution.** Multiple drivers routinely share one medallion
   (12h/24h lease structure, MCC §9-112-230). A >12h vehicle-day is
   indistinguishable between one overworking driver and two leased shifts.
2. **15-minute source rounding.** Trip timestamps are rounded to the nearest
   15 minutes (±7.5 min per boundary); `trip_end_datetime_exact` inherits that
   rounding from `trip_start_datetime`.
3. **Unreported trips.** The City states "not all trips are reported but most
   are" — active time is a floor, not a ceiling.
4. **DST.** Chicago-local wall-clock days are 23h (spring) or 25h (fall);
   `active_minutes` remains bounded by actual interval time.
5. **Vehicle time ≥ driver time.** Any driver-level reading of this metric is
   invalid by construction.

## 8. Terminology

Use: Vehicle-Day Utilization, Active Vehicle Hours, Within Single-Driver
Capacity, Exceeds Single-Driver Capacity, Vehicle Operational Block (secondary
concept only).

Never use: Driver Shift, Driver Overwork, Overworker, Overtime.
