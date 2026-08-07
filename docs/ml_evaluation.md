# XGBoost Model Evaluation

## Project

Chicago Taxi Demand Forecasting

---

## Model

- Algorithm: XGBoost Regressor
- Training Data: 2013–2022
- Test Data: 2023
- Target: total_trips

---

## Features

- Temperature (max, min, mean)
- Precipitation
- Snowfall
- Wind Speed
- Holiday Flag
- Rain Flag
- Snow Flag
- Day of Week
- Month
- Weekend Flag
- Previous Day Trips (lag_1)
- Previous Week Trips (lag_7)
- 7-Day Rolling Average

---

## Test Results

| Metric | Value |
|---------|------:|
| MAE | **1,264.85** |
| RMSE | **1,657.16** |
| MAPE | **7.80%** |
| R² | **0.8143** |

---

## Interpretation

- The model explains approximately **81.4%** of the variance in daily taxi demand on the 2023 test dataset.
- On average, predictions deviate from the actual number of daily trips by approximately **1,265 trips** (MAE).
- The model achieves a **7.8% Mean Absolute Percentage Error (MAPE)**, indicating strong forecasting accuracy for daily demand.

---

## End-to-End ML Pipeline

```text
                    Chicago Taxi Trips
              (BigQuery Public Dataset)
                           │
                           ▼
                    Dataform Pipeline
        Bronze → Silver → Gold (fact_daily_demand)
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
  Weather API                     Holiday API
          │                                 │
          └───────────────┬─────────────────┘
                          ▼
              gold.fact_daily_demand
                          │
                          ▼
       training_dataset.sql (2013–2022)
                          │
                          ▼
                 train.py (XGBoost)
                          │
                          ▼
                xgboost.pkl (Saved Model)
                          │
                          ▼
      prediction_dataset.sql (2023 Holdout)
                          │
                          ▼
                    predict.py
                          │
                          ▼
                 predictions.csv
                          │
                          ▼
                  evaluate.py
                          │
                          ▼
              Performance Metrics
       (R², MAE, RMSE, MAPE)
                          │
                          ▼
             upload_predictions.py
                          │
                          ▼
         BigQuery (ml.model_predictions)
                          │
                          ▼
               Looker Studio Dashboard
```

---

## Files

- `ml/train.py`
- `ml/predict.py`
- `ml/evaluate.py`
- `ml/upload_predictions.py`

---

## Output

- `ml/models/xgboost.pkl`
- `ml/outputs/predictions.csv`