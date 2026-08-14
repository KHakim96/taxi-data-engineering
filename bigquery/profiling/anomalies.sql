WITH base AS (
  SELECT
    unique_key,
    fare,
    trip_total,
    trip_miles,
    trip_seconds,

    SAFE_DIVIDE(fare, NULLIF(trip_miles, 0)) AS fare_per_mile,
    SAFE_DIVIDE(fare, NULLIF(trip_seconds / 60.0, 0)) AS fare_per_minute
  FROM `taxi-data-engineering-504801.bronze.raw_taxi_trips`
),

profile AS (
  SELECT
    COUNT(*) AS total_rows,

    -- =========================================================
    -- NULL / COMPLETENESS
    -- =========================================================
    COUNTIF(fare IS NULL) AS null_fare,
    COUNTIF(trip_total IS NULL) AS null_trip_total,
    COUNTIF(trip_miles IS NULL) AS null_trip_miles,
    COUNTIF(trip_seconds IS NULL) AS null_trip_seconds,

    -- =========================================================
    -- BASIC RANGE / VALIDITY
    -- =========================================================
    MIN(fare) AS min_fare,
    MAX(fare) AS max_fare,

    MIN(trip_total) AS min_trip_total,
    MAX(trip_total) AS max_trip_total,

    MIN(trip_miles) AS min_trip_miles,
    MAX(trip_miles) AS max_trip_miles,

    MIN(trip_seconds) AS min_trip_seconds,
    MAX(trip_seconds) AS max_trip_seconds,

    COUNTIF(fare < 0) AS negative_fare,
    COUNTIF(trip_total < 0) AS negative_trip_total,
    COUNTIF(trip_miles < 0) AS negative_trip_miles,
    COUNTIF(trip_seconds < 0) AS negative_trip_seconds,

    COUNTIF(trip_miles = 0) AS zero_mile_trips,
    COUNTIF(trip_seconds = 0) AS zero_second_trips,

    -- =========================================================
    -- FARE DISTRIBUTION
    -- =========================================================
    APPROX_QUANTILES(fare, 100)[OFFSET(50)] AS fare_p50,
    APPROX_QUANTILES(fare, 100)[OFFSET(90)] AS fare_p90,
    APPROX_QUANTILES(fare, 100)[OFFSET(95)] AS fare_p95,
    APPROX_QUANTILES(fare, 100)[OFFSET(99)] AS fare_p99,

    APPROX_QUANTILES(trip_total, 100)[OFFSET(50)] AS trip_total_p50,
    APPROX_QUANTILES(trip_total, 100)[OFFSET(90)] AS trip_total_p90,
    APPROX_QUANTILES(trip_total, 100)[OFFSET(95)] AS trip_total_p95,
    APPROX_QUANTILES(trip_total, 100)[OFFSET(99)] AS trip_total_p99,

    APPROX_QUANTILES(trip_miles, 100)[OFFSET(50)] AS miles_p50,
    APPROX_QUANTILES(trip_miles, 100)[OFFSET(90)] AS miles_p90,
    APPROX_QUANTILES(trip_miles, 100)[OFFSET(95)] AS miles_p95,
    APPROX_QUANTILES(trip_miles, 100)[OFFSET(99)] AS miles_p99,

    APPROX_QUANTILES(trip_seconds, 100)[OFFSET(50)] AS seconds_p50,
    APPROX_QUANTILES(trip_seconds, 100)[OFFSET(90)] AS seconds_p90,
    APPROX_QUANTILES(trip_seconds, 100)[OFFSET(95)] AS seconds_p95,
    APPROX_QUANTILES(trip_seconds, 100)[OFFSET(99)] AS seconds_p99,

    -- =========================================================
    -- FARE / DISTANCE + FARE / TIME
    -- =========================================================
    APPROX_QUANTILES(fare_per_mile, 100)[OFFSET(50)] AS fare_per_mile_p50,
    APPROX_QUANTILES(fare_per_mile, 100)[OFFSET(90)] AS fare_per_mile_p90,
    APPROX_QUANTILES(fare_per_mile, 100)[OFFSET(95)] AS fare_per_mile_p95,
    APPROX_QUANTILES(fare_per_mile, 100)[OFFSET(99)] AS fare_per_mile_p99,

    APPROX_QUANTILES(fare_per_minute, 100)[OFFSET(50)] AS fare_per_minute_p50,
    APPROX_QUANTILES(fare_per_minute, 100)[OFFSET(90)] AS fare_per_minute_p90,
    APPROX_QUANTILES(fare_per_minute, 100)[OFFSET(95)] AS fare_per_minute_p95,
    APPROX_QUANTILES(fare_per_minute, 100)[OFFSET(99)] AS fare_per_minute_p99,

    MAX(fare_per_mile) AS max_fare_per_mile,
    MAX(fare_per_minute) AS max_fare_per_minute,

    -- =========================================================
    -- FARE THRESHOLD COUNTS
    -- =========================================================
    COUNTIF(fare >= 100) AS fare_ge_100,
    COUNTIF(fare >= 500) AS fare_ge_500,
    COUNTIF(fare >= 1000) AS fare_ge_1000,
    COUNTIF(fare >= 2000) AS fare_ge_2000,
    COUNTIF(fare >= 5000) AS fare_ge_5000,
    COUNTIF(fare >= 9000) AS fare_ge_9000,

    -- =========================================================
    -- TRIP TOTAL THRESHOLD COUNTS
    -- =========================================================
    COUNTIF(trip_total >= 100) AS total_ge_100,
    COUNTIF(trip_total >= 500) AS total_ge_500,
    COUNTIF(trip_total >= 1000) AS total_ge_1000,
    COUNTIF(trip_total >= 5000) AS total_ge_5000,
    COUNTIF(trip_total >= 9000) AS total_ge_9000,

    -- =========================================================
    -- PHYSICAL PLAUSIBILITY
    -- =========================================================
    COUNTIF(fare >= 1000 AND trip_miles < 1 AND trip_seconds < 1800)
      AS high_fare_short_trip,

    COUNTIF(fare >= 5000 AND trip_miles < 5)
      AS extreme_fare_short_distance,

    COUNTIF(
      fare > 0
      AND trip_miles > 0
      AND SAFE_DIVIDE(fare, trip_miles) > 1000
    ) AS extreme_fare_per_mile,

    COUNTIF(
      fare > 0
      AND trip_seconds > 0
      AND SAFE_DIVIDE(fare, trip_seconds / 60.0) > 100
    ) AS extreme_fare_per_minute,

    -- =========================================================
    -- REVENUE IMPACT
    -- =========================================================
    SUM(fare) AS total_fare,

    SUM(IF(fare >= 1000, fare, 0))
      AS fare_from_ge_1000,

    SUM(IF(fare >= 5000, fare, 0))
      AS fare_from_ge_5000,

    SUM(IF(fare >= 9000, fare, 0))
      AS fare_from_ge_9000,

    -- =========================================================
    -- CANDIDATE RULES — INDEPENDENT FLAGS
    -- IMPORTANT: these are not yet exclusions.
    -- They quantify the candidate anomaly population.
    -- =========================================================
    COUNTIF(
      fare IS NULL
      OR (
        fare >= 1000
        AND trip_miles < 1
        AND trip_seconds < 1800
      )
      OR (
        fare >= 5000
        AND trip_miles < 5
      )
    ) AS unique_candidate_anomalies

  FROM base
)

SELECT
  *,
  SAFE_DIVIDE(fare_from_ge_1000, total_fare) * 100
    AS pct_fare_from_ge_1000,

  SAFE_DIVIDE(fare_from_ge_5000, total_fare) * 100
    AS pct_fare_from_ge_5000,

  SAFE_DIVIDE(fare_from_ge_9000, total_fare) * 100
    AS pct_fare_from_ge_9000,

  SAFE_DIVIDE(unique_candidate_anomalies, total_rows) * 100
    AS pct_candidate_anomalies

FROM profile; 