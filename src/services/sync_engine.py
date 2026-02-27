import logging
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import SyncRecord
from src.services import google_calendar

logger = logging.getLogger(__name__)


def _parse_event_time(event_body: dict) -> tuple[datetime | None, datetime | None]:
    """Extract start/end datetimes from a Google Calendar event body."""
    start = end = None
    try:
        start = datetime.fromisoformat(event_body["start"]["dateTime"])
        end = datetime.fromisoformat(event_body["end"]["dateTime"])
    except (KeyError, ValueError):
        pass
    return start, end


async def has_strava_overlap(db: AsyncSession, start: datetime, end: datetime) -> bool:
    """Check if any Strava activity overlaps with the given time window."""
    result = await db.execute(
        select(SyncRecord).where(
            SyncRecord.source == "strava",
            SyncRecord.activity_start.isnot(None),
            SyncRecord.activity_end.isnot(None),
            SyncRecord.activity_start < end,
            SyncRecord.activity_end > start,
        )
    )
    overlap = result.scalar_one_or_none()
    if overlap:
        logger.info("Skipping Whoop workout — overlaps with Strava activity %s", overlap.source_id)
        return True
    return False


async def sync_activity(
    db: AsyncSession,
    source: str,
    source_id: str,
    activity_type: str,
    event_body: dict,
    google_access_token: str,
    calendar_id: str,
    skip_if_strava_overlap: bool = False,
) -> SyncRecord | None:
    """Sync a single activity to Google Calendar with deduplication."""
    start, end = _parse_event_time(event_body)

    # Skip Whoop workouts that overlap with Strava activities
    if skip_if_strava_overlap and start and end:
        if await has_strava_overlap(db, start, end):
            return None

    # Check for existing sync record
    existing = await db.execute(
        select(SyncRecord).where(SyncRecord.source == source, SyncRecord.source_id == source_id)
    )
    record = existing.scalar_one_or_none()

    if record:
        logger.info("Updating existing sync: %s/%s", source, source_id)
        google_calendar.update_event(
            google_access_token, calendar_id, record.google_event_id, event_body
        )
        record.activity_start = start
        record.activity_end = end
        record.synced_at = datetime.utcnow()
    else:
        logger.info("Creating new sync: %s/%s", source, source_id)
        event = google_calendar.create_event(google_access_token, calendar_id, event_body)
        record = SyncRecord(
            source=source,
            source_id=source_id,
            activity_type=activity_type,
            google_event_id=event["id"],
            activity_start=start,
            activity_end=end,
        )
        db.add(record)

    await db.commit()
    return record


async def delete_activity(
    db: AsyncSession,
    source: str,
    source_id: str,
    google_access_token: str,
    calendar_id: str,
):
    """Delete a synced activity from Google Calendar."""
    existing = await db.execute(
        select(SyncRecord).where(SyncRecord.source == source, SyncRecord.source_id == source_id)
    )
    record = existing.scalar_one_or_none()
    if record:
        google_calendar.delete_event(google_access_token, calendar_id, record.google_event_id)
        await db.delete(record)
        await db.commit()
        logger.info("Deleted sync: %s/%s", source, source_id)
