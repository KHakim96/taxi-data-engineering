# Q1: Top 100 Tip Earners

**Definition:** Taxi IDs that earn more tips than others, ranked by total tips.

**Assumptions:**

- "Earn more money" = total tips (not total revenue or fare)
- Time window is user-controlled — the Looker Studio date picker filters the data; top 100 is applied via Looker's "top N" ranking on the filtered set

**Methodology:**

- Source table: `gold.tip_earners` (one row per taxi per day, with `total_tips`, `total_revenue`, `total_fare`, `total_trip_miles`, `trip_count`)
- Looker Studio: aggregate SUM(`total_tips`) by `taxi_label`, apply Top N = 100, sort descending
- User selects the time window via the date range picker


# Q2: Vehicle Utilization Beyond Single-Driver Capacity

**Definition:** Taxi IDs (vehicles) whose daily active operating time exceeds what one legal driver would be permitted to drive, ranked by vehicle-days beyond that capacity.

**Assumptions:**

- "Active time" = union of non-overlapping trip intervals per vehicle per Chicago-local calendar day (merged with a sweep-line algorithm; overlaps counted once, gaps not counted)
- "Single-driver capacity" = 12 active hours, the Chicago chauffeur limit (MCC §9-112-250: no chauffeur operates a taxicab more than 12 consecutive hours in a 24-hour period)
- Records flagged `IMPLAUSIBLE_SPEED` in Silver (≥2 hours at <3 mph — meter/device artifacts) are excluded from trusted utilization; their count is retained in `implausible_records_excluded`
- Time window is user-controlled — the Looker Studio date picker filters the data; top 100 applied via Looker's "top N" ranking on the filtered set
- The dataset has no driver identifier; `taxi_id` is a medallion-level **vehicle** identifier

**Limitations:**

- A vehicle-day >12 active hours is **indistinguishable** between one overworking driver and two leased shifts sharing the medallion (the industry-standard 12h/24h lease structure) — hence the classification label "Exceeds single-driver legal capacity (multi-driver and/or overwork — indeterminate)"
- This metric never claims driver identity, driver hours, or driver rest compliance

**Methodology:**

- Utilization model: `gold.vehicle_activity_day` (one row per taxi × activity date) computes `active_hours` from merged, midnight-clipped intervals; classification at >12 active hours
- Report table: `gold.overworkers` (name kept for Looker compatibility) provides per taxi-day `days_exceeding_single_driver_capacity` (0/1, summed in Looker), `total_active_hours`, `max_daily_active_hours`, `avg_daily_active_hours`
- Looker Studio: aggregate SUM(`days_exceeding_single_driver_capacity`) by `taxi_label` over the selected date range, apply Top N = 100, sort descending
- Utilization intensity is visible via `max_daily_active_hours` and the ratio of capacity-exceeding days to total days


## Q3: Public Holiday Impact on Trips

### Definition
Analyze how taxi demand differs on public holidays compared with weekdays and weekends.

### Assumptions
- Impact = difference in observed daily taxi trips.
- Weather may influence demand, so it can be filtered for context.
- Holiday data sourced from Nager.Date API via `dim_holiday`.

### Methodology
- Source: `gold.holiday_weather_impact`
- Grain: 1 row per day.
- Compare demand across Weekday, Weekend, and Holiday.
- Analyze demand and trip duration by weather condition.
- Rank individual holidays by observed taxi demand.

## Bonus Insight 1 — Recurring Mid-October Demand Spike

**Insight:**  
Daily taxi demand shows a recurring spike around **10–20 October across multiple years**, consistently higher than surrounding periods.

**Business value:**  
The operator can anticipate this recurring seasonal demand and increase driver availability/capacity during this period to reduce unmet demand and improve service availability.

**Supporting data:**

- Daily demand trend across multiple years
- Consistent demand increase around 10–20 October
- Comparison against surrounding October dates

## Bonus Insight 2 — Demand Forecasting for Capacity Planning

**Insight:**  
The XGBoost model can forecast daily taxi demand using historical demand, calendar, holiday, and weather features.

**Business value:**  
Forecasts can help planners anticipate high/low-demand days and adjust driver availability and fleet capacity before demand occurs.