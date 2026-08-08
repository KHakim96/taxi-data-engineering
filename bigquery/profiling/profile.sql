SELECT
    COUNT(*) AS total_rows,

    COUNT(DISTINCT unique_key) AS unique_trip_ids,

    MIN(trip_start_timestamp) AS first_trip,

    MAX(trip_start_timestamp) AS last_trip

FROM `taxi-data-engineering-504910.bronze.raw_taxi_trips`;