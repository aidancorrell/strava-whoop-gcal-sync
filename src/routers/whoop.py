import logging
import secrets

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.oauth_manager import store_tokens
from src.config import settings
from src.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

WHOOP_AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"

# In-memory state store (single-user app, fine for this use case)
_pending_states: set[str] = set()


@router.get("/")
async def whoop_auth_redirect():
    """Redirect user to Whoop OAuth consent screen."""
    state = secrets.token_urlsafe(32)
    _pending_states.add(state)
    params = {
        "client_id": settings.whoop_client_id,
        "redirect_uri": f"{settings.app_base_url}/auth/whoop/callback",
        "response_type": "code",
        "scope": "read:workout read:sleep read:recovery read:profile",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{WHOOP_AUTH_URL}?{query}")


@router.get("/callback")
async def whoop_callback(code: str | None = None, state: str | None = None, error: str | None = None, db: AsyncSession = Depends(get_db)):
    """Handle Whoop OAuth callback — exchange code for tokens."""
    if error:
        logger.error("Whoop OAuth error: %s", error)
        return HTMLResponse(f"<h2>Whoop auth failed</h2><p>Error: {error}</p><p><a href='/'>← Back</a></p>")
    if not code:
        return HTMLResponse("<h2>Whoop auth failed</h2><p>No authorization code received.</p><p><a href='/'>← Back</a></p>")
    if state:
        _pending_states.discard(state)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            WHOOP_TOKEN_URL,
            auth=(settings.whoop_client_id, settings.whoop_client_secret),
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{settings.app_base_url}/auth/whoop/callback",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    logger.info("Whoop token response keys: %s, has refresh: %s, expires_in: %s",
                list(data.keys()), "refresh_token" in data, data.get("expires_in"))

    await store_tokens(
        db,
        service="whoop",
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token"),
        expires_in=data.get("expires_in"),
    )
    logger.info("Whoop connected")
    return HTMLResponse("<h2>Whoop connected!</h2><p><a href='/'>← Back</a></p>")
