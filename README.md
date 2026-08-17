# Road Risk Prediction

This is a project I built to explore how machine learning and geospatial data can be used to identify roads that may have a higher accident risk.

The current version focuses on Chennai and combines accident data, road geometry, time information, and weather context. The result is shown through an interactive map and can also be accessed through an API.

## What I built

I wanted to build the project as a complete system rather than only training a model.

The main parts are:

* A React map for selecting and viewing road risk
* An Express API for handling requests
* A Python machine learning layer for inference
* Geospatial processing with OpenStreetMap data
* Road geometry features such as length, curvature and intersection density
* Weather information from Open Meteo
* A risk calculation that combines the model output with a geometry based score

## How it works

```text
React map
   ↓
Express API
   ↓
Python inference
   ↓
Model + road features + weather context
   ↓
Final risk score
   ↓
Map result
```

The current committed model uses an XGBoost regressor for accident severity. Its output is normalized and combined with a geometry risk score.

```text
Final Risk = 0.65 × ML Risk + 0.35 × Geometry Risk
```

The project currently uses three risk levels: LOW, MEDIUM and HIGH.

## Machine learning work

The feature work includes things such as:

* Hour of day
* Day of week
* Weekend and night indicators
* Weather related features
* Road length
* Curvature
* Intersection density
* Network density
* Road type

I also experimented with different models and used metrics such as RMSE, MAE, MAPE and R² while comparing them.

SHAP based analysis is included for looking at which features influence predictions.

## Project structure

```text
road-risk-prediction/
├── backend/
├── frontend/
├── ml-engine/
│   ├── experiments/
│   └── src/
├── documentation/
├── .github/
│   └── workflows/
└── README.md
```

## Running it locally

### Backend

```bash
cd backend
npm install
npm start
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Python inference code also needs the required model and geospatial files to be available locally.

## Things I learned from this project

This project taught me that getting a model to work is only one part of building an ML system. A useful application also needs data processing, feature creation, API design, frontend integration and a way to make the result understandable to the user.

I also spent time dealing with practical issues such as large geospatial files, separating generated data from source code, and keeping the model pipeline consistent with the API.

## Current limitations

The baseline model was trained using accident data that does not come directly from Chennai, so geographic transfer is an important limitation.

The current risk weights are also heuristic and need proper validation with local ground truth before the system could be used for real road safety decisions.

This is a project for learning, experimentation and demonstration.

## Tech used

Python, Pandas, NumPy, scikit learn, XGBoost, SHAP, OSMnx, GeoPandas, Shapely, React, Vite, Leaflet, Node.js, Express and Open Meteo.
