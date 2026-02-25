from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.config import settings

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
async def whoop_callback(code: str):
    """Handle Whoop OAuth callback — exchange code for tokens."""
    # TODO: Exchange code for tokens via WHOOP_TOKEN_URL
    # TODO: Store tokens in DB via OAuthToken
    return {"message": "Whoop connected", "code": code}
