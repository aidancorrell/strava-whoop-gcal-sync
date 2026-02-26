import logging
from datetime import datetime, timedelta

from src.config import settings
from src.database import async_session
from src.auth.oauth_manager import get_valid_token
from src.services.whoop_service import get_workouts, get_sleep, get_recovery
from src.services.google_calendar import find_or_create_calendar
from src.services.sync_engine import sync_activity
from src.formatters.whoop_formatter import format_workout, format_sleep

logger = logging.getLogger(__name__)

WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Track last poll time in memory (resets on restart, which is fine —
# the sync engine deduplicates so we just re-check recent items)
_last_poll: datetime | None = None


async def poll_whoop():
    """Fetch new Whoop data and sync to Google Calendar."""
    global _last_poll

    async with async_session() as db:
        whoop_token = await get_valid_token(
            db, "whoop", WHOOP_TOKEN_URL,
            settings.whoop_client_id, settings.whoop_client_secret,
        )
        google_token = await get_valid_token(
            db, "google", GOOGLE_TOKEN_URL,
            settings.google_client_id, settings.google_client_secret,
        )
        if not whoop_token or not google_token:
            logger.warning("Skipping Whoop poll — missing tokens (whoop=%s google=%s)",
                           bool(whoop_token), bool(google_token))
            return

        calendar_id = find_or_create_calendar(google_token)

        # Look back from last poll, or 1 hour on first run
        start_filter = None
        if _last_poll:
            start_filter = _last_poll.isoformat() + "Z"
        else:
            start_filter = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"

        _last_poll = datetime.utcnow()

        # Fetch workouts
        try:
            workouts = await get_workouts(whoop_token, start=start_filter)
            for w in workouts:
                if not w.get("score"):
                    continue
                event_body = format_workout(w)
                await sync_activity(
                    db, source="whoop", source_id=str(w["id"]),
                    activity_type="workout", event_body=event_body,
                    google_access_token=google_token, calendar_id=calendar_id,
                )
            logger.info("Synced %d Whoop workouts", len(workouts))
        except Exception:
            logger.exception("Error fetching Whoop workouts")

        # Fetch sleep + recovery
        try:
            sleep_records = await get_sleep(whoop_token, start=start_filter)
            recovery_records = await get_recovery(whoop_token, start=start_filter)
            # Index recovery by cycle_id or date for matching
            recovery_map = {}
            for r in recovery_records:
                if r.get("sleep_id"):
                    recovery_map[r["sleep_id"]] = r

            for s in sleep_records:
                if not s.get("score"):
                    continue
                recovery = recovery_map.get(s.get("id"))
                event_body = format_sleep(s, recovery)
                await sync_activity(
                    db, source="whoop", source_id=f"sleep-{s['id']}",
                    activity_type="sleep", event_body=event_body,
                    google_access_token=google_token, calendar_id=calendar_id,
                )
            logger.info("Synced %d Whoop sleep records", len(sleep_records))
        except Exception:
            logger.exception("Error fetching Whoop sleep/recovery")
