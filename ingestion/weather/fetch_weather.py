import requests
import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "taxi-data-engineering-504910"
DATASET = "bronze"
TABLE = "raw_weather"

LATITUDE = 41.8781
LONGITUDE = -87.6298

START_DATE = "2013-01-01"
END_DATE = "2023-12-31"

url = (
    "https://archive-api.open-meteo.com/v1/archive?"
    f"latitude={LATITUDE}"
    f"&longitude={LONGITUDE}"
    f"&start_date={START_DATE}"
    f"&end_date={END_DATE}"
    "&daily="
    "temperature_2m_max,"
    "temperature_2m_min,"
    "temperature_2m_mean,"
    "precipitation_sum,"
    "snowfall_sum,"
    "wind_speed_10m_max"
    "&timezone=UTC"
)

response = requests.get(url)
response.raise_for_status()

weather = response.json()["daily"]

df = pd.DataFrame(
    {
        "weather_date": weather["time"],
        "temperature_max": weather["temperature_2m_max"],
        "temperature_min": weather["temperature_2m_min"],
        "temperature_mean": weather["temperature_2m_mean"],
        "precipitation_mm": weather["precipitation_sum"],
        "snowfall_cm": weather["snowfall_sum"],
        "wind_speed_kmh": weather["wind_speed_10m_max"],
    }
)

client = bigquery.Client(project=PROJECT_ID)

table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"

job = client.load_table_from_dataframe(
    df, table_id, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
)

job.result()

print(df.head())
print(f"\nLoaded {len(df):,} rows into {table_id}")
