import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import settings
from src.database import init_db
from src.routers import google, health, home, strava, whoop

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initializing database")
    await init_db()
    # TODO: Start APScheduler for Whoop polling
    yield
    logger.info("Shutting down")


app = FastAPI(title="Strava + Whoop → Google Calendar Sync", lifespan=lifespan)

app.include_router(home.router)
app.include_router(health.router)
app.include_router(strava.router, prefix="/auth/strava", tags=["strava"])
app.include_router(whoop.router, prefix="/auth/whoop", tags=["whoop"])
app.include_router(google.router, prefix="/auth/google", tags=["google"])
# TODO: Add webhook router for Strava at /webhook/strava
