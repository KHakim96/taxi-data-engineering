WITH lagged AS (
  SELECT
    taxi_id,
    trip_start_datetime,
    trip_end_datetime,
    LAG(trip_end_datetime) OVER (PARTITION BY taxi_id ORDER BY trip_start_datetime, trip_end_datetime) as prev_end
  FROM silver.stg_taxi_trips
  WHERE DATE(trip_start_datetime) >= '2023-01-01'
)
SELECT * FROM lagged
WHERE trip_start_datetime < prev_end
LIMIT 5;
