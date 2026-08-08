SELECT
  COUNTIF(unique_key IS NULL) AS unique_key_nulls,
  COUNTIF(taxi_id IS NULL) AS taxi_id_nulls,
  COUNTIF(trip_start_timestamp IS NULL) AS trip_start_nulls,
  COUNTIF(trip_end_timestamp IS NULL) AS trip_end_nulls,
  COUNTIF(trip_seconds IS NULL) AS trip_seconds_nulls,
  COUNTIF(trip_miles IS NULL) AS trip_miles_nulls,
  COUNTIF(fare IS NULL) AS fare_nulls,
  COUNTIF(tips IS NULL) AS tips_nulls,
  COUNTIF(trip_total IS NULL) AS trip_total_nulls,
  COUNTIF(payment_type IS NULL) AS payment_type_nulls,
  COUNTIF(company IS NULL) AS company_nulls
FROM `taxi-data-engineering-504910.bronze.raw_taxi_trips`;