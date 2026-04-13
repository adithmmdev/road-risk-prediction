import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================================
# PATHS
# =========================================

RESULT_DIR = "results"

metrics_path = os.path.join(RESULT_DIR, "metrics.csv")
preds_path = os.path.join(RESULT_DIR, "predictions.csv")

# Load
metrics = pd.read_csv(metrics_path)
preds = pd.read_csv(preds_path)

# =========================================
# 1. MAPE COMPARISON
# =========================================

plt.figure()
plt.bar(metrics["model"], metrics["mape"])
plt.title("MAPE Comparison")
plt.ylabel("MAPE (%)")
plt.xlabel("Model")
plt.savefig(os.path.join(RESULT_DIR, "mape_comparison.png"))
plt.close()

# =========================================
# 2. RMSE COMPARISON
# =========================================

plt.figure()
plt.bar(metrics["model"], metrics["rmse"])
plt.title("RMSE Comparison")
plt.ylabel("RMSE")
plt.xlabel("Model")
plt.savefig(os.path.join(RESULT_DIR, "rmse_comparison.png"))
plt.close()

# =========================================
# 3. ERROR DISTRIBUTION
# =========================================

plt.figure()

for col in preds.columns[1:]:
    error = preds["actual"] - preds[col]
    plt.hist(error, bins=50, alpha=0.4, label=col)

plt.legend()
plt.title("Error Distribution Comparison")
plt.xlabel("Error")
plt.ylabel("Frequency")

plt.savefig(os.path.join(RESULT_DIR, "error_distribution.png"))
plt.close()

# =========================================
# 4. PRED VS ACTUAL (XGBoost)
# =========================================

plt.figure()
plt.scatter(preds["actual"], preds["XGBoost"], alpha=0.3)
plt.plot([1, 4], [1, 4])
plt.xlabel("Actual Severity")
plt.ylabel("Predicted Severity")
plt.title("Predicted vs Actual (XGBoost)")

plt.savefig(os.path.join(RESULT_DIR, "pred_vs_actual.png"))
plt.close()

print("✅ All plots generated successfully.")