import logging

import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.oauth_manager import store_tokens
from src.config import settings
from src.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"


@router.get("/")
async def strava_auth_redirect():
    """Redirect user to Strava OAuth consent screen."""
    params = {
        "client_id": settings.strava_client_id,
        "redirect_uri": f"{settings.app_base_url}/auth/strava/callback",
        "response_type": "code",
        "scope": "read,activity:read_all",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{STRAVA_AUTH_URL}?{query}")


@router.get("/callback")
async def strava_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle Strava OAuth callback — exchange code for tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            STRAVA_TOKEN_URL,
            data={
                "client_id": settings.strava_client_id,
                "client_secret": settings.strava_client_secret,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    await store_tokens(
        db,
        service="strava",
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token"),
        expires_in=data.get("expires_in"),
    )
    logger.info("Strava connected for athlete %s", data.get("athlete", {}).get("id"))
    return HTMLResponse("<h2>Strava connected!</h2><p><a href='/'>← Back</a></p>")
