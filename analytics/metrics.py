import pandas as pd


def prepare_runs_dataframe(activities):
    df = pd.DataFrame(activities)

    # Nur Runs behalten
    df = df[df["sport_type"] == "Run"].copy()

    # Einheiten umrechnen
    df["distance_km"] = df["distance"] / 1000
    df["moving_time_min"] = df["moving_time"] / 60

    # Pace berechnen
    df["pace_min_per_km"] = df["moving_time_min"] / df["distance_km"]

    # Datum konvertieren
    df["start_date"] = pd.to_datetime(df["start_date"])

    return df


# -----------------------------
# Basis-Metriken
# -----------------------------
# Berechnet die Gesamtdistanz der letzten 7 Tage
def calculate_rolling_weekly_distance(df):
    last_7_days = df[df["start_date"] >= (pd.Timestamp.utcnow() - pd.Timedelta(days=7))]
    return last_7_days["distance_km"].sum()

# Berechnet die durchschnittliche Pace über alle Läufe
def calculate_average_pace(df):
    total_distance = df["distance_km"].sum()
    total_time = df["moving_time_min"].sum()

    if total_distance == 0:
        return None

    return total_time / total_distance


# -----------------------------
# Wochenmetriken
# -----------------------------
# Berechnet die wöchentlichen Kilometer
def calculate_weekly_km(df):
    df = df.copy()
    df["week"] = df["start_date"].dt.strftime("%Y-KW%V")
    weekly_km = df.groupby("week")["distance_km"].sum().reset_index()
    weekly_km.columns = ["Woche", "Kilometer"]

    return weekly_km

# Berechnet die Anzahl der Läufe pro Woche
def calculate_runs_per_week(df):
    df = df.copy()
    df["week"] = df["start_date"].dt.strftime("%Y-KW%V")
    runs_per_week = df.groupby("week").size().reset_index(name="Anzahl Läufe")
    runs_per_week.columns = ["Woche", "Anzahl Läufe"]

    return runs_per_week

# Berechnet die maximale Distanz pro Woche (Long Run)
def calculate_weekly_training_load(df):
    df = df.copy()
    df["week"] = df["start_date"].dt.strftime("%Y-KW%V")
    weekly_load = df.groupby("week")["moving_time_min"].sum().reset_index()
    weekly_load.columns = ["Woche", "Training Load"]

    return weekly_load

#  Berechnet den Long Run pro Woche (maximale Distanz)
def calculate_long_run_per_week(df):
    df = df.copy()
    df["week"] = df["start_date"].dt.strftime("%Y-KW%V")
    long_run = df.groupby("week")["distance_km"].max().reset_index()
    long_run.columns = ["Woche", "Long Run (km)"]

    return long_run


# -----------------------------
# Load-Metriken
# -----------------------------
# Berechnet die Trainingsbelastung der letzten 7 Tage
def calculate_7_day_training_load(df):
    df = df.copy()
    last_7_days = df[df["start_date"] >= (pd.Timestamp.utcnow() - pd.Timedelta(days=7))]
    training_load_7d = last_7_days["moving_time_min"].sum()

    return training_load_7d

# Berechnet die Trainingsbelastung der letzten 28 Tage
def calculate_28_day_training_load(df):
    df = df.copy()
    last_28_days = df[df["start_date"] >= (pd.Timestamp.utcnow() - pd.Timedelta(days=28))]
    training_load_28d = last_28_days["moving_time_min"].sum()

    return training_load_28d

# Berechnet die Trainingsbelastung der letzten 7 Tage im Vergleich zu den letzten 28 Tagen
def calculate_load_ratio(training_load_7d, training_load_28d):
    average_weekly_load_28d = training_load_28d / 4

    if average_weekly_load_28d == 0:
        return None

    return training_load_7d / average_weekly_load_28d

def interpret_load_ratio(load_ratio):
    if load_ratio is None:
        return {
            "status": "Keine Daten",
            "message": "Noch nicht genug Daten für eine Bewertung."
        }

    if load_ratio < 0.8:
        return {
            "status": "Niedrig",
            "message": "Deine aktuelle Belastung liegt unter deinem üblichen Niveau."
        }
    elif load_ratio <= 1.2:
        return {
            "status": "Normal",
            "message": "Deine aktuelle Belastung liegt in einem normalen Bereich."
        }
    elif load_ratio <= 1.5:
        return {
            "status": "Erhöht",
            "message": "Deine aktuelle Belastung ist höher als üblich. Achte auf Erholung."
        }
    else:
        return {
            "status": "Kritisch",
            "message": "Deine aktuelle Belastung ist deutlich höher als üblich."
        }

# Berechnet die Ramp-Rate (Veränderung der Trainingsbelastung im Vergleich zur Vorwoche)
def calculate_ramp_rate(df):
    df = df.copy()

    now = pd.Timestamp.utcnow()
    current_7d = df[df["start_date"] >= (now - pd.Timedelta(days=7))]
    previous_7d = df[
        (df["start_date"] < (now - pd.Timedelta(days=7))) &
        (df["start_date"] >= (now - pd.Timedelta(days=14)))
    ]

    current_load = current_7d["moving_time_min"].sum()
    previous_load = previous_7d["moving_time_min"].sum()

    if previous_load == 0:
        return None

    ramp_rate = (current_load - previous_load) / previous_load

    return ramp_rate


def interpret_ramp_rate(ramp_rate):
    if ramp_rate is None:
        return {
            "status": "Keine Daten",
            "message": "Noch nicht genug Daten für eine Ramp-Rate-Bewertung."
        }

    if ramp_rate < 0:
        return {
            "status": "Rückgang",
            "message": "Deine Trainingsbelastung ist im Vergleich zur Vorwoche gesunken."
        }
    elif ramp_rate <= 0.10:
        return {
            "status": "Stabil",
            "message": "Deine Belastungssteigerung liegt in einem moderaten Bereich."
        }
    elif ramp_rate <= 0.25:
        return {
            "status": "Erhöht",
            "message": "Deine Belastung ist spürbar gestiegen. Achte auf Regeneration."
        }
    else:
        return {
            "status": "Kritisch",
            "message": "Deine Belastung ist sehr stark gestiegen."
        }

# -----------------------------
# Long Run-Metriken
# -----------------------------
# Berechnet das Verhältnis von Long Run zur wöchentlichen Gesamtbelastung (Long Run Ratio)
def calculate_long_run_ratio(df):
    df = df.copy()

    last_7_days = df[df["start_date"] >= (pd.Timestamp.utcnow() - pd.Timedelta(days=7))]

    weekly_distance = last_7_days["distance_km"].sum()

    if weekly_distance == 0:
        return None

    # nur Läufe >= 8 km als Long Run zählen
    potential_long_runs = last_7_days[last_7_days["distance_km"] >= 8]

    if potential_long_runs.empty:
        return None

    long_run_distance = potential_long_runs["distance_km"].max()

    return long_run_distance / weekly_distance

def interpret_long_run_ratio(long_run_ratio):

    if long_run_ratio is None:
        return {
            "status": "Keine Daten",
            "message": "Noch nicht genug Daten für eine Bewertung."
        }

    if long_run_ratio < 0.20:
        return {
            "status": "Niedrig",
            "message": "Dein Long Run Anteil ist eher niedrig."
        }

    elif long_run_ratio <= 0.30:
        return {
            "status": "Ausgewogen",
            "message": "Dein Long Run Anteil liegt in einem guten Bereich."
        }

    elif long_run_ratio <= 0.35:
        return {
            "status": "Erhöht",
            "message": "Dein Long Run macht einen recht großen Anteil deines Wochenumfangs aus."
        }

    else:
        return {
            "status": "Sehr hoch",
            "message": "Dein Long Run Anteil ist sehr hoch im Verhältnis zum Wochenumfang."
        }