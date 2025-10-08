import streamlit as st
from datetime import datetime 
import openrouteservice
import requests
import os
from dotenv import load_dotenv
from streamlit_folium import st_folium
import folium
import statistics
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")
client = openrouteservice.Client(key=ORS_API_KEY)


#-- Hämtar aktuellt USD -> SEK-kurs från ett öppet API.
#-- Om API:t inte svarar används en fallbackkurs (9.5 SEK/USD).
def fetch_usd_to_sek(fallback=9.5):
    url = "https://api.exchangerate.host/latest?base=USD&symbols=SEK"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return data["rates"]["SEK"]
    except Exception as e:
        print("Valutakurs kunde inte hämtas:", e)
        return fallback

#-- Tar ett ortnamn/adress och retunerar koordinater [lon, lat] via OpenRouteService.
#-- Används för att skapa rutt mellan två platser.

def get_coordinates(place_name):
    geocode = client.pelias_search(place_name)
    features = geocode.get("features")
    if not features:
        return None
    return features[0]["geometry"]["coordinates"] 

#-- Hämtar ruttdata mellan två platser: avstånd i km, tid i minuter, samt ruttens geometri.
#-- Om API:t misslyckas används en fallbackrutt Göteborg -> Malmö.

def get_route_info(origin_name, destination_name):
    try:
        origin_coords = get_coordinates(origin_name)
        destination_coords = get_coordinates(destination_name)

        if not origin_coords or not destination_coords:
            raise ValueError("Kunde inte hämta koordinater")
    
        route = client.directions([origin_coords, destination_coords], profile='driving-car', format='geojson')
        summary = route['features'][0]['properties']['summary']
        geometry = route['features'][0]['geometry']['coordinates']
        distance_km = summary['distance'] / 1000
        duration_min = summary['duration'] / 60
        return distance_km, duration_min, origin_coords, destination_coords, geometry

    except Exception as e:
        print(f"❌ Fallback aktiverad pga fel/API sida är nere: {e}")

        #-- Fallback Göteborg -> Malmö ifall api:et skulle ligga nere

        fallback_distance = 271.9
        fallback_duration = 178.4
        fallback_origin = [11.9746, 57.7089] #Göteborg

        fallback_destination = [13.0007, 55.6050] #Malmö

        fallback_geometry = [[11.9746, 57.7089], [13.0007, 44.6050]]
        return fallback_distance, fallback_duration, fallback_origin, fallback_destination, fallback_geometry 

#-- Visar rutt på karta  med start/slutmarkörer och linje mellan punkterna.
#-- Visuell feedback till användaren

def show_route_map(origin_coords, destination_coords, route_geometry):
    midpoint = [
        (origin_coords[1] + destination_coords[1]) / 2,
        (origin_coords[0] + destination_coords[0]) /2
    ]

    m = folium.Map(location=midpoint, zoom_start=6)

    folium.Marker(
        location=[origin_coords[1], origin_coords[0]],
        popup="Start",
        icon=folium.Icon(color="green")
    ).add_to(m)

    folium.Marker(
        location=[destination_coords[1], destination_coords[0]],
        popup="Slut",
        icon=folium.Icon(color="red")
    ).add_to(m)

    folium.PolyLine(
        locations=[(lat, lon) for lon, lat in route_geometry],
        color="blue",
        weight=5,
        opacity=0.7
    ).add_to(m)

    st_folium(m, width=700, height=500)

#-- Initierar session state-variabler för att hantera prisstatus och felmeddelanden. 

if "price_ready" not in st.session_state:
    st.session_state.price_ready = False

if "error" not in st.session_state:
    st.session_state.error = None


st.title("Taxipris från adress till adress")
st.caption("📍 Skriv in två svenska adresser eller orter för att beräkna taxipriset mellan dem.")

if "used_fallback" not in st.session_state:
    st.session_state.used_fallback = False


st.sidebar.markdown("### ⏰ Livetid")
st.sidebar.markdown(f"**{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")

#-- Inputfält för start och destination samt kontextuella faktorer
#-- Dessa används som input till prismodellen.

origin = st.text_input("🏁 Startpunkt", placeholder="Exempel: Vasagatan 1, Göteborg eller bara Göteborg")
destination = st.text_input("🎯 Slutadress eller ort", placeholder="Exempel: Stortorget 5, Malmö eller bara Malmö")

time_of_day = st.selectbox("🕒 Tid på dagen", ["Morning", "Afternoon", "Evening", "Night"])
day_of_week = st.selectbox("📅 Veckodag", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
weather = st.selectbox("🌦️ Väder", ["Clear", "Rain", "Snow", "Fog"])
traffic = st.selectbox("🚗 Trafikläge", ["Low", "Moderate", "High"])

#-- När användaren klickar på "Beräkna pris" hämtas ruttdata och sparas i session state.
#-- Om rutt saknas visas ett felmeddelande.

if st.button("Beräkna pris"):
    st.session_state.origin = origin
    st.session_state.destination = destination
    distance_km, duration_min, origin_coords, destination_coords, geometry = get_route_info(origin, destination)
    
    if distance_km is None:
        st.session_state.price_ready = False
        st.session_state.error = "Kunde inte hitta en rutt mellan orterna."

    else:
        st.session_state.price_ready = True
        st.session_state.error = None
        st.session_state.distance_km = distance_km
        st.session_state.duration_min = duration_min
        st.session_state.origin_coords = origin_coords
        st.session_state.destination_coords = destination_coords
        st.session_state.geometry = geometry

if "error" in st.session_state and st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.price_ready:
    st.write(f"Avstånd: {st.session_state.distance_km:.1f} km")
    st.write(f"Tid: {st.session_state.duration_min:.1f} minuter")
    
    show_route_map(
        st.session_state.origin_coords,
        st.session_state.destination_coords,
        st.session_state.geometry
    )
    if st.session_state.used_fallback:
        st.markdown("🏴 **Fallback används -- ruttdata är statisk.**")
    else:
        st.markdown("🏳️ **Live-rutt från OpenRouteService används**")

    input_data = {
        "Trip_Distance_km": st.session_state.distance_km,
        "Base_Fare": 35.0,
        "Per_Km_Rate": 12.0,
        "Per_Minute_Rate": 2.5,
        "Trip_Duration_Minutes": st.session_state.duration_min,
        "Time_of_Day": time_of_day,
        "Day_of_Week": day_of_week,
        "Weather": weather,
        "Traffic_Conditions": traffic
            }
    #st.write("Input till modellen", input_data)

#-- Skickar input till /predict-endpoint och visar pris i USD och SEK.

    with st.spinner("Beräknar pris ..."):
        response = requests.post("http://127.0.0.1:8000/predict", json=input_data)
        if response.status_code == 200:

            predicted_price = response.json()["predicted_price"]

            usd_to_sek = fetch_usd_to_sek()
            price_sek = predicted_price * usd_to_sek

            col1, col2 = st.columns(2)
            col1.metric("Pris i USD", f"{predicted_price:.2f} $")
            col2.metric("Pris i SEK", f"{price_sek:.2f} kr")

            if usd_to_sek == 9.5:
                st.caption("⚠️ Valutakurs: 1 USD ≈ 9.50 SEK (fallback)")
            else:
                st.caption(f"✅ Valutakurs: 1 USD ≈ {usd_to_sek:.2f} SEK (live)")
            st.success("Pris beräknat! 🎉🚕")
            
            #-- GIF visas efter lyckad beräkning

            gif_url = "https://media.giphy.com/media/arZ261VdyAuXu/giphy.gif"
            with st.container():
                st.image(gif_url, use_container_width=True)

        #-- insights för att ge användaren exempel på rutter, är också en framtida implementation 
        #-- Skickar input till /insights-endpoint för att hämgta liknande resor.
        #-- Visualisering med tabell och graf är planerad men ej aktiv just nu.
        
        # insights_response = requests.post("http://127.0.0.1:8000/insights", json=input_data)
        # if insights_response.status_code == 200:
        #         insights = insights_response.json()
        #         #avvikelse vid 2 kortare distanser. 
        #         default_trips = [
        #         {"Trip_Distance_km": 462.8, "Trip_Price": 118.19, "Sträcka": "Stockholm -> Göteborg"},
        #         {"Trip_Distance_km": 276.9, "Trip_Price": 118.19, "Sträcka": "Göteborg  -> Malmö"},
        #         {"Trip_Distance_km": 113.9, "Trip_Price": 111.38, "Sträcka": "Båstad -> Malmö"},
        #         {"Trip_Distance_km": 247.5, "Trip_Price": 118.19, "Sträcka": "Karlstad -> Göteborg"},
        #         {"Trip_Distance_km": 132.1, "Trip_Price": 117.32, "Sträcka": "Göteborg -> Smögen"}                    
        #         ]
        #         st.write("Insights statuskod:", insights_response.status_code)
        #         st.write("Insights-data:", insights)
        #         if not insights: 
        #             st.caption("Visar standardresor för jämförelse.")
        #             insights = default_trips
        #         if insights:
        #             with st.expander("🔍 Visa liknande resor"):

        #                 df = pd.DataFrame(insights)
        #                 df = df[["Trip_Distance_km", "Trip_Price"]].rename(columns={
        #                     "Trip_Distance_km": "Avstånd (km)", 
        #                     "Trip_Price": "Pris (kr)"
        #                     })
                            
        #                 styled_df = df.style.background_gradient(subset=["Pris (kr)"], cmap="YlOrRd")
        #                 st.dataframe(styled_df, use_container_width=True)
        #                 avg_price = statistics.mean(df["Pris (kr)"])
        #                 st.markdown(f"**📈 Genomsnittspris: {avg_price:.2f} kr**")
                    
                        # -- grafen är en framtida implementation
                        # fig = px.scatter(
                        #     df,
                        #     x="Avstånd (km)",
                        #     y="Pris (kr)",
                        #     title="Pris vs Avstånd för liknande resor",
                        #     labels={"Avstånd (km)": "Avstånd (km)", "Pris (kr)": "Pris (kr)"},
                        #     template="simple_white",
                        #     color="Pris (kr)",
                        #     size="Pris (kr)",
                        #     hover_data=["Avstånd (km)", "Pris (kr)"]
                        # )

                        # fig.add_trace(go.Scatter(
                        #     x=[input_data["Trip_Distance_km"]],
                        #     y=[price_sek],
                        #     mode="markers",
                        #     marker=dict(size=12, color="blue", symbol="star"),
                        #     name="Din resa",
                        #     hovertext=[f"Din resa: {input_data['Trip_Distance_km']:.1f} km -> {price_sek:.2f} kr"]
                        # ))
                        # st.plotly_chart(fig, use_container_width=True)
                #else:
                        #st.info("🔍 Inga liknande resor hittades för den här kombinationen")
        else:
            st.error("Kunde inte få ett pris från API:t.")
#test

# st.markdown("---")
# st.subheader("🧪 Testa modellen med exempelresor")

# test_resor = [
#     {"Trip_Distance_km": 5, "Base_Fare": 35, "Per_Km_Rate": 12, "Per_Minute_Rate": 2.5,
#     "Trip_Duration_Minutes": 15, "Time_of_Day": "Morning", "Day_of_Week": "Monday", "Weather": "Clear", "Traffic_Conditions": "Low"},

#     {"Trip_Distance_km": 25, "Base_Fare": 35, "Per_Km_Rate": 12, "Per_Minute_Rate": 2.5, "Trip_Duration_Minutes": 45, "Time_of_Day": "Evening", "Day_of_Week": "Friday", "Weather": "Rain", "Traffic_Conditions": "High"},
# ]

# results = []
# for resa in test_resor:
#     try:
#         r = requests.post("http://127.0.0.1:8000/predict", json=resa)
#         predicted = r.json()["predicted_price"]
#     except Exception as e:
#         predicted = f"Fel: {e}"
#     results.append({**resa, "Predicted_Price": predicted})
# df_test = pd.DataFrame(results)
# st.dataframe(df_test, width='stretch')

# if st.session_state.price_ready or st.session_state.error:
#     if st.button("🔄Återställ"):
#         st.session_state.clear()
#         st.experimental_rerun()

