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

        line = alt.Chart(chart_data["pace_at_hr_per_week"]).mark_line(
            color="purple"
        ).encode(
            x=alt.X("Woche:N", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Pace @ 150 bpm:Q",
                    title="Pace (min/km)",
                    scale=alt.Scale(reverse=True))
        )

        points = alt.Chart(chart_data["pace_at_hr_per_week"]).mark_point(
            filled=True,
            color="purple",
            size=60
        ).encode(
            x="Woche:N",
            y="Pace @ 150 bpm:Q"
        )

        trend = alt.Chart(chart_data["pace_at_hr_per_week"]).transform_regression(
            "week_order",
            "Pace @ 150 bpm"
        ).mark_line(
            color="black",
            opacity=0.6
        ).encode(
            x="week_order:Q",
            y="Pace @ 150 bpm:Q"
        )

        chart = line + points + trend

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