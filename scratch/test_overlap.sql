WITH trips AS (
  SELECT
    taxi_id,
    trip_start_datetime,
    trip_end_datetime,
    trip_seconds
  FROM silver.stg_taxi_trips
  WHERE taxi_id = '4ab7a7510c1ebcc9b2e3eaa7bdd6508dbea34da7986aca2d8478bb55d1eabf707cda06384ba05783521e50bd5c027c95e6feda8af5eb623f31aceb1c9cf7c6cf'
    AND DATE(trip_start_datetime) = '2023-10-27'
),
events AS (
  SELECT taxi_id, trip_start_datetime AS event_datetime, 1 AS delta FROM trips
  UNION ALL
  SELECT taxi_id, trip_end_datetime AS event_datetime, -1 AS delta FROM trips
),
event_points AS (
  SELECT taxi_id, event_datetime, SUM(delta) AS delta
  FROM events
  GROUP BY taxi_id, event_datetime
),
coverage AS (
  SELECT
    taxi_id,
    event_datetime,
    SUM(delta) OVER (PARTITION BY taxi_id ORDER BY event_datetime ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS active_trip_count,
    LEAD(event_datetime) OVER (PARTITION BY taxi_id ORDER BY event_datetime) AS next_event_datetime
  FROM event_points
),
active_intervals AS (
  SELECT
    taxi_id,
    event_datetime AS active_start_datetime,
    next_event_datetime AS active_end_datetime,
    DATETIME_DIFF(next_event_datetime, event_datetime, MINUTE) AS mins
  FROM coverage
  WHERE active_trip_count > 0
    AND next_event_datetime IS NOT NULL
    AND next_event_datetime > event_datetime
)
SELECT 'RAW_TRIP' as type, trip_start_datetime as start_time, trip_end_datetime as end_time, trip_seconds / 60 as mins
FROM trips
UNION ALL
SELECT 'MERGED_INTERVAL' as type, active_start_datetime as start_time, active_end_datetime as end_time, mins
FROM active_intervals
ORDER BY start_time, type DESC;
