from datetime import datetime, timedelta

KM_TO_MI = 0.621371
M_TO_FT = 3.28084

SPORT_EMOJI = {
    "Run": "\U0001f3c3",
    "Ride": "\U0001f6b4",
    "Swim": "\U0001f3ca",
    "WeightTraining": "\U0001f3cb\ufe0f",
    "Hike": "\U0001f6b6",
    "Walk": "\U0001f6b6",
    "Yoga": "\U0001f9d8",
    "VirtualRide": "\U0001f6b4",
    "VirtualRun": "\U0001f3c3",
}


def format_activity(activity: dict) -> dict:
    """Convert a Strava activity to a Google Calendar event body."""
    sport = activity.get("type", "Workout")
    emoji = SPORT_EMOJI.get(sport, "\U0001f4aa")
    distance_mi = activity.get("distance", 0) / 1000 * KM_TO_MI
    name = activity.get("name", sport)

    title = f"{emoji} {name}"
    if distance_mi > 0.1:
        title += f" \u2014 {distance_mi:.1f} mi"

    start_dt = datetime.fromisoformat(activity["start_date"].replace("Z", "+00:00"))
    elapsed = activity.get("elapsed_time", 0)
    end_dt = start_dt + timedelta(seconds=elapsed)

    description_parts = [f"Sport: {sport}"]
    if distance_mi > 0.1:
        description_parts.append(f"Distance: {distance_mi:.2f} mi")
        moving_time = activity.get("moving_time", 0)
        if moving_time and distance_mi:
            pace_min = (moving_time / 60) / distance_mi
            description_parts.append(f"Pace: {int(pace_min)}:{int(pace_min % 1 * 60):02d} /mi")
    if activity.get("total_elevation_gain"):
        elevation_ft = activity["total_elevation_gain"] * M_TO_FT
        description_parts.append(f"Elevation: {elevation_ft:.0f} ft")
    if activity.get("average_heartrate"):
        description_parts.append(
            f"HR: {activity['average_heartrate']:.0f} avg / {activity.get('max_heartrate', 0):.0f} max"
        )
    if activity.get("suffer_score"):
        description_parts.append(f"Suffer Score: {activity['suffer_score']}")
    if activity.get("calories"):
        description_parts.append(f"Calories: {activity['calories']:.0f}")
    description_parts.append(f"\nhttps://www.strava.com/activities/{activity['id']}")

    event = {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
        "description": "\n".join(description_parts),
    }

    if activity.get("start_latlng"):
        lat, lng = activity["start_latlng"]
        event["location"] = f"{lat},{lng}"

    return event
