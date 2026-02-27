import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI

from src.auth.basic_auth import verify_admin
from src.config import settings
from src.database import init_db
from src.routers import google, health, home, strava, webhook, whoop
from src.services.strava_backfill import backfill_strava
from src.services.whoop_poller import poll_whoop

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initializing database")
    await init_db()

    # Start Whoop polling
    scheduler.add_job(
        poll_whoop,
        "interval",
        minutes=settings.whoop_poll_interval_minutes,
        id="whoop_poll",
    )
    scheduler.start()
    logger.info("Whoop poller started — every %d minutes", settings.whoop_poll_interval_minutes)

    # Run initial syncs on startup
    try:
        await poll_whoop()
    except Exception:
        logger.exception("Initial Whoop poll failed (will retry on schedule)")

    try:
        await backfill_strava(days=7)
    except Exception:
        logger.exception("Initial Strava backfill failed")

    yield

    scheduler.shutdown()
    logger.info("Shutting down")


app = FastAPI(title="Strava + Whoop → Google Calendar Sync", lifespan=lifespan)

# Protected routes — require basic auth
app.include_router(home.router, dependencies=[Depends(verify_admin)])
app.include_router(strava.router, prefix="/auth/strava", tags=["strava"], dependencies=[Depends(verify_admin)])
app.include_router(whoop.router, prefix="/auth/whoop", tags=["whoop"], dependencies=[Depends(verify_admin)])
app.include_router(google.router, prefix="/auth/google", tags=["google"], dependencies=[Depends(verify_admin)])

# Public routes — no auth (Strava webhook must be reachable, health check for monitoring)
app.include_router(health.router)
app.include_router(webhook.router, prefix="/webhook/strava", tags=["strava-webhook"])
