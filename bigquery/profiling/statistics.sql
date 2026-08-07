SELECT
    MIN(trip_seconds) AS min_trip_seconds,
    MAX(trip_seconds) AS max_trip_seconds,
    AVG(trip_seconds) AS avg_trip_seconds,

    MIN(trip_miles) AS min_trip_miles,
    MAX(trip_miles) AS max_trip_miles,
    AVG(trip_miles) AS avg_trip_miles,

    MIN(fare) AS min_fare,
    MAX(fare) AS max_fare,
    AVG(fare) AS avg_fare,

    MIN(tips) AS min_tips,
    MAX(tips) AS max_tips,
    AVG(tips) AS avg_tips,

    MIN(trip_total) AS min_trip_total,
    MAX(trip_total) AS max_trip_total,
    AVG(trip_total) AS avg_trip_total

FROM `taxi-data-engineering-504801.bronze.raw_taxi_trips`;