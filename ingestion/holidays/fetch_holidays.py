import requests
import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "taxi-data-engineering-504910"
DATASET = "bronze"
TABLE = "raw_holidays"

years = range(2013, 2024)

all_holidays = []

for year in years:
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/US"

    response = requests.get(url)
    response.raise_for_status()

    holidays = response.json()

    for holiday in holidays:
        all_holidays.append(
            {
                "holiday_date": holiday["date"],
                "holiday_name": holiday["localName"],
                "country": holiday["countryCode"],
            }
        )

df = pd.DataFrame(all_holidays)

client = bigquery.Client(project=PROJECT_ID)

table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"

job = client.load_table_from_dataframe(
    df,
    table_id,
    job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"),
)

job.result()

print(df.head())
print(f"Loaded {len(df)} holidays into {table_id}")
