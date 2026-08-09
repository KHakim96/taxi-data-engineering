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

3- total trip not tally

Data Quality Observation

During profiling, approximately 10.74% of trips had a trip_total that did not exactly equal fare + tips + tolls + extras. The discrepancy was concentrated in electronic payment methods (Credit Card, Mobile, Split, Way2ride), while Cash transactions reconciled exactly. Therefore, trip_total was treated as the authoritative revenue field throughout the Gold reporting layer.

to check query:
SELECT
    payment_type,
    COUNT(*) AS trip_count,
    ROUND(
      AVG(
        trip_total
        - (
            COALESCE(fare,0)
          + COALESCE(tips,0)
          + COALESCE(tolls,0)
          + COALESCE(extras,0)
        )
      ),
      2
    ) AS avg_difference
FROM `taxi-data-engineering-504801.bronze.raw_taxi_trips`
GROUP BY payment_type
ORDER BY trip_count DESC;