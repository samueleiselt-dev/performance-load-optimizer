import os
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

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
    interpret_long_run_ratio,
    calculate_consistency_score,
    interpret_consistency_score,
    calculate_average_run_distance,
    calculate_weekly_training_time,
    calculate_average_heart_rate,
    calculate_max_heart_rate,
    calculate_average_hr_per_week,
    prepare_pace_vs_hr_data,
    calculate_efficiency_score,
    calculate_efficiency_per_week,
    calculate_efficiency_baseline,
    calculate_pace_at_hr_per_week,
    calculate_daily_training_load,
    calculate_fitness_fatigue_form,
    forecast_fitness_fatigue_form,
)

from utils.formatters import format_pace, format_minutes_to_hours

from ui.renderers import (
    render_dashboard_tab,
    render_training_tab,
    render_activities_tab,
    render_test_tab
)

load_dotenv()

st.set_page_config(page_title="Performance Load Optimizer", layout="wide")


def initialize_session_state():
    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None

    if "activities" not in st.session_state:
        st.session_state["activities"] = None

def filter_dataframe_by_time_range(df, selected_range):
    if df.empty:
        return df

    latest_date = df["start_date"].max()

    if selected_range == "Letzte 4 Wochen":
        cutoff_date = latest_date - pd.Timedelta(weeks=4)
    elif selected_range == "Letzte 3 Monate":
        cutoff_date = latest_date - pd.Timedelta(days=90)
    elif selected_range == "Letzte 6 Monate":
        cutoff_date = latest_date - pd.Timedelta(days=180)
    elif selected_range == "Letzte 12 Monate":
        cutoff_date = latest_date - pd.Timedelta(days=365)
    else:
        return df

    return df[df["start_date"] >= cutoff_date].copy()


def render_sidebar(strava_client_id, strava_client_secret, redirect_uri, code, access_token, activities):
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


def calculate_metrics(df):
    rolling_weekly_distance = calculate_rolling_weekly_distance(df)

    weekly_training_time = calculate_weekly_training_time(df)
    weekly_training_time_formatted = format_minutes_to_hours(weekly_training_time)

    avg_pace = calculate_average_pace(df)
    pace_formatted = format_pace(avg_pace)

    average_run_distance = calculate_average_run_distance(df)

    training_load_7d = calculate_7_day_training_load(df)
    training_load_28d = calculate_28_day_training_load(df)

    load_ratio = calculate_load_ratio(training_load_7d, training_load_28d)
    load_ratio_interpretation = interpret_load_ratio(load_ratio)

    ramp_rate = calculate_ramp_rate(df)
    ramp_rate_interpretation = interpret_ramp_rate(ramp_rate)

    long_run_ratio = calculate_long_run_ratio(df)
    long_run_ratio_interpretation = interpret_long_run_ratio(long_run_ratio)

    consistency_score = calculate_consistency_score(df)
    consistency_score_interpretation = interpret_consistency_score(consistency_score)

    average_heart_rate = calculate_average_heart_rate(df)
    max_heart_rate = calculate_max_heart_rate(df)

    raw_efficiency_score = calculate_efficiency_score(df)
    efficiency_score = raw_efficiency_score * 1000 if raw_efficiency_score is not None else None

    efficiency_baseline = calculate_efficiency_baseline(df, baseline_hr=150)
    efficiency_baseline_formatted = format_pace(efficiency_baseline)

    return {
        "rolling_weekly_distance": rolling_weekly_distance,
        "weekly_training_time": weekly_training_time,
        "weekly_training_time_formatted": weekly_training_time_formatted,
        "avg_pace": avg_pace,
        "pace_formatted": pace_formatted,
        "average_run_distance": average_run_distance,
        "training_load_7d": training_load_7d,
        "training_load_28d": training_load_28d,
        "load_ratio": load_ratio,
        "load_ratio_interpretation": load_ratio_interpretation,
        "ramp_rate": ramp_rate,
        "ramp_rate_interpretation": ramp_rate_interpretation,
        "long_run_ratio": long_run_ratio,
        "long_run_ratio_interpretation": long_run_ratio_interpretation,
        "consistency_score": consistency_score,
        "consistency_score_interpretation": consistency_score_interpretation,
        "average_heart_rate": average_heart_rate,
        "max_heart_rate": max_heart_rate,
        "efficiency_score": efficiency_score,
        "efficiency_baseline": efficiency_baseline,
        "efficiency_baseline_formatted": efficiency_baseline_formatted,
    }


def calculate_chart_data(df):
    return {
        "weekly_km": calculate_weekly_km(df),
        "runs_per_week": calculate_runs_per_week(df),
        "weekly_training_load": calculate_weekly_training_load(df),
        "long_run_per_week": calculate_long_run_per_week(df),
        "average_hr_per_week": calculate_average_hr_per_week(df),
        "pace_vs_hr_data": prepare_pace_vs_hr_data(df),
        "efficiency_per_week": calculate_efficiency_per_week(df),
        "pace_at_hr_per_week": calculate_pace_at_hr_per_week(df, baseline_hr=150),
        "daily_training_load": calculate_daily_training_load(df),
        "fitness_fatigue_form": calculate_fitness_fatigue_form(df),
        "fitness_fatigue_form_forecast": forecast_fitness_fatigue_form(df),
    }

def calculate_analysis_summary(df, selected_range):
    total_runs = len(df)
    total_distance = df["distance_km"].sum()
    total_minutes = df["moving_time_min"].sum()

    return {
        "selected_range": selected_range,
        "total_runs": total_runs,
        "total_distance": total_distance,
        "total_minutes": total_minutes,
        "total_time_formatted": format_minutes_to_hours(total_minutes)
    }

def main():
    initialize_session_state()

    strava_client_id = os.getenv("STRAVA_CLIENT_ID")
    strava_client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    redirect_uri = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8501")

    query_params = st.query_params
    code = query_params.get("code")

    access_token = st.session_state["access_token"]
    activities = st.session_state["activities"]

    render_sidebar(
        strava_client_id,
        strava_client_secret,
        redirect_uri,
        code,
        access_token,
        activities
    )

    st.title("Performance Load Optimizer")
    st.subheader("Erste Testversion")

    if activities is None:
        st.info("Verbinde dich links in der Sidebar mit Strava und lade deine Aktivitäten.")
        return

    if not activities:
        st.info("Keine Aktivitäten gefunden.")
        return

    df = prepare_runs_dataframe(activities)

    if df.empty:
        st.warning("Es wurden keine Laufaktivitäten gefunden.")
        return
    
    st.markdown("### Analysezeitraum")

    col_filter, col_empty = st.columns([1, 3])
    with col_filter:
        selected_range = st.selectbox(
            "Wähle den Zeitraum für die Analyse",
        [
                "Letzte 4 Wochen",
                "Letzte 3 Monate",
                "Letzte 6 Monate",
                "Letzte 12 Monate",
                "Alle Aktivitäten"
            ],
            index=1
        )

    filtered_df = filter_dataframe_by_time_range(df, selected_range)

    if filtered_df.empty:
        st.warning("Für den gewählten Zeitraum sind keine Laufaktivitäten vorhanden.")
        return

    metrics = calculate_metrics(filtered_df)
    chart_data = calculate_chart_data(filtered_df)
    analysis_summary = calculate_analysis_summary(filtered_df, selected_range)

    columns_to_show = [
        "name",
        "sport_type",
        "distance_km",
        "moving_time_min",
        "total_elevation_gain",
        "start_date"
    ]
    existing_columns = [col for col in columns_to_show if col in df.columns]

    st.markdown("### Analyse-Zusammenfassung")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Zeitraum", analysis_summary["selected_range"])

    with col2:
        st.metric("Läufe", analysis_summary["total_runs"])

    with col3:
        st.metric("Kilometer", f"{analysis_summary['total_distance']:.1f} km")

    with col4:
        st.metric("Trainingszeit", analysis_summary["total_time_formatted"])

    tab_dashboard, tab_training, tab_activities, tab_test = st.tabs(
        ["Dashboard", "Training", "Aktivitäten", "Testbereich"]
    )

    with tab_dashboard:
        render_dashboard_tab(metrics)

    with tab_training:
        render_training_tab(chart_data)

    with tab_activities:
        render_activities_tab(df, existing_columns)

    with tab_test:
        render_test_tab()


if __name__ == "__main__":
    main()