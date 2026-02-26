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

WHOOP_AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"


@router.get("/")
async def whoop_auth_redirect():
    """Redirect user to Whoop OAuth consent screen."""
    params = {
        "client_id": settings.whoop_client_id,
        "redirect_uri": f"{settings.app_base_url}/auth/whoop/callback",
        "response_type": "code",
        "scope": "read:workout read:sleep read:recovery read:profile",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{WHOOP_AUTH_URL}?{query}")


@router.get("/callback")
async def whoop_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle Whoop OAuth callback — exchange code for tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            WHOOP_TOKEN_URL,
            data={
                "client_id": settings.whoop_client_id,
                "client_secret": settings.whoop_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{settings.app_base_url}/auth/whoop/callback",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    await store_tokens(
        db,
        service="whoop",
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token"),
        expires_in=data.get("expires_in"),
    )
    logger.info("Whoop connected")
    return HTMLResponse("<h2>Whoop connected!</h2><p><a href='/'>← Back</a></p>")
