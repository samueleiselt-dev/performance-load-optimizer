import streamlit as st

st.set_page_config(page_title="Performance Load Optimizer", layout="wide")

st.title("Performance Load Optimizer")
st.subheader("Erste Testversion")

st.write("Die App läuft erfolgreich.")

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
