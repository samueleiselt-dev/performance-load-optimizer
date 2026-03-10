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
    calculate_weekly_km,
    calculate_runs_per_week,
    calculate_7_day_training_load,
    calculate_28_day_training_load,
    calculate_load_ratio,
    interpret_load_ratio,
    calculate_ramp_rate,
    interpret_ramp_rate,
    calculate_weekly_training_load,
    calculate_long_run_per_week,
    calculate_long_run_ratio,
    interpret_long_run_ratio
)

from utils.formatters import format_pace

load_dotenv()

st.set_page_config(page_title="Performance Load Optimizer", layout="wide")

# -----------------------------
# Grunddaten / Session State
# -----------------------------
strava_client_id = os.getenv("STRAVA_CLIENT_ID")
strava_client_secret = os.getenv("STRAVA_CLIENT_SECRET")
redirect_uri = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8501")

query_params = st.query_params
code = query_params.get("code")

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

if "activities" not in st.session_state:
    st.session_state["activities"] = None

access_token = st.session_state["access_token"]
activities = st.session_state["activities"]

# -----------------------------
# Sidebar: Strava-Verbindung
# -----------------------------
with st.sidebar:
    st.header("Strava Verbindung")

    if strava_client_id and strava_client_secret:
        st.success("Strava Konfiguration geladen")
    else:
        st.error("Strava Zugangsdaten fehlen")

    if not code and not access_token:
        if strava_client_id:
            auth_url = build_strava_auth_url(strava_client_id, redirect_uri)
            st.link_button("Mit Strava verbinden", auth_url)
        else:
            st.warning("Client ID fehlt")

    elif code and not access_token:
        st.success("Strava Code erhalten")

        if st.button("Access Token abrufen"):
            token_data = exchange_code_for_token(
                strava_client_id,
                strava_client_secret,
                code
            )

            if token_data:
                st.session_state["access_token"] = token_data.get("access_token")
                st.success("Access Token erfolgreich erhalten")
                st.rerun()
            else:
                st.error("Fehler beim Abrufen des Access Tokens")

    elif access_token and activities is None:
        st.success("Strava verbunden")

        if st.button("Aktivitäten laden"):
            loaded_activities = fetch_activities(access_token, per_page=100, max_pages=5)

            if loaded_activities is not None:
                st.session_state["activities"] = loaded_activities
                st.success("Aktivitäten erfolgreich geladen")
                st.rerun()
            else:
                st.error("Fehler beim Laden der Aktivitäten")

    elif access_token and activities is not None:
        st.success("Aktivitäten geladen")

        if st.button("Aktivitäten neu laden"):
            loaded_activities = fetch_activities(access_token, per_page=100, max_pages=5)

            if loaded_activities is not None:
                st.session_state["activities"] = loaded_activities
                st.success("Aktivitäten aktualisiert")
                st.rerun()
            else:
                st.error("Fehler beim Aktualisieren")

        if st.button("Session zurücksetzen"):
            st.session_state["access_token"] = None
            st.session_state["activities"] = None
            st.rerun()

# -----------------------------
# Hauptbereich
# -----------------------------
st.title("Performance Load Optimizer")
st.subheader("Erste Testversion")

if activities is None:
    st.info("Verbinde dich links in der Sidebar mit Strava und lade deine Aktivitäten.")
else:
    if activities:
        df = prepare_runs_dataframe(activities)

        if df.empty:
            st.warning("Es wurden keine Laufaktivitäten gefunden.")
        else:
            # Kennzahlen berechnen
            rolling_weekly_distance = calculate_rolling_weekly_distance(df)

            avg_pace = calculate_average_pace(df)
            pace_formatted = format_pace(avg_pace)

            training_load_7d = calculate_7_day_training_load(df)
            training_load_28d = calculate_28_day_training_load(df)

            load_ratio = calculate_load_ratio(training_load_7d, training_load_28d)
            load_ratio_interpretation = interpret_load_ratio(load_ratio)

            ramp_rate = calculate_ramp_rate(df)
            ramp_rate_interpretation = interpret_ramp_rate(ramp_rate)

            long_run_ratio = calculate_long_run_ratio(df)
            long_run_ratio_interpretation = interpret_long_run_ratio(long_run_ratio)

            weekly_km = calculate_weekly_km(df)
            runs_per_week = calculate_runs_per_week(df)
            weekly_training_load = calculate_weekly_training_load(df)
            long_run_per_week = calculate_long_run_per_week(df)

            columns_to_show = [
                "name",
                "sport_type",
                "distance_km",
                "moving_time_min",
                "total_elevation_gain",
                "start_date"
            ]
            existing_columns = [col for col in columns_to_show if col in df.columns]

            # Tabs
            tab_dashboard, tab_training, tab_activities, tab_test = st.tabs(
                ["Dashboard", "Training", "Aktivitäten", "Testbereich"]
            )

            # -----------------------------
            # Dashboard Tab
            # -----------------------------
            with tab_dashboard:
                st.markdown("## Dashboard")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Rolling Weekly Distance",
                        f"{rolling_weekly_distance:.1f} km"
                    )

                with col2:
                    st.metric(
                        "Average Pace",
                        f"{pace_formatted} min/km"
                    )

                with col3:
                    st.metric(
                        "7-Day Training Load",
                        f"{training_load_7d:.0f}"
                    )

                with col4:
                    st.metric(
                        "28-Day Training Load",
                        f"{training_load_28d:.0f}"
                    )

                col5, col6, col7 = st.columns(3)

                with col5:
                    if load_ratio is not None:
                        st.metric("Load Ratio", f"{load_ratio:.2f}")
                    else:
                        st.metric("Load Ratio", "-")

                with col6:
                    if ramp_rate is not None:
                        st.metric("Ramp Rate", f"{ramp_rate * 100:.1f}%")
                    else:
                        st.metric("Ramp Rate", "-")

                with col7:
                    if long_run_ratio is not None:
                        st.metric("Long Run Ratio", f"{long_run_ratio * 100:.1f}%")
                    else:
                        st.metric("Long Run Ratio", "-")

                st.markdown("### Bewertungen")
                col_left, col_right = st.columns(2)

                with col_left:
                    st.markdown("#### Load Bewertung")

                    status = load_ratio_interpretation["status"]
                    message = load_ratio_interpretation["message"]

                    if status == "Normal":
                        st.success(f"{status}: {message}")
                    elif status == "Erhöht":
                        st.warning(f"{status}: {message}")
                    elif status == "Kritisch":
                        st.error(f"{status}: {message}")
                    else:
                        st.info(f"{status}: {message}")

                with col_right:
                    st.markdown("#### Ramp-Rate Bewertung")

                    ramp_status = ramp_rate_interpretation["status"]
                    ramp_message = ramp_rate_interpretation["message"]

                    if ramp_status == "Stabil":
                        st.success(f"{ramp_status}: {ramp_message}")
                    elif ramp_status == "Erhöht":
                        st.warning(f"{ramp_status}: {ramp_message}")
                    elif ramp_status == "Kritisch":
                        st.error(f"{ramp_status}: {ramp_message}")
                    else:
                        st.info(f"{ramp_status}: {ramp_message}")


                st.markdown("### Long Run Bewertung")

                lr_status = long_run_ratio_interpretation["status"]
                lr_message = long_run_ratio_interpretation["message"]

                if lr_status == "Ausgewogen":
                    st.success(f"{lr_status}: {lr_message}")
                elif lr_status == "Erhöht":
                   st.warning(f"{lr_status}: {lr_message}")
                elif lr_status == "Sehr hoch":
                    st.error(f"{lr_status}: {lr_message}")
                else:
                    st.info(f"{lr_status}: {lr_message}")

            # -----------------------------
            # Training Tab
            # -----------------------------
            with tab_training:
                st.markdown("## Trainingsverlauf")

                st.markdown("### Wochenkilometer")
                st.bar_chart(weekly_km.set_index("Woche"))

                st.markdown("### Läufe pro Woche")
                st.bar_chart(runs_per_week.set_index("Woche"))

                st.markdown("### Weekly Training Load")
                st.bar_chart(weekly_training_load.set_index("Woche"))

                st.markdown("### Long Run pro Woche")
                st.bar_chart(long_run_per_week.set_index("Woche"))

            # -----------------------------
            # Aktivitäten Tab
            # -----------------------------
            with tab_activities:
                st.markdown("## Aktivitäten")
                st.dataframe(df[existing_columns], use_container_width=True)

            # -----------------------------
            # Testbereich Tab
            # -----------------------------
            with tab_test:
                st.markdown("## Testbereich")

                goal = st.selectbox(
                    "Wofür trainierst du gerade?",
                    ["Halbmarathon", "Marathon", "10 km", "Ohne Wettkampfziel"]
                )

                weekly_km_input = st.slider(
                    "Wie viele Kilometer läufst du aktuell pro Woche?",
                    0,
                    150,
                    40
                )

                if st.button("Analyse starten"):
                    if weekly_km_input < 20:
                        st.warning("Niedriger Trainingsumfang – für ambitionierte Ziele evtl. noch ausbaufähig.")
                    elif weekly_km_input < 60:
                        st.success("Solide Basis für strukturiertes Training.")
                    else:
                        st.info("Hoher Trainingsumfang – Belastungssteuerung wird besonders wichtig.")

                    st.write(f"Gewähltes Ziel: {goal}")
                    st.write(f"Aktueller Wochenumfang: {weekly_km_input} km")

    else:
        st.info("Keine Aktivitäten gefunden.")