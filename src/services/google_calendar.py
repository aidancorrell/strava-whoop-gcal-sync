import logging

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from src.config import settings

logger = logging.getLogger(__name__)


def _get_service(access_token: str, refresh_token: str | None = None):
    """Build a Google Calendar API service object."""
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
    )
    return build("calendar", "v3", credentials=creds)


def find_or_create_calendar(access_token: str, refresh_token: str | None = None) -> str:
    """Find the sync calendar by name, or create it. Returns calendar ID."""
    service = _get_service(access_token, refresh_token)
    calendars = service.calendarList().list().execute()
    for cal in calendars.get("items", []):
        if cal["summary"] == settings.sync_calendar_name:
            return cal["id"]

    new_cal = service.calendars().insert(body={"summary": settings.sync_calendar_name}).execute()
    logger.info("Created calendar: %s", new_cal["id"])
    return new_cal["id"]


def create_event(access_token: str, calendar_id: str, event_body: dict) -> dict:
    """Insert a new event into Google Calendar."""
    service = _get_service(access_token)
    return service.events().insert(calendarId=calendar_id, body=event_body).execute()


def update_event(access_token: str, calendar_id: str, event_id: str, event_body: dict) -> dict:
    """Update an existing Google Calendar event."""
    service = _get_service(access_token)
    return (
        service.events().update(calendarId=calendar_id, eventId=event_id, body=event_body).execute()
    )


def delete_event(access_token: str, calendar_id: str, event_id: str):
    """Delete a Google Calendar event."""
    service = _get_service(access_token)
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
