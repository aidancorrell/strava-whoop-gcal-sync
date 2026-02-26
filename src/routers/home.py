from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import OAuthToken

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(db: AsyncSession = Depends(get_db)):
    """Landing page showing auth status for each service."""
    result = await db.execute(select(OAuthToken))
    tokens = {t.service: t for t in result.scalars().all()}

    def status_row(service: str, label: str) -> str:
        token = tokens.get(service)
        if token:
            expired = token.expires_at and token.expires_at < datetime.utcnow()
            if expired:
                badge = '<span style="color:#e67e22">&#9888; Expired</span>'
            else:
                badge = '<span style="color:#27ae60">&#10003; Connected</span>'
            return f"<tr><td>{label}</td><td>{badge}</td><td><a href='/auth/{service}'>Reconnect</a></td></tr>"
        return f"<tr><td>{label}</td><td><span style='color:#999'>Not connected</span></td><td><a href='/auth/{service}'>Connect</a></td></tr>"

    rows = status_row("strava", "Strava") + status_row("whoop", "Whoop") + status_row("google", "Google Calendar")

    return f"""<!DOCTYPE html>
<html>
<head><title>Fitness Sync</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
  td {{ padding: 12px; border-bottom: 1px solid #eee; }}
  a {{ color: #3498db; }}
</style>
</head>
<body>
  <h1>Fitness Sync</h1>
  <p>Strava + Whoop &rarr; Google Calendar</p>
  <table>
    <tr><th align="left">Service</th><th align="left">Status</th><th></th></tr>
    {rows}
  </table>
</body>
</html>"""
