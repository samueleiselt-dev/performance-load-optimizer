import streamlit as st
from dotenv import load_dotenv
import os

from services.strava_api import (
    build_strava_auth_url,
    exchange_code_for_token,
    fetch_activities
)

from analytics.metrics import (
    prepare_runs_dataframe,
    calculate_rolling_weekly_distance,
    calculate_average_pace,
    calculate_weekly_km
)

from utils.formatters import format_pace

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
    auth_url = build_strava_auth_url(strava_client_id, redirect_uri)

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
        token_data = exchange_code_for_token(strava_client_id, strava_client_secret, code)

        if token_data:
            access_token = token_data.get("access_token")
            st.session_state["access_token"] = access_token
            st.success("Access Token erfolgreich erhalten.")
        else:
            st.error("Fehler beim Abrufen des Access Tokens.")

if "access_token" in st.session_state:
    access_token = st.session_state["access_token"]

st.markdown("### Strava-Aktivitäten abrufen")

if access_token:
    if st.button("Meine Aktivitäten laden"):
        activities = fetch_activities(access_token, per_page=50, page=1)

        if activities is not None:
            if activities:
                df = prepare_runs_dataframe(activities)

                rolling_weekly_distance = calculate_rolling_weekly_distance(df)

                avg_pace = calculate_average_pace(df)
                pace_formatted = format_pace(avg_pace)

                columns_to_show = [
                    "name",
                    "sport_type",
                    "distance_km",
                    "moving_time_min",
                    "total_elevation_gain",
                    "start_date"
                ]

                existing_columns = [col for col in columns_to_show if col in df.columns]

                st.success("Aktivitäten erfolgreich geladen.")
                st.metric("Rolling Weekly Distance (letzte 7 Tage)", f"{rolling_weekly_distance:.1f} km")
                st.metric("Average Pace", f"{pace_formatted} min/km")

                st.markdown("### Wochenkilometer")
                weekly_km = calculate_weekly_km(df)
                st.bar_chart(weekly_km.set_index("Woche"))

                st.markdown("### Aktivitäten")
                st.dataframe(df[existing_columns])

            else:
                st.info("Keine Aktivitäten gefunden.")
        else:
            st.error("Fehler beim Laden der Aktivitäten.")

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