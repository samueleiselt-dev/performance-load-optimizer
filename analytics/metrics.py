import pandas as pd
import numpy as np

def get_reference_date(df):
    if df.empty:
        return None

    return df["start_date"].max()

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

    # Herzfrequenz-Spalten übernehmen, falls vorhanden
    if "average_heartrate" in df.columns:
        df["avg_hr"] = df["average_heartrate"]

    if "max_heartrate" in df.columns:
        df["max_hr"] = df["max_heartrate"]

    df = df.sort_values("start_date").reset_index(drop=True)

    return df


# -----------------------------
# Basis-Metriken
# -----------------------------
# Berechnet die Gesamtstrecke der letzten 7 Tage
def calculate_rolling_weekly_distance(df):
    reference_date = get_reference_date(df)

    if reference_date is None:
        return 0

    last_7_days = df[df["start_date"] >= (reference_date - pd.Timedelta(days=7))]
    return last_7_days["distance_km"].sum()

# Berechnet die durchschnittliche Pace über alle Läufe
def calculate_average_pace(df):
    total_distance = df["distance_km"].sum()
    total_time = df["moving_time_min"].sum()

    if total_distance == 0:
        return None

    return total_time / total_distance

# Berechnet die Gesamtzeit der letzten 7 Tage
def calculate_weekly_training_time(df):
    df = df.copy()

    reference_date = get_reference_date(df)

    if reference_date is None:
        return 0

    last_7_days = df[df["start_date"] >= (reference_date - pd.Timedelta(days=7))]

    return last_7_days["moving_time_min"].sum()


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

    reference_date = get_reference_date(df)

    if reference_date is None:
        return 0

    last_7_days = df[df["start_date"] >= (reference_date - pd.Timedelta(days=7))]
    training_load_7d = last_7_days["moving_time_min"].sum()

    return training_load_7d

# Berechnet die tägliche Trainingsbelastung (Summe der Trainingszeit pro Tag)
def calculate_daily_training_load(df):
    df = df.copy()

    if df.empty:
        return pd.DataFrame()

    # Datum extrahieren
    df["date"] = df["start_date"].dt.date

    # Tageslast berechnen
    daily_load = df.groupby("date")["moving_time_min"].sum().reset_index()
    daily_load.columns = ["Datum", "Daily Training Load"]

    daily_load["Datum"] = pd.to_datetime(daily_load["Datum"])

    # vollständige Datumsreihe erzeugen
    full_date_range = pd.date_range(
        start=daily_load["Datum"].min(),
        end=daily_load["Datum"].max()
    )

    daily_load = daily_load.set_index("Datum").reindex(full_date_range)

    daily_load["Daily Training Load"] = daily_load["Daily Training Load"].fillna(0)

    daily_load = daily_load.reset_index()
    daily_load.columns = ["Datum", "Daily Training Load"]

    # Rolling Load berechnen
    daily_load["Load 7d"] = daily_load["Daily Training Load"].rolling(window=7).mean()
    daily_load["Load 28d"] = daily_load["Daily Training Load"].rolling(window=28).mean()

    return daily_load

# Berechnet die Trainingsbelastung der letzten 28 Tage
def calculate_28_day_training_load(df):
    df = df.copy()

    reference_date = get_reference_date(df)

    if reference_date is None:
        return 0

    last_28_days = df[df["start_date"] >= (reference_date - pd.Timedelta(days=28))]
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

    reference_date = get_reference_date(df)

    if reference_date is None:
        return None

    current_7d = df[df["start_date"] >= (reference_date - pd.Timedelta(days=7))]
    previous_7d = df[
        (df["start_date"] < (reference_date - pd.Timedelta(days=7))) &
        (df["start_date"] >= (reference_date - pd.Timedelta(days=14)))
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
    
def calculate_fitness_fatigue_form(df):
    daily_load = calculate_daily_training_load(df)

    if daily_load.empty:
        return pd.DataFrame()

    result = daily_load.copy()

    result["Fatigue"] = result["Daily Training Load"].ewm(span=7, adjust=False).mean()
    result["Fitness"] = result["Daily Training Load"].ewm(span=28, adjust=False).mean()
    result["Form"] = result["Fitness"] - result["Fatigue"]

    return result

# -----------------------------
# Long Run-Metriken
# -----------------------------
# Berechnet das Verhältnis von Long Run zur wöchentlichen Gesamtbelastung (Long Run Ratio)
def calculate_long_run_ratio(df):
    df = df.copy()

    reference_date = get_reference_date(df)

    if reference_date is None:
        return None

    last_7_days = df[df["start_date"] >= (reference_date - pd.Timedelta(days=7))]

    weekly_distance = last_7_days["distance_km"].sum()

    if weekly_distance == 0:
        return None

    potential_long_runs = last_7_days[last_7_days["distance_km"] >= 8]

    if potential_long_runs.empty:
        return None

    long_run_distance = potential_long_runs["distance_km"].max()

    return long_run_distance / weekly_distance

    # nur Läufe >= 8 km als Long Run zählen
    potential_long_runs = last_7_days[last_7_days["distance_km"] >= 10]

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

# -----------------------------
# Konsistenz-Metriken
# -----------------------------
def calculate_consistency_score(df):
    df = df.copy()

    reference_date = get_reference_date(df)

    if reference_date is None:
        return 0

    last_7_days = df[df["start_date"] >= (reference_date - pd.Timedelta(days=7))]

    if last_7_days.empty:
        return 0

    unique_run_days = last_7_days["start_date"].dt.date.nunique()

    return (unique_run_days / 7) * 100

def interpret_consistency_score(consistency_score):
    if consistency_score == 0:
        return {
            "status": "Keine Aktivität",
            "message": "In den letzten 7 Tagen wurden keine Läufe erfasst."
        }

    if consistency_score < 30:
        return {
            "status": "Niedrig",
            "message": "Deine Trainingsfrequenz ist aktuell eher niedrig."
        }
    elif consistency_score < 60:
        return {
            "status": "Solide",
            "message": "Du trainierst bereits einigermaßen regelmäßig."
        }
    elif consistency_score < 85:
        return {
            "status": "Gut",
            "message": "Deine Trainingsfrequenz ist konstant und stabil."
        }
    else:
        return {
            "status": "Sehr hoch",
            "message": "Du trainierst an fast jedem Tag der Woche."
        }
    
# -----------------------------
# Distanz-Metriken
# -----------------------------
def calculate_average_run_distance(df):
    df = df.copy()

    if df.empty:
        return None

    total_distance = df["distance_km"].sum()
    total_runs = len(df)

    if total_runs == 0:
        return None

    return total_distance / total_runs


# -----------------------------
# Herzfrequenz-Metriken
# -----------------------------
# Berechnet die maximale Herzfrequenz über alle Läufe
def calculate_average_heart_rate(df):
    if "avg_hr" not in df.columns:
        return None

    hr_data = df["avg_hr"].dropna()

    if hr_data.empty:
        return None

    return hr_data.mean()

# Berechnet die maximale Herzfrequenz über alle Läufe
def calculate_max_heart_rate(df):
    if "max_hr" not in df.columns:
        return None

    hr_data = df["max_hr"].dropna()

    if hr_data.empty:
        return None

    return hr_data.max()

# Berechnet die durchschnittliche Herzfrequenz pro Woche
def calculate_average_hr_per_week(df):
    df = df.copy()

    if "avg_hr" not in df.columns:
        return pd.DataFrame()

    hr_df = df.dropna(subset=["avg_hr"]).copy()

    if hr_df.empty:
        return pd.DataFrame()

    hr_df["week"] = hr_df["start_date"].dt.strftime("%Y-KW%V")
    weekly_avg_hr = hr_df.groupby("week")["avg_hr"].mean().reset_index()
    weekly_avg_hr.columns = ["Woche", "Average HR"]

    return weekly_avg_hr

# Bereitet die Daten für die Pace vs. Herzfrequenz-Analyse vor
def prepare_pace_vs_hr_data(df):
    df = df.copy()

    required_columns = ["pace_min_per_km", "avg_hr", "name", "distance_km", "start_date"]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return pd.DataFrame()

    scatter_df = df.dropna(subset=["pace_min_per_km", "avg_hr"]).copy()

    if scatter_df.empty:
        return pd.DataFrame()

    scatter_df["date"] = scatter_df["start_date"].dt.strftime("%Y-%m-%d")

    return scatter_df[["start_date", "date", "name", "distance_km", "pace_min_per_km", "avg_hr"]]

# Berechnet die geschätzte Pace bei einer Herzfrequenz von 150 bpm pro Woche (Pace @ 150 bpm)
def calculate_pace_at_hr_per_week(df, baseline_hr=150):
    df = df.copy()

    required_columns = ["avg_hr", "pace_min_per_km", "start_date"]

    # Prüfen ob notwendige Spalten vorhanden sind
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return pd.DataFrame()

    # Nur Läufe mit Pace und HR verwenden
    valid_runs = df.dropna(subset=["avg_hr", "pace_min_per_km"]).copy()

    if valid_runs.empty:
        return pd.DataFrame()

    # Kalenderwoche berechnen
    valid_runs["week"] = valid_runs["start_date"].dt.strftime("%Y-KW%V")

    weekly_rows = []

    grouped = valid_runs.groupby("week")

    for week, group in grouped:

        # Mindestens zwei Läufe nötig für Regression
        if len(group) < 3:
            continue

        # HR-Range prüfen
        if group["avg_hr"].max() - group["avg_hr"].min() < 5:
            continue

        x = group["avg_hr"]
        y = group["pace_min_per_km"]

        # Lineare Regression Pace ~ HR
        slope, intercept = np.polyfit(x, y, 1)

        # Geschätzte Pace bei baseline_hr
        pace_at_hr = slope * baseline_hr + intercept

        weekly_rows.append({
            "Woche": week,
            "Pace @ 150 bpm": pace_at_hr
        })

    pace_at_hr_df = pd.DataFrame(weekly_rows)

    if pace_at_hr_df.empty:
        return pd.DataFrame()

    # Reihenfolge für Trendlinie
    pace_at_hr_df["week_order"] = range(len(pace_at_hr_df))

    # Formatierte Pace für Tooltips (mm:ss)
    pace_at_hr_df["pace_formatted"] = pace_at_hr_df["Pace @ 150 bpm"].apply(
        lambda x: f"{int(x)}:{int((x - int(x)) * 60):02d}"
    )

    return pace_at_hr_df


# -----------------------------
# Efficiency Metriken
# -----------------------------
def calculate_efficiency_score(df):
    df = df.copy()

    required_columns = ["distance_km", "moving_time_min", "avg_hr"]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return None

    valid_runs = df.dropna(subset=["avg_hr", "distance_km", "moving_time_min"])

    if valid_runs.empty:
        return None

    # Speed = km pro Minute
    valid_runs["speed_km_per_min"] = valid_runs["distance_km"] / valid_runs["moving_time_min"]

    # Efficiency = Speed / HR
    valid_runs["efficiency"] = valid_runs["speed_km_per_min"] / valid_runs["avg_hr"]

    return valid_runs["efficiency"].mean()


def calculate_efficiency_baseline(df, baseline_hr=150):
    df = df.copy()

    required_columns = ["avg_hr", "pace_min_per_km"]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return None

    valid_runs = df.dropna(subset=["avg_hr", "pace_min_per_km"]).copy()

    if len(valid_runs) < 2:
        return None

    x = valid_runs["avg_hr"]
    y = valid_runs["pace_min_per_km"]

    slope, intercept = np.polyfit(x, y, 1)

    baseline_pace = slope * baseline_hr + intercept

    return baseline_pace

# -----------------------------
# Efficiency Trend
# -----------------------------
def calculate_efficiency_per_week(df):
    df = df.copy()

    required_columns = ["distance_km", "moving_time_min", "avg_hr", "start_date"]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return pd.DataFrame()

    valid_runs = df.dropna(subset=["distance_km", "moving_time_min", "avg_hr"]).copy()

    if valid_runs.empty:
        return pd.DataFrame()

    valid_runs["speed_km_per_min"] = valid_runs["distance_km"] / valid_runs["moving_time_min"]
    valid_runs["efficiency"] = (valid_runs["speed_km_per_min"] / valid_runs["avg_hr"]) * 1000
    valid_runs["week"] = valid_runs["start_date"].dt.strftime("%Y-KW%V")

    weekly_efficiency = valid_runs.groupby("week")["efficiency"].mean().reset_index()
    weekly_efficiency.columns = ["Woche", "Efficiency"]
    weekly_efficiency["week_order"] = range(len(weekly_efficiency))

    return weekly_efficiency

# -----------------------------
# Forecasting
# -----------------------------
def forecast_fitness_fatigue_form(df, days=14):

    fff = calculate_fitness_fatigue_form(df)

    if fff.empty:
        return pd.DataFrame()

    forecast_rows = []

    last_row = fff.iloc[-1]

    fitness = last_row["Fitness"]
    fatigue = last_row["Fatigue"]
    last_date = last_row["Datum"]

    for i in range(1, days + 1):

        date = last_date + pd.Timedelta(days=i)

        # kein Training → Load = 0
        load = 0

        # exponentielle decay (ähnlich wie im TrainingPeaks Modell)
        fatigue = fatigue * (1 - 1/7)
        fitness = fitness * (1 - 1/28)

        form = fitness - fatigue

        forecast_rows.append({
            "Datum": date,
            "Fitness": fitness,
            "Fatigue": fatigue,
            "Form": form
        })

    forecast_df = pd.DataFrame(forecast_rows)

    return forecast_df