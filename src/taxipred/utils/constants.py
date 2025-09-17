from importlib.resources import files 

TAXI_CSV_PATH = files("taxipred").joinpath("data/taxi_trip_pricing.csv")

#print(TAXI_CSV_PATH)