this is my personal note not readme:



1-fix timestamp region.to cehck as below:

SELECT
  trip_start_timestamp,
  DATETIME(trip_start_timestamp, "America/Chicago") AS chicago_time,
  EXTRACT(HOUR FROM trip_start_timestamp) AS utc_hour,
  EXTRACT(HOUR FROM DATETIME(trip_start_timestamp, "America/Chicago")) AS chicago_hour
FROM `taxi-data-engineering-504801.bronze.raw_taxi_trips`
LIMIT 10;

###Chicago = UTC - 6 hours   (Winter) CST = Central Standard Time
###Chicago = UTC - 5 hours   (Summer) CDT = Central Daylight Time

solution : DATETIME(trip_start_timestamp, "America/Chicago")

2-to check significant null comm area and pickup loc

SELECT
    COUNT(*) AS total_rows,
    COUNTIF(pickup_community_area IS NULL) AS null_rows,
    ROUND(
        100 * COUNTIF(pickup_community_area IS NULL) / COUNT(*),
        2
    ) AS null_percentage
FROM `taxi-data-engineering-504801.gold.pickup_geospatial`;

only 0.33 percent.no worries