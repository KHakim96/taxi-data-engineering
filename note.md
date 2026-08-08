this is my personal note not readme:

first issue:

fix timestamp region.to cehck as below:
SELECT
  trip_start_timestamp,
  DATETIME(trip_start_timestamp, "America/Chicago") AS chicago_time,
  EXTRACT(HOUR FROM trip_start_timestamp) AS utc_hour,
  EXTRACT(HOUR FROM DATETIME(trip_start_timestamp, "America/Chicago")) AS chicago_hour
FROM `taxi-data-engineering-504910.bronze.raw_taxi_trips`
LIMIT 10;