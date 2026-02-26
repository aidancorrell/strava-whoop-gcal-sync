import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from src.config import settings
from src.database import init_db
from src.routers import google, health, home, strava, webhook, whoop
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

    # Run an initial poll on startup
    try:
        await poll_whoop()
    except Exception:
        logger.exception("Initial Whoop poll failed (will retry on schedule)")

    yield

    scheduler.shutdown()
    logger.info("Shutting down")


app = FastAPI(title="Strava + Whoop → Google Calendar Sync", lifespan=lifespan)

app.include_router(home.router)
app.include_router(health.router)
app.include_router(strava.router, prefix="/auth/strava", tags=["strava"])
app.include_router(whoop.router, prefix="/auth/whoop", tags=["whoop"])
app.include_router(google.router, prefix="/auth/google", tags=["google"])
app.include_router(webhook.router, prefix="/webhook/strava", tags=["strava-webhook"])
