import pandas as pd
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error,
)
import numpy as np

df = pd.read_csv("ml/outputs/predictions.csv")

y_true = df["total_trips"]
y_pred = df["predicted_total_trips"]

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
r2 = r2_score(y_true, y_pred)

mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

print("=" * 50)
print("XGBoost Evaluation")
print("=" * 50)

print(f"MAE  : {mae:,.2f}")
print(f"RMSE : {rmse:,.2f}")
print(f"MAPE : {mape:.2f}%")
print(f"R²   : {r2:.4f}")
