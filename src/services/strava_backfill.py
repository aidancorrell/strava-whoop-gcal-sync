import logging
from datetime import datetime, timedelta

from src.config import settings
from src.database import async_session
from src.auth.oauth_manager import get_valid_token
from src.services.strava_service import list_activities, get_activity
from src.services.google_calendar import find_or_create_calendar
from src.services.sync_engine import sync_activity
from src.formatters.strava_formatter import format_activity

logger = logging.getLogger(__name__)

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


async def backfill_strava(days: int = 7):
    """Fetch recent Strava activities and sync them to Google Calendar."""
    async with async_session() as db:
        strava_token = await get_valid_token(
            db, "strava", STRAVA_TOKEN_URL,
            settings.strava_client_id, settings.strava_client_secret,
        )
        google_token = await get_valid_token(
            db, "google", GOOGLE_TOKEN_URL,
            settings.google_client_id, settings.google_client_secret,
        )
        if not strava_token or not google_token:
            logger.warning("Skipping Strava backfill — missing tokens")
            return

        calendar_id = find_or_create_calendar(google_token)

        after = int((datetime.utcnow() - timedelta(days=days)).timestamp())
        activities = await list_activities(strava_token, after=after)
        logger.info("Strava backfill: found %d activities in last %d days", len(activities), days)

        for a in activities:
            try:
                full = await get_activity(strava_token, a["id"])
                event_body = format_activity(full)
                await sync_activity(
                    db,
                    source="strava",
                    source_id=str(a["id"]),
                    activity_type=full.get("type", "unknown"),
                    event_body=event_body,
                    google_access_token=google_token,
                    calendar_id=calendar_id,
                )
            except Exception:
                logger.exception("Error syncing Strava activity %s", a["id"])

        logger.info("Strava backfill complete: synced %d activities", len(activities))
