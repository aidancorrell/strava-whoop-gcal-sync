from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from src.config import settings

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
async def strava_callback(code: str):
    """Handle Strava OAuth callback — exchange code for tokens."""
    # TODO: Exchange code for tokens via STRAVA_TOKEN_URL
    # TODO: Store tokens in DB via OAuthToken
    return {"message": "Strava connected", "code": code}
