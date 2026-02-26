from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Strava
    strava_client_id: str = ""
    strava_client_secret: str = ""
    strava_webhook_verify_token: str = "my-random-verify-token"

    # Whoop
    whoop_client_id: str = ""
    whoop_client_secret: str = ""

    # Google
    google_client_id: str = ""
    google_client_secret: str = ""

    # Basic Auth
    admin_username: str = "admin"
    admin_password: str = ""  # MUST be set in production

    # App
    app_base_url: str = "http://localhost:8000"
    database_url: str = "sqlite+aiosqlite:///./sync.db"
    sync_calendar_name: str = "Fitness Sync"
    whoop_poll_interval_minutes: int = 15
    log_level: str = "INFO"


settings = Settings()
