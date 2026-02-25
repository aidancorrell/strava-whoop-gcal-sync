import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import SyncRecord
from src.services import google_calendar

logger = logging.getLogger(__name__)


async def sync_activity(
    db: AsyncSession,
    source: str,
    source_id: str,
    activity_type: str,
    event_body: dict,
    google_access_token: str,
    calendar_id: str,
) -> SyncRecord:
    """Sync a single activity to Google Calendar with deduplication."""
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
        record.synced_at = datetime.utcnow()
    else:
        logger.info("Creating new sync: %s/%s", source, source_id)
        event = google_calendar.create_event(google_access_token, calendar_id, event_body)
        record = SyncRecord(
            source=source,
            source_id=source_id,
            activity_type=activity_type,
            google_event_id=event["id"],
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
