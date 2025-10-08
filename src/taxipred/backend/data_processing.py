from taxipred.utils.constants import TAXI_CSV_PATH 
import pandas as pd 
import json

#-- Klass för att hantera och analysera taxidata från CSV

class TaxiData:
    def __init__(self):
        try: 
            self._df = pd.read_csv(TAXI_CSV_PATH)
        except Exception as e:
            raise RuntimeError(f"Kunde inte läsa CSV: {e}")

    def to_json(self):
        return json.loads(self.df.to_json(orient = "records"))
    
    def summary(self):
        return {
            "antal resor": len(self._df),
            "medelpris": round(self._df['Trip_Price'].mean(), 2),
            "unika_väder": self._df['Weather'].nunique(),
            "unika_tidpunkter": self._df['Time_of_Day'].nunique()
        }
    
    #-- Framtida implementation
    # def insights(self, input_df):
    #     dist = input_df['Trip_Distance_km'].values[0]
    #     liknande = self._df[
    #         (self._df['Trip_Distance_km'] - dist).abs() < 1.0
    #     ][['Trip_Distance_km', 'Trip_Price']].head(5)
    #     return liknande.to_dict(orient="records")
    
    @property 
    def df(self):
        return self._df
    
