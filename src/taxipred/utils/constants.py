from importlib.resources import files 

#-- Dataset-sökväg - används av TaxiData-klassen för att läsa in taxiresor

TAXI_CSV_PATH = files("taxipred").joinpath("data/taxi_trip_pricing.csv")

#-- Numeriska features - används för att fylla NaN och för modellinput

numeric_cols = [
    'Trip_Distance_km',
    'Base_Fare',
    'Per_Km_Rate',
    'Per_Minute_Rate',
    'Trip_Duration_Minutes'
]

#-- Kategoriska features - används för att fylla NaN och för modellinput

categorical_cols = [
    'Time_of_Day',
    'Day_of_Week',
    'Weather',
    'Traffic_Conditions'
]