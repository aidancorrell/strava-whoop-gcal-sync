import logging
from datetime import datetime, timedelta

from src.config import settings
from src.database import async_session
from src.auth.oauth_manager import get_valid_token
from src.services.whoop_service import get_workouts, get_sleep, get_cycles
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
        if _last_poll:
            start_filter = _last_poll.isoformat() + "Z"
        else:
            start_filter = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"

        _last_poll = datetime.utcnow()

        # Fetch workouts
        try:
            workouts = await get_workouts(whoop_token, start=start_filter)
            for w in workouts:
                if w.get("score_state") != "SCORED":
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

        # Fetch sleep + cycles (cycles contain recovery scores in v2)
        try:
            sleep_records = await get_sleep(whoop_token, start=start_filter)
            cycles = await get_cycles(whoop_token, start=start_filter)

            # Build recovery map from cycles: cycle_id -> recovery score
            recovery_map = {}
            for c in cycles:
                if c.get("score"):
                    recovery_map[c["id"]] = c.get("score", {})

            for s in sleep_records:
                if s.get("score_state") != "SCORED":
                    continue
                # Match sleep to its cycle's recovery
                recovery = None
                cycle_id = s.get("cycle_id")
                if cycle_id and cycle_id in recovery_map:
                    recovery = {"score": recovery_map[cycle_id]}
                event_body = format_sleep(s, recovery)
                await sync_activity(
                    db, source="whoop", source_id=f"sleep-{s['id']}",
                    activity_type="sleep", event_body=event_body,
                    google_access_token=google_token, calendar_id=calendar_id,
                )
            logger.info("Synced %d Whoop sleep records", len(sleep_records))
        except Exception:
            logger.exception("Error fetching Whoop sleep/recovery")
