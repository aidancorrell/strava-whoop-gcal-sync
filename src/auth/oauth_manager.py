import logging
from datetime import datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import OAuthToken

logger = logging.getLogger(__name__)


async def store_tokens(
    db: AsyncSession,
    service: str,
    access_token: str,
    refresh_token: str | None,
    expires_in: int | None,
):
    """Store or update OAuth tokens for a service."""
    result = await db.execute(select(OAuthToken).where(OAuthToken.service == service))
    token = result.scalar_one_or_none()

    expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None

    if token:
        token.access_token = access_token
        token.refresh_token = refresh_token or token.refresh_token
        token.expires_at = expires_at
        token.updated_at = datetime.utcnow()
    else:
        token = OAuthToken(
            service=service,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        db.add(token)

    await db.commit()
    return token


async def get_valid_token(db: AsyncSession, service: str, token_url: str, client_id: str, client_secret: str) -> str | None:
    """Get a valid access token, refreshing if expired."""
    result = await db.execute(select(OAuthToken).where(OAuthToken.service == service))
    token = result.scalar_one_or_none()
    if not token:
        return None

    if token.expires_at and token.expires_at < datetime.utcnow():
        if not token.refresh_token:
            logger.warning("Token expired for %s and no refresh token available", service)
            return None
        logger.info("Refreshing token for %s", service)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": token.refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            resp.raise_for_status()
            data = resp.json()
        await store_tokens(
            db, service, data["access_token"], data.get("refresh_token"), data.get("expires_in")
        )
        return data["access_token"]

    return token.access_token
