import streamlit as st
from dotenv import load_dotenv
import os
import requests
import pandas as pd

load_dotenv()

st.set_page_config(page_title="Performance Load Optimizer", layout="wide")

st.title("Performance Load Optimizer")
st.subheader("Erste Testversion")

st.write("Die App läuft erfolgreich.")

strava_client_id = os.getenv("STRAVA_CLIENT_ID")
strava_client_secret = os.getenv("STRAVA_CLIENT_SECRET")

st.markdown("### Strava-Konfiguration testen")

if strava_client_id and strava_client_secret:
    st.success("Strava Client ID und Client Secret wurden erfolgreich geladen.")
else:
    st.error("Strava Zugangsdaten wurden nicht gefunden. Prüfe deine .env Datei.")

st.markdown("### Mit Strava verbinden")

if strava_client_id:
    redirect_uri = "http://localhost:8501"
    scope = "read,activity:read_all"

    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={strava_client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&approval_prompt=force"
        f"&scope={scope}"
    )

    st.link_button("Mit Strava verbinden", auth_url)
else:
    st.warning("Client ID fehlt – Strava-Verbindung kann nicht erstellt werden.")

st.markdown("### Rückgabe von Strava prüfen")

query_params = st.query_params
code = query_params.get("code")

if code:
    st.success("Strava hat einen Code zurückgegeben.")
else:
    st.info("Noch kein Strava-Code in der URL gefunden.")

st.markdown("### Access Token holen")

access_token = None

if code and strava_client_id and strava_client_secret:
    if st.button("Access Token abrufen"):
        token_url = "https://www.strava.com/oauth/token"

        payload = {
            "client_id": strava_client_id,
            "client_secret": strava_client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }

        response = requests.post(token_url, data=payload)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")

            st.session_state["access_token"] = access_token

            st.success("Access Token erfolgreich erhalten.")
        else:
            st.error("Fehler beim Abrufen des Access Tokens.")
            st.write(response.text)

if "access_token" in st.session_state:
    access_token = st.session_state["access_token"]

st.markdown("### Strava-Aktivitäten abrufen")

if access_token:
    if st.button("Meine Aktivitäten laden"):
        activities_url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"per_page": 50, "page": 1}

        response = requests.get(activities_url, headers=headers, params=params)

        if response.status_code == 200:
            activities = response.json()

            if activities:

                df = pd.DataFrame(activities)

                # Nur Läufe anzeigen
                df = df[df["sport_type"] == "Run"]

                # Einheiten umrechnen
                df["distance_km"] = df["distance"] / 1000
                df["moving_time_min"] = df["moving_time"] / 60

                # Pace berechnen
                df["pace_min_per_km"] = df["moving_time_min"] / df["distance_km"]

                # Datum umwandeln
                df["start_date"] = pd.to_datetime(df["start_date"])

                # letzte 7 Tage filtern
                last_7_days = df[df["start_date"] >= (pd.Timestamp.utcnow() - pd.Timedelta(days=7))]
                
                # Wochenkilometer berechnen
                rolling_weekly_distance = last_7_days["distance_km"].sum()

                # Pace Durchschnitt berechnen
                total_distance = df["distance_km"].sum()
                total_time = df["moving_time_min"].sum()

                avg_pace = total_time / total_distance
                minutes = int(avg_pace)
                seconds = int((avg_pace - minutes) * 60)
                pace_formatted = f"{minutes}:{seconds:02d}"

                columns_to_show = [
                    "name",
                    "sport_type",
                    "distance_km",
                    "moving_time_min",
                    "total_elevation_gain",
                    "start_date"
                ]

                existing_columns = [col for col in columns_to_show if col in df.columns]
                st.dataframe(df[existing_columns])
                st.success("Aktivitäten erfolgreich geladen.")
                st.metric("Rolling Weekly Distance (letzte 7 Tage)", f"{rolling_weekly_distance:.1f} km")
                st.metric("Average Pace", f"{pace_formatted} min/km")

                st.markdown("### Wochenkilometer")

                df["week"] = df["start_date"].dt.to_period("W").astype(str)

                weekly_km = df.groupby("week")["distance_km"].sum().reset_index()
                weekly_km.columns = ["Woche", "Kilometer"]

                st.bar_chart(weekly_km.set_index("Woche"))

            else:
                st.info("Keine Aktivitäten gefunden.")
        else:
            st.error("Fehler beim Laden der Aktivitäten.")
            st.write(response.text)

goal = st.selectbox(
    "Wofür trainierst du gerade?",
    ["Halbmarathon", "Marathon", "10 km", "Ohne Wettkampfziel"]
)

weekly_km = st.slider("Wie viele Kilometer läufst du aktuell pro Woche?", 0, 150, 40)

if st.button("Analyse starten"):
    if weekly_km < 20:
        st.warning("Niedriger Trainingsumfang – für ambitionierte Ziele evtl. noch ausbaufähig.")
    elif weekly_km < 60:
        st.success("Solide Basis für strukturiertes Training.")
    else:
        st.info("Hoher Trainingsumfang – Belastungssteuerung wird besonders wichtig.")

    st.write(f"Gewähltes Ziel: {goal}")
    st.write(f"Aktueller Wochenumfang: {weekly_km} km")