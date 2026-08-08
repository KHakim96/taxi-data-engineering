SELECT
  COUNTIF(trip_seconds = 0) AS zero_trip_seconds,
  COUNTIF(trip_miles = 0) AS zero_trip_miles,
  COUNTIF(fare = 0) AS zero_fare,
  COUNTIF(trip_total = 0) AS zero_trip_total,

  COUNTIF(trip_miles > 100) AS trips_over_100_miles,
  COUNTIF(fare > 1000) AS fare_over_1000,
  COUNTIF(trip_total > 1000) AS total_over_1000,
  COUNTIF(trip_seconds > 14400) AS trips_over_4_hours

FROM `taxi-data-engineering-504910.bronze.raw_taxi_trips`;