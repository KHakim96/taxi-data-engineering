SELECT 
  taxi_id, 
  DATE(trip_start_datetime) as date, 
  SUM(trip_seconds) as total_seconds, 
  SUM(trip_seconds)/3600 as total_hours, 
  COUNT(*) as trip_count
FROM silver.stg_taxi_trips
GROUP BY taxi_id, date
HAVING total_hours > 24
ORDER BY total_hours DESC
LIMIT 10;
