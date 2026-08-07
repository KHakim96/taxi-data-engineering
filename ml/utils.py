from google.cloud import bigquery
import joblib

client = bigquery.Client()


def read_sql(path):
    with open(path, "r") as f:
        return f.read()


def save_model(model, path):
    joblib.dump(model, path)


def load_model(path):
    return joblib.load(path)
