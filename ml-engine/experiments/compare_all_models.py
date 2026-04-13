import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

# ======================================================
# PATHS (SIMPLE & RELIABLE)
# ======================================================

DATA_PATH = os.path.join("..", "data", "processed", "accidents_processed.csv")
RESULT_DIR = os.path.join("results")

os.makedirs(RESULT_DIR, exist_ok=True)

# ======================================================
# LOAD DATA
# ======================================================

print("Loading dataset...")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)

X = df.drop(columns=["Severity"])
y = df["Severity"]

# ======================================================
# TRAIN / TEST SPLIT (SAME AS MAIN MODEL)
# ======================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42
)

print("Train:", X_train.shape)
print("Test:", X_test.shape)

# ======================================================
# SAFE MAPE FUNCTION
# ======================================================

def compute_mape(y_true, y_pred):
    y_true = np.clip(y_true, 1, None)  # avoid division by zero
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

# ======================================================
# EVALUATION FUNCTION (ADVANCED)
# ======================================================

def evaluate_model(name, model):
    print(f"\nTraining {name}...")

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    mape = compute_mape(y_test.values, y_pred)
    r2 = r2_score(y_test, y_pred)

    median_ae = np.median(np.abs(y_test - y_pred))
    std_error = np.std(y_test - y_pred)

    print(f"{name} RMSE: {rmse:.4f}")
    print(f"{name} MAE: {mae:.4f}")
    print(f"{name} MAPE: {mape:.2f}%")
    print(f"{name} R2: {r2:.4f}")

    return {
        "model": name,
        "rmse": rmse,
        "mae": mae,
        "mape": mape,
        "r2": r2,
        "median_ae": median_ae,
        "std_error": std_error,
        "predictions": y_pred
    }

# ======================================================
# MODELS
# ======================================================

models = [
    ("Linear Regression", LinearRegression()),
    ("Random Forest", RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )),
    ("XGBoost", XGBRegressor(
        n_estimators=1200,
        max_depth=6,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=2.0,
        min_child_weight=3,
        gamma=0.1,
        objective="reg:squarederror",
        tree_method="hist",
        random_state=42,
        n_jobs=-1
    ))
]

# ======================================================
# RUN MODELS
# ======================================================

results = []
all_preds = pd.DataFrame()
all_preds["actual"] = y_test.values

for name, model in models:
    res = evaluate_model(name, model)

    results.append({
        k: v for k, v in res.items() if k != "predictions"
    })

    all_preds[name] = res["predictions"]

# ======================================================
# SAVE RESULTS
# ======================================================

metrics_df = pd.DataFrame(results)
metrics_df.to_csv(os.path.join(RESULT_DIR, "metrics.csv"), index=False)

all_preds.to_csv(os.path.join(RESULT_DIR, "predictions.csv"), index=False)

print("\n✅ Saved metrics and predictions successfully.")
print("📁 Location:", RESULT_DIR)