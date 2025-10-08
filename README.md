## 🚕 Taxi Price Prediction App

En modulär och användarvänlig applikation för att prediktera taxipriser baserat på resedata. Appen kombinerar maskininlärning, API-design och interaktiv visualisering för att ge tillförlitliga prisestimat.
---

## Teknikstack

- **Machine Learning**: scikit-learn, XGBoost
- **Backend**: FastAPI
- **Frontend**: Streamlit + Folium
- **Modellhantering**: joblib
- **Ruttberäkning**: OpenRouteService API
- **Visualisering**: Plotly, Seaborn
  ---

##  ⚙️ Installation
```bash
git clone https://github.com/linehanna/Taxi_prediction.git
uv pip install -r requirements.txt
```
##  Användning

1. Starta API:
```bash
uvicorn api:app --reload
```
2. Öppna ny terminal
   
streamlit run streamlit_app.py

### Modellbeskrivning

Modellen tränas på data om taxiresor och använder regressionsalgoritmer som Linear Regression, XGBoost. Feature engineering inkluderar features som distans väder, trafik. Utvärdering sker med MAE, RMSE, R².

## Projektstruktur

TAXI-PREDICTION/
├── .env                      # Miljövariabler (API-nycklar, konfiguration)
├── .gitignore               # Ignorerade filer för versionshantering
├── .python-version          # Python-version för miljöhantering
├── README.md                # Projektbeskrivning och instruktioner
├── requirements.txt         # Lista över Python-paket
├── setup.py                 # Installations- och paketkonfiguration
├── explorations/
│   └── eda.ipynb            # Exploratory Data Analysis (EDA)
├── src/
│   └── taxipred/
│       ├── backend/
│       │   ├── api.py                 # FastAPI-endpoints för prediktion och insikter
│       │   ├── data_processing.py     # Funktioner för datarensning och transformation
│       │   └── data/
│       │       ├── cleaned_data.csv
│       │       ├── predicted_output.csv
│       │       ├── prediction_input.csv
│       │       └── taxi_trip_pricing.csv
│       ├── frontend/
│       │   ├── streamlit_app.py       # Streamlit-gränssnitt för användarinteraktion
│       │   ├── model_dev/
│       │   │   ├── ml_model_taxipricepred.ipynb
│       │   │   ├── ml_model_tts.ipynb
│       │   │   ├── ml_pred.ipynb
│       │   │   ├── scaler.joblib      # Skalad transformer
│       │   │   └── taxiprice_model.pkl# Tränad ML-modell
│       │   └── utils/
│       │       ├── constants.py       # Konstanter och inställningar
│       │       └── __init__.py
│       └── __init__.py
├── taxi_prediction.egg-info/ # Metadata för paketering
└── .venv/                    # Virtuell miljö (lokal, ej versionshanterad)

## Vidareutveckling
- [ ] Förbättra modellprecision med fler features
- [ ] Lägga till insiktsmodul för prisfördelning
- [ ] Exportera prediktioner som PDF eller CSV
- [ ] Implementera användarautentisering, användarprofil som i en riktig app. 

 
