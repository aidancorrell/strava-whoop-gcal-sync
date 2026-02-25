import logging

import httpx

logger = logging.getLogger(__name__)

STRAVA_API_BASE = "https://www.strava.com/api/v3"


async def get_activity(access_token: str, activity_id: int) -> dict:
    """Fetch full activity details from Strava."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{STRAVA_API_BASE}/activities/{activity_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()


async def list_activities(
    access_token: str, after: int | None = None, per_page: int = 50
) -> list[dict]:
    """List athlete activities, optionally filtered by epoch timestamp."""
    params: dict = {"per_page": per_page}
    if after:
        params["after"] = after
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{STRAVA_API_BASE}/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
        )
        resp.raise_for_status()
        return resp.json()
