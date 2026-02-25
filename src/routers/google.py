from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.config import settings

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


@router.get("/")
async def google_auth_redirect():
    """Redirect user to Google OAuth consent screen."""
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": f"{settings.app_base_url}/auth/google/callback",
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar.events",
        "access_type": "offline",
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/callback")
async def google_callback(code: str):
    """Handle Google OAuth callback — exchange code for tokens."""
    # TODO: Exchange code for tokens via GOOGLE_TOKEN_URL
    # TODO: Store tokens in DB via OAuthToken
    return {"message": "Google Calendar connected", "code": code}
