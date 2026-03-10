# Formatierung der Pace in Minuten pro Kilometer
def format_pace(pace_min_per_km):

    if pace_min_per_km is None:
        return "-"

    minutes = int(pace_min_per_km)
    seconds = int((pace_min_per_km - minutes) * 60)

    return f"{minutes}:{seconds:02d}"

# Formatierung der Zeit in Stunden und Minuten
def format_minutes_to_hours(minutes):

    if minutes is None:
        return "-"

    total_minutes = int(minutes)
    hours = total_minutes // 60
    remaining_minutes = total_minutes % 60

    return f"{hours}h {remaining_minutes:02d}min"