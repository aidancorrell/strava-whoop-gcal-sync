from datetime import datetime

SPORT_EMOJI = {
    "Running": "\U0001f3c3",
    "Cycling": "\U0001f6b4",
    "Swimming": "\U0001f3ca",
    "Weightlifting": "\U0001f3cb\ufe0f",
    "Strength Training": "\U0001f3cb\ufe0f",
    "Hiking": "\U0001f6b6",
    "Walking": "\U0001f6b6",
    "Yoga": "\U0001f9d8",
    "CrossFit": "\U0001f4aa",
    "Functional Fitness": "\U0001f4aa",
}


def _ms_to_hm(ms: int) -> str:
    """Convert milliseconds to 'Xh YYm' format."""
    total_min = ms // 60_000
    h = total_min // 60
    m = total_min % 60
    return f"{h}h {m:02d}m"


def format_workout(workout: dict) -> dict:
    """Convert a Whoop workout to a Google Calendar event body."""
    sport_name = workout.get("sport_name", "Workout")
    emoji = SPORT_EMOJI.get(sport_name, "\U0001f4aa")
    score = workout.get("score") or {}
    strain = score.get("strain", 0)

    title = f"{emoji} {sport_name} \u2014 Strain {strain:.1f}"

    start_dt = datetime.fromisoformat(workout["start"].replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(workout["end"].replace("Z", "+00:00"))

    desc_parts = [
        f"Strain: {strain:.1f}",
        f"Avg HR: {score.get('average_heart_rate', 0):.0f} bpm",
        f"Max HR: {score.get('max_heart_rate', 0):.0f} bpm",
        f"Calories: {(score.get('kilojoule', 0) or 0) / 4.184:.0f} kcal",
    ]
    if score.get("distance_meter"):
        miles = score["distance_meter"] / 1609.34
        desc_parts.append(f"Distance: {miles:.2f} mi")
    if score.get("altitude_gain_meter"):
        desc_parts.append(f"Elevation: {score['altitude_gain_meter']:.0f} m")

    return {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
        "description": "\n".join(desc_parts),
    }


def format_sleep(sleep: dict, recovery: dict | None = None) -> dict:
    """Convert Whoop sleep data to a Google Calendar event body."""
    start_dt = datetime.fromisoformat(sleep["start"].replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(sleep["end"].replace("Z", "+00:00"))

    score = sleep.get("score") or {}
    stages = score.get("stage_summary") or {}

    # Calculate actual time asleep (light + SWS + REM)
    light = stages.get("total_light_sleep_time_milli", 0) or 0
    sws = stages.get("total_slow_wave_sleep_time_milli", 0) or 0
    rem = stages.get("total_rem_sleep_time_milli", 0) or 0
    total_sleep_ms = light + sws + rem

    sleep_str = _ms_to_hm(total_sleep_ms)

    recovery_pct = ""
    if recovery:
        r_score = recovery.get("score") or {}
        if r_score.get("recovery_score"):
            recovery_pct = f" ({r_score['recovery_score']:.0f}% recovery)"

    title = f"\U0001f634 Sleep \u2014 {sleep_str}{recovery_pct}"

    desc_parts = [
        f"Time Asleep: {sleep_str}",
        f"  Light: {_ms_to_hm(light)}",
        f"  Deep (SWS): {_ms_to_hm(sws)}",
        f"  REM: {_ms_to_hm(rem)}",
        f"Sleep Performance: {score.get('sleep_performance_percentage', 0):.0f}%",
        f"Sleep Efficiency: {score.get('sleep_efficiency_percentage', 0):.0f}%",
        f"Disturbances: {stages.get('disturbance_count', 0)}",
        f"Respiratory Rate: {score.get('respiratory_rate', 0):.1f}",
    ]
    if recovery:
        r_score = recovery.get("score") or {}
        desc_parts.extend([
            "",
            "Recovery:",
            f"  Score: {r_score.get('recovery_score', 0):.0f}%",
            f"  HRV: {r_score.get('hrv_rmssd_milli', 0):.1f} ms",
            f"  Resting HR: {r_score.get('resting_heart_rate', 0):.0f} bpm",
        ])

    return {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
        "description": "\n".join(desc_parts),
    }
