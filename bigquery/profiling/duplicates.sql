-- SELECT
--     unique_key,
--     COUNT(*) AS duplicate_count
-- FROM `taxi-data-engineering-504801.bronze.raw_taxi_trips`
-- GROUP BY unique_key
-- HAVING COUNT(*) > 1
-- ORDER BY duplicate_count DESC;

WITH duplicate_keys AS (
  SELECT unique_key
  FROM `taxi-data-engineering-504801.bronze.raw_taxi_trips`
  GROUP BY unique_key
  HAVING COUNT(*) > 1
)

SELECT *
FROM `taxi-data-engineering-504801.bronze.raw_taxi_trips`
WHERE unique_key IN (
  SELECT unique_key
  FROM duplicate_keys
)
ORDER BY unique_key;