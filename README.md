# Q1: Top 100 Tip Earners

**Definition:** Taxi IDs that earn more tips than others, ranked by total tips.

**Assumptions:**

- "Earn more money" = total tips (not total revenue or fare)
- Time window is user-controlled — the Looker Studio date picker filters the data; top 100 is applied via Looker's "top N" ranking on the filtered set

**Methodology:**

- Source table: `gold.tip_earners` (one row per taxi per day, with `total_tips`, `total_revenue`, `total_fare`, `total_trip_miles`, `trip_count`)
- Looker Studio: aggregate SUM(`total_tips`) by `taxi_label`, apply Top N = 100, sort descending
- User selects the time window via the date range picker


# Q2: Top 100 Overworkers

**Definition:** Taxi IDs that work more hours than others without taking at least an 8-hour break and regularly have long shifts.

**Assumptions:**

- "8 hours break" = a gap of ≥480 minutes between consecutive trips starts a new shift (implemented in `shift_summary.sqlx`)
- "Long shift" = 12–24 hours. Shifts in this range are classified as Overworker
- "Typical shifts" = the Normal classification (<12 hours) represents typical human work patterns; the fleet-wide median is ~5–8 hours
- Shifts >24 hours are classified as Shared Vehicle Fleet — these represent multi-driver vehicles, not individual overworkers, and are excluded from the overworker ranking
- The dataset has no driver identifier, so `taxi_id` is used as a proxy

**Methodology:**

- Shift reconstruction: `gold.shift_summary` sessionizes trips per taxi using the 8-hour gap rule, then classifies each shift as Normal / Overworker / Shared Vehicle Fleet
- Daily aggregation: `gold.overworkers` rolls shifts up to one row per taxi per day, counting `overworker_shift_count`, `total_shift_hours`, `longest_shift_hours`
- Looker Studio: aggregate SUM(`overworker_shift_count`) by `taxi_label`, apply Top N = 100, sort descending. User selects the time window via the date range picker
- Regularity is visible via `longest_shift_hours` and the ratio of overworker shifts to total shifts


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