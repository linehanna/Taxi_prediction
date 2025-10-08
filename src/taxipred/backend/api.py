from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from taxipred.backend.data_processing import TaxiData 
from taxipred.utils.constants import numeric_cols, categorical_cols #-- Featurelistor på preprocessing
import joblib
import pandas as pd
import os


app = FastAPI()

#-- Laddar den tränade prismodellen från fil

model = joblib.load(os.path.join(os.path.dirname(__file__), '..', 'model_dev', 'taxiprice_model.pkl'))
print("Modelltyp:", type(model))
#-- Initierar dataklass för att kunna returnera exempeldata och sammanfattningar
taxi_data = TaxiData()


class PredictionResponse(BaseModel):
    predicted_price: float

#-- Definerar inputformat för taxiresor- används både för prediktion och insights

class TaxiInput(BaseModel):
    Trip_Distance_km: float = 5.2
    Base_Fare: float = 35.0
    Per_Km_Rate: float = 12.0
    Per_Minute_Rate: float = 2.5
    Trip_Duration_Minutes: float = 18
    Time_of_Day: str = "Evening"
    Day_of_Week: str = "Friday"
    Weather: str = "Clear"
    Traffic_Conditions: str = "Moderate"

#-- Test-endpoint för att verifiera att API:t körs
@app.get("/")
def home():
    return {"message": "Taxi price prediction API is running"}

#-- Huvudendpoint för att beräkna pris baserat på inputdata

@app.post("/predict", response_model=PredictionResponse)
def predict_price(data: TaxiInput):
    df = pd.DataFrame([data.model_dump()])
    print("Input to model: \n", df)

#-- Fyller i saknade värden med standardvärden

    for col in numeric_cols:
        df[col] = df[col].fillna(0)
    for col in categorical_cols:
        df[col] = df[col].fillna("Unknown")

#-- Gör prediktion med laddad modell

    try:
        
        prediction = model.predict(df)[0]
        prediction = float(prediction)

        return {"predicted_price": round(prediction, 2)}
    #-- Felhantering ifall modellen kraschar
    except Exception as e:
        print("Prediction error:", e)
        raise HTTPException(status_code=500, detail=str(e))
    
#-- Returnerar hela taxidatasetet som JSON

@app.get("/taxi")
async def read_taxi_data():
    return taxi_data.to_json()

#-- Returnerar sammanfattning av taxidatasetet

@app.get("/summary")
async def get_summary():
    return taxi_data.summary()

#-- Denna håller på att skapas, framtida implementation
# @app.post("/insights")
# async def get_similar_trips(input: TaxiInput):
#     df = pd.read_csv("../src/taxipred/data/cleaned_data.csv")
#     df["distance_diff"] = abs(df["Trip_Distance_km"] -input.Trip_Distance_km)
#     df_sorted = df.sort_values("distance_diff").head(5)
#     return df_sorted.to_dict(orient="records")

#-- Startkommandon för att köra API:t lokalt
# to navigate thru FAST API /docs or /taxi
# uvicorn api:app --reload
