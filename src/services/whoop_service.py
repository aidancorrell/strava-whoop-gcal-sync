import logging

import httpx

logger = logging.getLogger(__name__)

WHOOP_API_BASE = "https://api.prod.whoop.com/developer/v1"


async def get_workouts(access_token: str, start: str | None = None) -> list[dict]:
    """Fetch workouts from Whoop. `start` is an ISO datetime string."""
    params = {}
    if start:
        params["start"] = start
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{WHOOP_API_BASE}/activity/workout",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("records", [])


async def get_sleep(access_token: str, start: str | None = None) -> list[dict]:
    """Fetch sleep records from Whoop."""
    params = {}
    if start:
        params["start"] = start
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{WHOOP_API_BASE}/activity/sleep",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("records", [])


async def get_recovery(access_token: str, start: str | None = None) -> list[dict]:
    """Fetch recovery data from Whoop."""
    params = {}
    if start:
        params["start"] = start
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{WHOOP_API_BASE}/recovery",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("records", [])
