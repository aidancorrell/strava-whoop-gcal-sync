import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.services.strava_service import get_activity
from src.formatters.strava_formatter import format_activity
from src.services.sync_engine import sync_activity, delete_activity
from src.auth.oauth_manager import get_valid_token
from src.services.google_calendar import find_or_create_calendar

logger = logging.getLogger(__name__)

router = APIRouter()

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


@router.get("")
async def strava_webhook_validate(request: Request):
    """Respond to Strava's webhook subscription validation challenge."""
    # Strava sends hub.mode, hub.verify_token, hub.challenge (with dots)
    params = request.query_params
    verify_token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if verify_token == settings.strava_webhook_verify_token:
        logger.info("Strava webhook validation successful")
        return {"hub.challenge": challenge}
    logger.warning("Strava webhook validation failed — bad verify token")
    return JSONResponse(status_code=403, content={"error": "Invalid verify token"})


@router.post("")
async def strava_webhook_receive(request: Request, db: AsyncSession = Depends(get_db)):
    """Receive Strava webhook events for activity create/update/delete."""
    body = await request.json()
    logger.info("Strava webhook received: %s", body)

    object_type = body.get("object_type")
    aspect_type = body.get("aspect_type")
    object_id = body.get("object_id")

    if object_type != "activity":
        return {"status": "ignored"}

    # Get valid tokens
    strava_token = await get_valid_token(
        db, "strava", STRAVA_TOKEN_URL,
        settings.strava_client_id, settings.strava_client_secret,
    )
    google_token = await get_valid_token(
        db, "google", GOOGLE_TOKEN_URL,
        settings.google_client_id, settings.google_client_secret,
    )
    if not strava_token or not google_token:
        logger.error("Missing tokens — strava=%s google=%s", bool(strava_token), bool(google_token))
        return JSONResponse(status_code=500, content={"error": "Not fully connected"})

    calendar_id = find_or_create_calendar(google_token)

    if aspect_type in ("create", "update"):
        activity = await get_activity(strava_token, object_id)
        event_body = format_activity(activity)
        await sync_activity(
            db,
            source="strava",
            source_id=str(object_id),
            activity_type=activity.get("type", "unknown"),
            event_body=event_body,
            google_access_token=google_token,
            calendar_id=calendar_id,
        )
        logger.info("Synced Strava activity %s (%s)", object_id, aspect_type)
    elif aspect_type == "delete":
        await delete_activity(db, "strava", str(object_id), google_token, calendar_id)
        logger.info("Deleted Strava activity %s", object_id)

    return {"status": "ok"}
