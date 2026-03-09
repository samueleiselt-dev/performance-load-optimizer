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


def calculate_rolling_weekly_distance(df):
    last_7_days = df[df["start_date"] >= (pd.Timestamp.utcnow() - pd.Timedelta(days=7))]
    return last_7_days["distance_km"].sum()


def calculate_average_pace(df):
    total_distance = df["distance_km"].sum()
    total_time = df["moving_time_min"].sum()

    if total_distance == 0:
        return None

    return total_time / total_distance


def calculate_weekly_km(df):
    df = df.copy()
    df["week"] = df["start_date"].dt.to_period("W").astype(str)
    weekly_km = df.groupby("week")["distance_km"].sum().reset_index()
    weekly_km.columns = ["Woche", "Kilometer"]

    return weekly_km