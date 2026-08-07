SELECT
    unique_key,
    COUNT(*) AS duplicate_count
FROM `taxi-data-engineering-504801.bronze.raw_taxi_trips`
GROUP BY unique_key
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;