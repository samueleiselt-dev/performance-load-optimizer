import streamlit as st
import altair as alt


def render_status_box(status, message):
    if status in ["Normal", "Stabil", "Ausgewogen", "Gut", "Sehr hoch"]:
        st.success(f"{status}: {message}")
    elif status in ["Erhöht"]:
        st.warning(f"{status}: {message}")
    elif status in ["Kritisch"]:
        st.error(f"{status}: {message}")
    else:
        st.info(f"{status}: {message}")


# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

def render_dashboard_tab(metrics):

    st.markdown("## Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Rolling Weekly Distance",
            f"{metrics['rolling_weekly_distance']:.1f} km"
        )

    with col2:
        st.metric(
            "Weekly Training Time",
            metrics["weekly_training_time_formatted"]
        )

    with col3:
        st.metric(
            "Average Pace",
            f"{metrics['pace_formatted']} min/km"
        )

    with col4:
        if metrics["average_run_distance"] is not None:
            st.metric(
                "Average Run Distance",
                f"{metrics['average_run_distance']:.1f} km"
            )
        else:
            st.metric("Average Run Distance", "-")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric("Consistency Score", f"{metrics['consistency_score']:.0f}%")

    with col6:
        st.metric("7-Day Training Load", f"{metrics['training_load_7d']:.0f}")

    with col7:
        st.metric("28-Day Training Load", f"{metrics['training_load_28d']:.0f}")

    with col8:
        if metrics["load_ratio"] is not None:
            st.metric("Load Ratio", f"{metrics['load_ratio']:.2f}")
        else:
            st.metric("Load Ratio", "-")

    col9, col10, col11, col12 = st.columns(4)

    with col9:
        if metrics["ramp_rate"] is not None:
            st.metric("Ramp Rate", f"{metrics['ramp_rate']*100:.1f}%")
        else:
            st.metric("Ramp Rate", "-")

    with col10:
        if metrics["long_run_ratio"] is not None:
            st.metric("Long Run Ratio", f"{metrics['long_run_ratio']*100:.1f}%")
        else:
            st.metric("Long Run Ratio", "-")

    with col11:
        if metrics["average_heart_rate"] is not None:
            st.metric("Average HR", f"{metrics['average_heart_rate']:.0f} bpm")
        else:
            st.metric("Average HR", "-")

    with col12:
        if metrics["max_heart_rate"] is not None:
            st.metric("Max HR", f"{metrics['max_heart_rate']:.0f} bpm")
        else:
            st.metric("Max HR", "-")

    col13, col14 = st.columns(2)

    with col13:
        if metrics["efficiency_score"] is not None:
            st.metric("Running Efficiency", f"{metrics['efficiency_score']:.3f}")
        else:
            st.metric("Running Efficiency", "-")

    with col14:
        if metrics["efficiency_baseline"] is not None:
            st.metric(
                "Pace @150 bpm",
                f"{metrics['efficiency_baseline_formatted']} min/km"
            )
        else:
            st.metric("Pace @150 bpm", "-")

    st.markdown("### Bewertungen")

    col_left, col_right = st.columns(2)

    with col_left:

        st.markdown("#### Load Bewertung")

        render_status_box(
            metrics["load_ratio_interpretation"]["status"],
            metrics["load_ratio_interpretation"]["message"]
        )

        st.markdown("#### Long Run Bewertung")

        render_status_box(
            metrics["long_run_ratio_interpretation"]["status"],
            metrics["long_run_ratio_interpretation"]["message"]
        )

    with col_right:

        st.markdown("#### Ramp Rate Bewertung")

        render_status_box(
            metrics["ramp_rate_interpretation"]["status"],
            metrics["ramp_rate_interpretation"]["message"]
        )

        st.markdown("#### Konsistenz Bewertung")

        render_status_box(
            metrics["consistency_score_interpretation"]["status"],
            metrics["consistency_score_interpretation"]["message"]
        )


# -------------------------------------------------
# TRAINING TAB
# -------------------------------------------------

def render_training_tab(chart_data):

    st.markdown("## Training")

    # -------------------------
    # Daily Training Load
    # -------------------------

    st.markdown("### Daily Training Load")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟦 **Daily Load**")
    with col2:
        st.markdown("🟧 **7-Day Load**")
    with col3:
        st.markdown("🟥 **28-Day Load**")

    if not chart_data["daily_training_load"].empty:

        base = alt.Chart(chart_data["daily_training_load"])

        bars = base.mark_bar(
            opacity=0.5,
            color="#58a3cb"
        ).encode(
            x=alt.X("Datum:T", title="Datum"),
            y=alt.Y("Daily Training Load:Q", title="Training Load (min)"),
            tooltip=[
                alt.Tooltip("Datum:T", title="Datum"),
                alt.Tooltip("Daily Training Load:Q", title="Daily Load", format=".1f"),
                alt.Tooltip("Load 7d:Q", title="7d Durchschnitt", format=".1f"),
                alt.Tooltip("Load 28d:Q", title="28d Durchschnitt", format=".1f")
            ]
        )

        line_7d = base.mark_line(
            color="#ff7f0e",
            size=2.5
        ).encode(
            x=alt.X("Datum:T"),
            y=alt.Y("Load 7d:Q", title="Training Load (min)"),
            tooltip=[
                alt.Tooltip("Datum:T", title="Datum"),
                alt.Tooltip("Load 7d:Q", title="7d Durchschnitt", format=".1f")
            ]
        )

        line_28d = base.mark_line(
            color="#d62728",
            size=2,
            opacity=0.9
        ).encode(
            x=alt.X("Datum:T"),
            y=alt.Y("Load 28d:Q", title="Training Load (min)"),
            tooltip=[
                alt.Tooltip("Datum:T", title="Datum"),
                alt.Tooltip("Load 28d:Q", title="28d Durchschnitt", format=".1f")
            ]
        )

        chart = alt.layer(bars, line_7d, line_28d).resolve_scale(
            y="shared"
        )

        st.altair_chart(chart, use_container_width=True)

    else:
        st.info("Keine Daten für Daily Training Load vorhanden.")

    with st.expander("Was zeigt dieser Chart?"):
        st.markdown("""
        **Daily Training Load**
        - Die Balken zeigen die Trainingsbelastung pro Tag (Trainingszeit in Minuten).

        **7-Day Load**
        - Durchschnittliche tägliche Belastung der letzten 7 Tage.
        - Reagiert relativ schnell auf Trainingsänderungen.

        **28-Day Load**
        - Durchschnittliche tägliche Belastung der letzten 28 Tage.
        - Zeigt dein längerfristiges Trainingsniveau.

        **Interpretation**
        - Wenn die **7-Day Load über der 28-Day Load liegt**, steigt deine aktuelle Trainingsbelastung.
        - Wenn sie darunter liegt, befindest du dich eher in einer Erholungsphase.
        """)
    
    # -------------------------
    # Fitness / Fatigue / Form
    # -------------------------

    st.markdown("### Fitness / Fatigue / Form")

    if not chart_data["fitness_fatigue_form"].empty:

        fff_data = chart_data["fitness_fatigue_form"]
        latest = fff_data.iloc[-1]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Fitness", f"{latest['Fitness']:.1f}")

        with col2:
            st.metric("Fatigue", f"{latest['Fatigue']:.1f}")

        with col3:
            st.metric("Form", f"{latest['Form']:.1f}")
        

        form_value = latest["Form"]

        if form_value > 10:
            st.success("Status: Sehr frisch – gute Bedingungen für harte Einheiten oder Wettkampf.")

        elif form_value > 0:
            st.info("Status: Frisch – du bist gut erholt.")

        elif form_value > -10:
            st.warning("Status: Moderat belastet – normale Trainingsbelastung.")

        elif form_value > -20:
            st.warning("Status: Ermüdet – achte auf Erholung.")

        else:
            st.error("Status: Stark belastet – zusätzliche Erholung könnte sinnvoll sein.")


        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("🟢 **Fitness**")

        with col2:
            st.markdown("🔴 **Fatigue**")

        with col3:
            st.markdown("🟣 **Form**")

        base = alt.Chart(fff_data).encode(
            x=alt.X("Datum:T", title="Datum")
        )

        fitness_line = base.mark_line(
            color="#2ca02c",
            size=2.5
        ).encode(
            y=alt.Y("Fitness:Q", title="Load Score"),
            tooltip=[
                alt.Tooltip("Datum:T", title="Datum"),
                alt.Tooltip("Fitness:Q", title="Fitness", format=".1f")
            ]
        )

        fatigue_line = base.mark_line(
            color="#d62728",
            size=2.5
        ).encode(
            y=alt.Y("Fatigue:Q", title="Load Score"),
            tooltip=[
                alt.Tooltip("Datum:T", title="Datum"),
                alt.Tooltip("Fatigue:Q", title="Fatigue", format=".1f")
            ]
        )

        form_line = base.mark_line(
            color="#9467bd",
            size=2,
            opacity=0.9
        ).encode(
            y=alt.Y("Form:Q", title="Load Score"),
            tooltip=[
                alt.Tooltip("Datum:T", title="Datum"),
                alt.Tooltip("Form:Q", title="Form", format=".1f")
            ]
        )

        forecast_data = chart_data["fitness_fatigue_form_forecast"]

        race_window = forecast_data[
            (forecast_data["Form"] >= 5) &
            (forecast_data["Form"] <= 15)
        ].copy()

        forecast_base = alt.Chart(forecast_data).encode(
            x="Datum:T"
        )

        fitness_forecast = forecast_base.mark_line(
            strokeDash=[5,5],
            color="#2ca02c"
        ).encode(
            y="Fitness:Q"
        )

        fatigue_forecast = forecast_base.mark_line(
            strokeDash=[5,5],
            color="#d62728"
        ).encode(
            y="Fatigue:Q"
        )

        form_forecast = forecast_base.mark_line(
            strokeDash=[5,5],
            color="#9467bd"
        ).encode(
            y="Form:Q"
        )

        chart = alt.layer(
            fitness_line,
            fatigue_line,
            form_line,
            fitness_forecast,
            fatigue_forecast,
            form_forecast
        ).resolve_scale(
            y="shared"
        )

        if not race_window.empty:
            window_start = race_window.iloc[0]["Datum"]
            window_end = race_window.iloc[-1]["Datum"]

            min_form = race_window["Form"].min()
            max_form = race_window["Form"].max()

            days_until_start = (window_start - fff_data["Datum"].iloc[-1]).days

            st.success(
                f"🏁 **Race Readiness Window startet in {days_until_start} Tagen** "
                f"({window_start.strftime('%d.%m')} bis {window_end.strftime('%d.%m')}, "
                f"Form: {min_form:.1f} bis {max_form:.1f})"
            )
        else:
            best_row = forecast_data.loc[forecast_data["Form"].idxmax()]
            best_date = best_row["Datum"]
            best_form = best_row["Form"]
            days_until_best = (best_date - fff_data["Datum"].iloc[-1]).days

            st.info(
                f"Kein klares Race Window im Forecast. "
                f"Beste prognostizierte Form in {days_until_best} Tagen: {best_form:.1f}"
            )

        st.caption(
            "Das Race Window basiert auf der Form-Prognose. "
            "Aktuell wird ein Bereich von +5 bis +15 als günstiges Wettkampffenster interpretiert, "
            "wenn in den nächsten Tagen kein weiteres Training stattfindet."
            )

        st.altair_chart(chart, use_container_width=True)

        with st.expander("Was zeigt dieser Chart?"):
            st.markdown("""
            **Fitness**
            - Die grüne Linie zeigt dein längerfristiges Trainingsniveau.
            - Sie steigt langsamer an und fällt langsamer ab.

            **Fatigue**
            - Die rote Linie zeigt deine kurzfristige Ermüdung.
            - Sie reagiert schneller auf harte oder umfangreiche Trainingstage.

            **Form**
            - Die violette Linie ist definiert als: **Fitness - Fatigue**
            - Positive Werte sprechen eher für Frische.
            - Negative Werte sprechen eher für akute Belastung oder Müdigkeit.

            **Interpretation**
            - Wenn **Fatigue über Fitness liegt**, bist du aktuell eher belastet.
            - Wenn **Fitness stabil steigt**, baust du langfristig Trainingsbasis auf.
            - Wenn **Form deutlich negativ wird**, kann das auf hohe aktuelle Belastung hindeuten.
            """)

    else:
        st.info("Keine Daten für Fitness / Fatigue / Form vorhanden.")



    # -------------------------
    # Trainingsvolumen
    # -------------------------

    st.markdown("### Wochenkilometer")
    st.bar_chart(chart_data["weekly_km"].set_index("Woche"))

    st.markdown("### Läufe pro Woche")
    st.bar_chart(chart_data["runs_per_week"].set_index("Woche"))

    st.markdown("### Weekly Training Load")
    st.bar_chart(chart_data["weekly_training_load"].set_index("Woche"))

    st.markdown("### Long Run pro Woche")
    st.bar_chart(chart_data["long_run_per_week"].set_index("Woche"))

    # -------------------------
    # Herzfrequenz
    # -------------------------

    st.markdown("### Average HR pro Woche")

    if not chart_data["average_hr_per_week"].empty:
        st.bar_chart(chart_data["average_hr_per_week"].set_index("Woche"))
    else:
        st.info("Keine Herzfrequenzdaten vorhanden.")

    # -------------------------
    # Pace vs HR
    # -------------------------

    st.markdown("### Pace vs Average HR")

    if not chart_data["pace_vs_hr_data"].empty:

        scatter = alt.Chart(chart_data["pace_vs_hr_data"]).mark_point(
            filled=True,
            opacity=0.75
        ).encode(
            x=alt.X("avg_hr:Q", title="Average HR (bpm)"),
            y=alt.Y("pace_min_per_km:Q",
                    title="Pace (min/km)",
                    scale=alt.Scale(reverse=True)),
            color=alt.Color(
                "start_date:T",
                scale=alt.Scale(range=["#d9d9d9", "#ff3b30"]),
                title="Datum"
            ),
            size=alt.Size("distance_km:Q", title="Distance (km)"),
            tooltip=[
                alt.Tooltip("date:N", title="Datum"),
                alt.Tooltip("name:N", title="Aktivität"),
                alt.Tooltip("distance_km:Q", title="Distanz", format=".1f"),
                alt.Tooltip("pace_min_per_km:Q", title="Pace", format=".2f"),
                alt.Tooltip("avg_hr:Q", title="Avg HR", format=".0f")
            ]
        ).interactive()

        trend = alt.Chart(chart_data["pace_vs_hr_data"]).transform_regression(
            "avg_hr",
            "pace_min_per_km"
        ).mark_line(
            color="black",
            size=2,
            opacity=0.7
        ).encode(
            x="avg_hr:Q",
            y=alt.Y("pace_min_per_km:Q", scale=alt.Scale(reverse=True))
        )

        chart = scatter + trend

        st.altair_chart(chart, use_container_width=True)

    else:
        st.info("Keine Daten für Pace vs HR.")

    # -------------------------
    # Efficiency Trend
    # -------------------------

    st.markdown("### Running Efficiency pro Woche")

    if not chart_data["efficiency_per_week"].empty:

        line = alt.Chart(chart_data["efficiency_per_week"]).mark_line(
            color="green"
        ).encode(
            x=alt.X("Woche:N", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Efficiency:Q", scale=alt.Scale(zero=False))
        )

        points = alt.Chart(chart_data["efficiency_per_week"]).mark_point(
            filled=True,
            color="green",
            size=60
        ).encode(
            x="Woche:N",
            y="Efficiency:Q"
        )

        trend = alt.Chart(chart_data["efficiency_per_week"]).transform_regression(
            "week_order",
            "Efficiency"
        ).mark_line(
            color="black",
            opacity=0.6
        ).encode(
            x="week_order:Q",
            y="Efficiency:Q"
        )

        chart = line + points + trend

        st.altair_chart(chart, use_container_width=True)

    else:
        st.info("Nicht genügend Daten für Efficiency Trend.")

    # -------------------------
    # Pace @150 bpm
    # -------------------------

    st.markdown("### Pace @150 bpm pro Woche")

    if not chart_data["pace_at_hr_per_week"].empty:

        base = alt.Chart(chart_data["pace_at_hr_per_week"]).encode(
            x=alt.X("Woche:N", axis=alt.Axis(labelAngle=-45))
        )

        line = base.mark_line(
            color="purple"
        ).encode(
            y=alt.Y(
                "Pace @ 150 bpm:Q",
                title="Pace (min/km)",
                scale=alt.Scale(reverse=True)
            ),
            tooltip=[
                alt.Tooltip("Woche:N", title="Woche"),
                alt.Tooltip("pace_formatted:N", title="Pace @150")
            ]
        )

        points = base.mark_point(
            filled=True,
            color="purple",
            size=60
        ).encode(
            y="Pace @ 150 bpm:Q",
            tooltip=[
                alt.Tooltip("Woche:N", title="Woche"),
                alt.Tooltip("pace_formatted:N", title="Pace @150")
            ]
        )

        chart = line + points

        st.altair_chart(chart, use_container_width=True)

    else:
        st.info("Nicht genügend Daten für Pace @150 Trend.")


# -------------------------------------------------
# ACTIVITIES TAB
# -------------------------------------------------

def render_activities_tab(df, columns):

    st.markdown("## Aktivitäten")

    st.dataframe(
        df[columns],
        use_container_width=True
    )


# -------------------------------------------------
# TEST TAB
# -------------------------------------------------

def render_test_tab():

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
            st.warning(
                "Niedriger Trainingsumfang – für ambitionierte Ziele evtl. noch ausbaufähig."
            )

        elif weekly_km_input < 60:
            st.success(
                "Solide Basis für strukturiertes Training."
            )

        else:
            st.info(
                "Hoher Trainingsumfang – Belastungssteuerung wird besonders wichtig."
            )

        st.write(f"Gewähltes Ziel: {goal}")
        st.write(f"Aktueller Wochenumfang: {weekly_km_input} km")