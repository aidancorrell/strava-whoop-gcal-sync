from datetime import datetime


def format_workout(workout: dict) -> dict:
    """Convert a Whoop workout to a Google Calendar event body."""
    sport = workout.get("sport_id", 0)
    score = workout.get("score") or {}
    strain = score.get("strain", 0)
    title = f"\U0001f4aa Whoop Workout \u2014 Strain {strain:.1f}"

    start_dt = datetime.fromisoformat(workout["start"].replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(workout["end"].replace("Z", "+00:00"))

    desc_parts = [
        f"Strain: {strain:.1f}",
        f"Avg HR: {score.get('average_heart_rate', 0):.0f}",
        f"Max HR: {score.get('max_heart_rate', 0):.0f}",
        f"Calories: {(score.get('kilojoule', 0) or 0) / 4.184:.0f} kcal",
    ]

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
    duration = end_dt - start_dt
    hours = int(duration.total_seconds() // 3600)
    minutes = int((duration.total_seconds() % 3600) // 60)

    recovery_pct = ""
    if recovery and recovery.get("score", {}).get("recovery_score"):
        recovery_pct = f" ({recovery['score']['recovery_score']:.0f}% recovery)"

    title = f"\U0001f634 Sleep \u2014 {hours}h {minutes:02d}m{recovery_pct}"

    score = sleep.get("score", {})
    desc_parts = [
        f"Sleep Performance: {score.get('sleep_performance_percentage', 0):.0f}%",
        f"Time in Bed: {hours}h {minutes:02d}m",
        f"Disturbances: {score.get('disturbance_count', 0)}",
        f"Respiratory Rate: {score.get('respiratory_rate', 0):.1f}",
    ]
    if recovery:
        r_score = recovery.get("score", {})
        desc_parts.extend([
            f"HRV: {r_score.get('hrv_rmssd_milli', 0):.1f} ms",
            f"Resting HR: {r_score.get('resting_heart_rate', 0):.0f} bpm",
            f"Recovery: {r_score.get('recovery_score', 0):.0f}%",
        ])

    return {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
        "description": "\n".join(desc_parts),
    }
