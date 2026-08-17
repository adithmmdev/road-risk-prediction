# AI-Driven Road Accident Risk Prediction Platform

A full-stack geospatial machine-learning platform for assessing road-segment accident risk in Chennai. The system combines historical accident data, road geometry, temporal context, and live weather conditions to return an explainable risk score through an interactive map.

> **Portfolio focus:** geospatial ML + model inference + REST API + React/Leaflet visualization.

## Why this project matters

Traditional accident dashboards mostly show where accidents happened in the past. This project turns those historical patterns into a road-level risk assessment workflow that can incorporate current environmental conditions and intrinsic road geometry.

## Architecture

```text
                    ┌──────────────────────┐
                    │ React + Leaflet Map  │
                    └──────────┬───────────┘
                               │ POST /api/risk/predict
                               ▼
                    ┌──────────────────────┐
                    │ Express.js Backend   │
                    │ - request handling   │
                    │ - weather context    │
                    │ - risk response      │
                    └──────────┬───────────┘
                               │ stdin / stdout
                               ▼
                    ┌──────────────────────┐
                    │ Python ML Engine     │
                    │ - feature creation   │
                    │ - XGBoost inference  │
                    │ - geometry lookup    │
                    │ - risk fusion        │
                    └──────────────────────┘
                               ▲
                               │
                    ┌──────────┴───────────┐
                    │ OpenStreetMap +      │
                    │ Open-Meteo weather   │
                    └──────────────────────┘
```

## Current implementation

The committed implementation in this repository uses an **XGBoost Regressor** to estimate accident severity on a 1–4 scale, then normalizes the model output and combines it with a pre-computed geometry-risk score.

The final risk calculation is:

```text
Final Risk = 0.65 × ML Risk + 0.35 × Geometry Risk
```

Risk tiers:

- **LOW:** ≤ 35
- **MEDIUM:** 35–70
- **HIGH:** > 70

The repository also contains model-comparison experiments and an inference API. Any newer experimental model results should be documented separately from this committed baseline so that the repository remains reproducible.

## Key features

- Interactive Chennai road map using React + Leaflet
- Road-segment risk prediction through a REST API
- XGBoost-based accident-severity model
- Live weather context from Open-Meteo
- Temporal features such as hour and weekend status
- Road-geometry risk based on length, curvature, intersection density, network density, and road type
- SHAP-based model explainability tooling
- Frontend prediction caching to reduce repeated API requests
- Separate Node.js API and Python inference layers

## Machine-learning pipeline

### 1. Data preprocessing

The preprocessing workflow transforms accident records into model-ready features including:

- hour of day
- day of week
- weekend indicator
- night indicator
- simplified weather categories
- infrastructure indicators
- missing-value handling

### 2. Model training

The current training configuration uses XGBoost with a histogram-based tree method and regularization. Model-comparison experiments also include Linear Regression and Random Forest baselines.

The experiment scripts report:

- RMSE
- MAE
- MAPE
- R²
- median absolute error
- prediction error distribution

### 3. Geospatial feature engineering

Road geometry is used as a separate structural-risk signal. Features include:

| Feature | Purpose |
|---|---|
| Road length | Captures segment exposure |
| Curvature | Captures turning complexity |
| Intersection density | Captures junction complexity |
| Network density | Captures local road complexity |
| Road type | Encodes road hierarchy |

The resulting geometry score is normalized to a 0–100 scale.

### 4. Inference

For a selected road segment, the system:

1. identifies the road segment;
2. obtains current weather/time context;
3. constructs the model feature vector;
4. runs Python inference;
5. obtains the geometry-risk score;
6. fuses both signals;
7. assigns a LOW/MEDIUM/HIGH tier;
8. returns the result to the map UI.

## API

### `POST /api/risk/predict`

Request:

```json
{
  "road_index": 42
}
```

Response contains the model risk, geometry risk, final risk, risk tier, and contextual information used during inference.

## Repository structure

```text
.
├── backend/
│   ├── controllers/
│   ├── routes/
│   ├── services/
│   └── utils/
├── frontend/
│   ├── public/
│   └── src/
├── ml-engine/
│   ├── experiments/
│   └── src/
│       ├── geo/
│       └── inference/
├── documentation/
├── .github/workflows/ci.yml
└── README.md
```

## Running locally

### Prerequisites

- Node.js 22+
- Python 3.11+
- Git

### Backend

```bash
cd backend
npm install
npm start
```

The backend runs on port `5000` by default.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Python environment

Create a virtual environment and install the Python dependencies required by the ML engine. The inference scripts expect the trained model artifacts and supporting geometry data to be available locally.

> Large datasets and trained artifacts are intentionally not required to be committed to Git. Use a local data/model directory or a documented artifact-storage solution for reproducible deployments.

## CI

GitHub Actions runs on pushes and pull requests to `main` and currently checks:

- frontend dependency installation, linting, and production build;
- backend JavaScript syntax;
- Python source compilation.

The workflow is intentionally lightweight until a deterministic test suite is added.

## Reproducibility notes

This repository contains large geospatial/modeling assets and historical experiment artifacts. The long-term goal is to make the training pipeline reproducible from documented datasets and configuration rather than relying on checked-in generated data.

For model-development work, keep these concerns separate:

```text
raw data → preprocessing → features → training → evaluation → model artifact → inference
```

## Limitations

- The baseline model is trained using accident data that does not originate from Chennai, so geographic transferability is an important modeling assumption.
- Live weather improves contextualization but does not make the prediction causal.
- Risk fusion weights are heuristic and should be validated using local ground-truth data before operational use.
- The current repository is a research/prototype system, not a safety-critical deployment.

## Future engineering work

- Add a deterministic automated test suite for the API and inference pipeline
- Add model/version metadata and experiment tracking
- Replace heuristic fusion weights with a validated calibration strategy
- Add local Chennai accident data for geographic validation
- Containerize backend and ML inference for reproducible deployment
- Add observability, rate limiting, and production security controls

## Tech stack

**Frontend:** React, Vite, Leaflet, React-Leaflet, Axios  
**Backend:** Node.js, Express.js, Axios  
**ML:** Python, Pandas, NumPy, scikit-learn, XGBoost, SHAP  
**Geospatial:** OpenStreetMap, OSMnx, GeoPandas, Shapely, GeoJSON  
**Weather:** Open-Meteo

## Disclaimer

This project is intended for research and demonstration. It should not be used as the sole basis for real-world road-safety decisions.
