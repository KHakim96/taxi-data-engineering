from google.cloud import bigquery
from xgboost import XGBRegressor
from joblib import dump
import pandas as pd

from config import TRAINING_QUERY, MODEL_PATH
from utils import read_sql

client = bigquery.Client()

query = read_sql(TRAINING_QUERY)

df = client.query(query).to_dataframe()

print(f"Loaded {len(df)} rows")

X = df.drop(columns=["trip_date", "total_trips"])
y = df["total_trips"]

model = XGBRegressor(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    objective="reg:squarederror",
)

model.fit(X, y)

dump(model, MODEL_PATH)

print(f"Model saved to {MODEL_PATH}")
