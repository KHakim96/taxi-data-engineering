# Logic Notes

`trip_end_datetime_exact` · `fact_vehicle_activity_day`

---

**1-** So, this dataset uses 15-minute time intervals. and in some cases, a real trip could start at 5:50 and end at 6:05, but the recorded timestamps could become 06:00 → 06:00.

That's why i use `trip_seconds` to derive the end time in Silver:

```sql
DATETIME_ADD(
  trip_start_datetime,
  INTERVAL trip_seconds SECOND
) AS trip_end_datetime_exact
```

This way, I don't lose the actual trip duration just because the recorded timestamps are rounded.

**2-** In fact_vehicle_activity_day, this fact table is prepared solely for over workers mart question.the logic is:

Only select trusted activity from silver layer :

```sql
WHERE taxi_id IS NOT NULL
    AND trip_start_datetime IS NOT NULL
    AND trip_end_datetime_exact IS NOT NULL
    AND NOT duration_anomaly_flag (=TRUE)
```

Then for these trusted cte,then we assigned +1 for trip start and -1 for trip end.this is to handle the overlap issue (CTE: events,points,timeline,blocks)

Then that handled overlap data then is split over midnight because we want to use daily date as our metric for filtering.so the logic is as :

```
start_t = 2024-01-01 22:00:00
end_t   = 2024-01-02 01:00:00
```

if not split it cannot correctly attribute the 3 hours to individual calendar dates

so we split by midnight(end of the date day)

it become :

```
2024-01-01 = 2h
2024-01-02 = 1h
```

This allows us to correctly calculate/filter metrics by calendar day.

So some new function I just learn from this is:

`GREATEST()` → selects the later timestamp to determine when the daily slice starts.

`LEAST()` → selects the earlier timestamp to determine when the daily slice ends.

example as below:

```
Trip: Jan 1 22:00 → Jan 2 01:00

Jan 1:
GREATEST(22:00, 00:00) = 22:00  → slice starts
LEAST(01:00, 00:00)   = 00:00  → slice ends

Jan 2:
GREATEST(22:00, 00:00) = 00:00  → slice starts
LEAST(01:00, 00:00 next day) = 01:00 → slice ends
```

Then drop start time = the end time :

```sql
day_slices AS (
  SELECT * FROM sliced WHERE slice_start < slice_end
),
```

Then it summarizes the activity data into one record per taxi per day, then calculates the metrics needed for the final Day/Night flag (this is vehicle activity summary level = How long was the vehicle actually active?).

```sql
per_day AS (

  SELECT
    taxi_id,
    activity_date,

    SUM(DATETIME_DIFF(slice_end, slice_start, SECOND)) AS active_seconds,
    MIN(slice_start) AS first_active,
    MAX(slice_end) AS last_active,
    MAX(active_trips) AS max_concurrent_trips, -- find overlaps trip

    -- for day/night flag (day_night_flag query)
    SUM(
      GREATEST(
        0,
        DATETIME_DIFF(
          LEAST(slice_end, DATETIME_ADD(DATETIME(activity_date), INTERVAL 17 HOUR)),
          GREATEST(slice_start, DATETIME_ADD(DATETIME(activity_date), INTERVAL 5 HOUR)),
          SECOND
        )
      )
    ) AS daytime_seconds

  FROM day_slices
  GROUP BY taxi_id, activity_date
),
```

Then for trip activity summary per day level (How many trips did it make and how far did it travel?):

```sql
trips_per_day AS (
  SELECT
    taxi_id,
    trip_start_date AS activity_date,
    COUNT(*) AS trip_count,
    SUM(trip_miles) AS trip_miles,
    MAX(trip_seconds) / 60.0 AS longest_trip_minutes
  FROM trusted
  GROUP BY taxi_id, activity_date
),
```

Then count anomaly that has been flagged in silver (The first exclusion protects the metrics, this second CTE counts what was excluded):

```sql
excluded_per_day AS (
  SELECT
    taxi_id,
    DATE(trip_start_datetime) AS activity_date,
    COUNT(*) AS implausible_records_excluded
  FROM ${ref("stg_taxi_trips")}
  WHERE taxi_id IS NOT NULL
    AND trip_start_datetime IS NOT NULL
    AND duration_anomaly_flag
  GROUP BY taxi_id, activity_date
),
```

Then creates a complete list of taxi-days with activity, trips, or excluded records (use UNION DISTINCT):

```sql
all_taxi_days AS (
  SELECT taxi_id, activity_date FROM per_day
  UNION DISTINCT
  SELECT taxi_id, activity_date FROM trips_per_day
  UNION DISTINCT
  SELECT taxi_id, activity_date FROM excluded_per_day
)
```

Then select statement from our CTEs.
