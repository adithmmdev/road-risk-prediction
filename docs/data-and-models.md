# Data and model artifacts

The inference entry point is `ml-engine/src/inference/predict_api.py`. It expects these files relative to `ml-engine/`:

| File | Expected contents |
| --- | --- |
| `models/universal_severity_model.pkl` | A model exposing `predict` for the saved feature columns |
| `models/universal_feature_names.pkl` | The exact ordered feature names used during training |
| `models/universal_target_bounds.pkl` | A pair of lower and upper target bounds, with upper greater than lower |
| `data/processed/chennai_geometry_final.csv` | Road rows with a numeric `geometry_risk_score` column on a 0–100 scale |

These artifacts are excluded from Git and are not provided by a release or download link in this repository. A fresh clone cannot reproduce full predictions without them. The experiment scripts refer to additional local datasets and are not a complete training pipeline.

The frontend GeoJSON is committed at `frontend/public/chennai_roads.geojson`. The API currently indexes the processed CSV by row position. A matching ordering between map identifiers and CSV rows must be established; copying an unrelated geometry file will not produce trustworthy road-specific results.

Only load pickle/joblib model files from a trusted source: deserializing them can execute code. Record the training data version, split, preprocessing, library versions and validation metrics alongside any future published artifacts.
