from src.formatters.strava_formatter import format_activity
from src.formatters.whoop_formatter import format_sleep, format_workout


def test_strava_run_format(sample_strava_activity):
    event = format_activity(sample_strava_activity)
    assert "Morning Run" in event["summary"]
    assert "6.3 mi" in event["summary"]
    assert "/mi" in event["description"]
    assert "strava.com/activities/12345678" in event["description"]
    assert event["location"] == "37.7749,-122.4194"


def test_strava_no_distance(sample_strava_activity):
    sample_strava_activity["distance"] = 0
    event = format_activity(sample_strava_activity)
    assert "mi" not in event["summary"]


def test_whoop_workout_format(sample_whoop_workout):
    event = format_workout(sample_whoop_workout)
    assert "Running" in event["summary"]
    assert "Strain 14.2" in event["summary"]
    assert "Avg HR: 145" in event["description"]
    assert "4.97 mi" in event["description"]


def test_whoop_sleep_format(sample_whoop_sleep, sample_whoop_recovery):
    event = format_sleep(sample_whoop_sleep, sample_whoop_recovery)
    assert "Sleep" in event["summary"]
    assert "6h 30m" in event["summary"]  # actual sleep time, not time in bed
    assert "78% recovery" in event["summary"]
    assert "HRV: 55.2 ms" in event["description"]
    assert "Light:" in event["description"]
    assert "Deep (SWS):" in event["description"]
    assert "REM:" in event["description"]


def test_whoop_sleep_no_recovery(sample_whoop_sleep):
    event = format_sleep(sample_whoop_sleep)
    assert "recovery" not in event["summary"]
    assert "Recovery:" not in event["description"]
