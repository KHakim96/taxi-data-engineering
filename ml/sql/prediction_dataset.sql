WITH base AS (

SELECT
    *,
    LAG(total_trips, 1) OVER (ORDER BY trip_date) AS lag_1,
    LAG(total_trips, 7) OVER (ORDER BY trip_date) AS lag_7,

    AVG(total_trips) OVER (
        ORDER BY trip_date
        ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
    ) AS rolling_7d

FROM `taxi-data-engineering-504910.gold.fact_daily_demand`

)

SELECT

trip_date,

temperature_max,
temperature_min,
temperature_mean,

precipitation_mm,
snowfall_cm,
wind_speed_kmh,

CAST(is_raining AS INT64) AS is_raining,
CAST(is_snowing AS INT64) AS is_snowing,
CAST(is_holiday AS INT64) AS is_holiday,

CASE
WHEN EXTRACT(DAYOFWEEK FROM trip_date) IN (1,7)
THEN 1
ELSE 0
END AS is_weekend,

EXTRACT(DAYOFWEEK FROM trip_date) AS day_of_week,
EXTRACT(MONTH FROM trip_date) AS month,
EXTRACT(QUARTER FROM trip_date) AS quarter,
EXTRACT(DAYOFYEAR FROM trip_date) AS day_of_year,

lag_1,
lag_7,
rolling_7d,

total_trips

FROM base

WHERE
lag_1 IS NOT NULL
AND lag_7 IS NOT NULL
AND rolling_7d IS NOT NULL
AND EXTRACT(YEAR FROM trip_date) = 2023

ORDER BY trip_date;