import pytest


@pytest.fixture
def sample_strava_activity():
    return {
        "id": 12345678,
        "name": "Morning Run",
        "type": "Run",
        "distance": 10200.0,
        "moving_time": 3060,
        "elapsed_time": 3200,
        "total_elevation_gain": 85.0,
        "start_date": "2024-01-15T07:30:00Z",
        "average_heartrate": 155.0,
        "max_heartrate": 178.0,
        "suffer_score": 72,
        "calories": 680,
        "start_latlng": [37.7749, -122.4194],
    }


@pytest.fixture
def sample_whoop_workout():
    return {
        "id": 87654321,
        "sport_id": 1,
        "start": "2024-01-15T08:00:00Z",
        "end": "2024-01-15T09:00:00Z",
        "score": {
            "strain": 14.2,
            "average_heart_rate": 145,
            "max_heart_rate": 172,
            "kilojoule": 2500,
        },
    }


@pytest.fixture
def sample_whoop_sleep():
    return {
        "id": 11111111,
        "start": "2024-01-14T22:30:00Z",
        "end": "2024-01-15T06:02:00Z",
        "score": {
            "sleep_performance_percentage": 85,
            "disturbance_count": 2,
            "respiratory_rate": 15.3,
        },
    }


@pytest.fixture
def sample_whoop_recovery():
    return {
        "score": {
            "recovery_score": 78,
            "hrv_rmssd_milli": 55.2,
            "resting_heart_rate": 52,
        },
    }
