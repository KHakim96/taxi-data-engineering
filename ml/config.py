PROJECT_ID = "taxi-data-engineering-504801"

DATASET = "gold"

TABLE = "fact_daily_demand"

PREDICTION_DATASET = "ml"

PREDICTION_TABLE = "model_predictions"

MODEL_PATH = "ml/models/xgboost.pkl"

TRAINING_QUERY = "ml/sql/training_dataset.sql"

PREDICTION_QUERY = "ml/sql/prediction_dataset.sql"
