import pandas as pd
from google.cloud import bigquery

from config import (
    PROJECT_ID,
    PREDICTION_DATASET,
    PREDICTION_TABLE,
)

client = bigquery.Client(project=PROJECT_ID)

df = pd.read_csv("ml/outputs/predictions.csv")

table_id = f"{PROJECT_ID}.{PREDICTION_DATASET}.{PREDICTION_TABLE}"

job = client.load_table_from_dataframe(df, table_id)

job.result()

print(f"Loaded {len(df)} rows into {table_id}")
