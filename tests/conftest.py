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
        "id": "87654321-abcd-1234-efgh-567890123456",
        "sport_id": 1,
        "sport_name": "Running",
        "start": "2024-01-15T08:00:00Z",
        "end": "2024-01-15T09:00:00Z",
        "score_state": "SCORED",
        "score": {
            "strain": 14.2,
            "average_heart_rate": 145,
            "max_heart_rate": 172,
            "kilojoule": 2500,
            "distance_meter": 8000,
        },
    }


@pytest.fixture
def sample_whoop_sleep():
    return {
        "id": "11111111-aaaa-2222-bbbb-333333333333",
        "start": "2024-01-14T22:30:00Z",
        "end": "2024-01-15T06:02:00Z",
        "score_state": "SCORED",
        "score": {
            "stage_summary": {
                "total_in_bed_time_milli": 27120000,
                "total_awake_time_milli": 1800000,
                "total_light_sleep_time_milli": 10800000,
                "total_slow_wave_sleep_time_milli": 5400000,
                "total_rem_sleep_time_milli": 7200000,
                "total_no_data_time_milli": 0,
                "sleep_cycle_count": 4,
                "disturbance_count": 2,
            },
            "sleep_performance_percentage": 85,
            "sleep_efficiency_percentage": 91.7,
            "sleep_consistency_percentage": 90,
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
