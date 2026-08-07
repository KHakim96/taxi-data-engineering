from google.cloud import bigquery
import pandas as pd

from config import PREDICTION_QUERY
from utils import read_sql, load_model

client = bigquery.Client()

query = read_sql(PREDICTION_QUERY)

df = client.query(query).to_dataframe()

print(f"Loaded {len(df)} prediction rows")

X = df.drop(columns=["trip_date", "total_trips"])

model = load_model("ml/models/xgboost.pkl")

df["predicted_total_trips"] = model.predict(X)

df.to_csv("ml/outputs/predictions.csv", index=False)

print("Predictions saved to ml/outputs/predictions.csv")
