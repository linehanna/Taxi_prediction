from fastapi import FastAPI 
from taxipred.backend.data_processing import TaxiData 


app = FastAPI()

taxi_data = TaxiData()

# to navigate /docs or /taxi
# uvicorn api:app --reload
# uvicorn taxipred.backend.api:app --reload --app-dir src

@app.get("/taxi")
async def read_taxi_data():
    return taxi_data.to_json()