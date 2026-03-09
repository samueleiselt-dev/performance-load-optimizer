def format_pace(pace_min_per_km):

    if pace_min_per_km is None:
        return "-"

    minutes = int(pace_min_per_km)
    seconds = int((pace_min_per_km - minutes) * 60)

    return f"{minutes}:{seconds:02d}"