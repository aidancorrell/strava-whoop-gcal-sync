# CLAUDE.md

## Project Overview
Python service that syncs Strava activities and Whoop workout/sleep/recovery data to Google Calendar. Built with FastAPI, SQLAlchemy (async SQLite), and OAuth2 for all three services.

## Deployment
- **Hosted on Railway**: https://strava-whoop-gcal-sync-production.up.railway.app
- **Railway project**: https://railway.com/project/db57d5cd-b7c4-4881-b225-e76ee44a13b5
- **Repo**: private GitHub repo at `aidancorrell/strava-whoop-gcal-sync`
- **DB**: SQLite on a Railway persistent volume mounted at `/data`
- **Deploy**: `railway up --detach` from project root (or push to GitHub — not auto-deploy, manual only)
- **Logs**: `railway logs -n 50`
- **Env vars**: Non-secrets set via `railway variables set`. Secrets (client IDs/secrets) managed in Railway dashboard only — never in code or CLI history.

## Commands
- **Run dev server**: `uv run uvicorn src.main:app --reload`
- **Run tests**: `uv run pytest`
- **Run single test file**: `uv run pytest tests/test_formatters.py`
- **Lint**: `uv run ruff check src/ tests/`
- **Lint fix**: `uv run ruff check --fix src/ tests/`
- **Format**: `uv run ruff format src/ tests/`
- **Install deps**: `uv sync` (or `uv sync --extra dev` for dev deps)
- **Deploy to Railway**: `railway up --detach`

## Architecture
- `src/main.py` — FastAPI app with lifespan: DB init, APScheduler for Whoop polling (every 15 min)
- `src/config.py` — All settings via pydantic-settings, loaded from `.env` or Railway env vars
- `src/models.py` — SQLAlchemy models: `OAuthToken`, `SyncRecord`
- `src/routers/home.py` — Landing page at `/` showing connection status per service
- `src/routers/strava.py` — Strava OAuth redirect + callback
- `src/routers/whoop.py` — Whoop OAuth redirect + callback (includes `state` param for CSRF)
- `src/routers/google.py` — Google OAuth redirect + callback
- `src/routers/webhook.py` — Strava webhook: GET for validation, POST for activity create/update/delete
- `src/routers/health.py` — Health check at `/health`
- `src/services/strava_service.py` — Strava API client (get activity, list activities)
- `src/services/whoop_service.py` — Whoop API client (workouts, sleep, recovery)
- `src/services/whoop_poller.py` — APScheduler job: polls Whoop, formats, syncs to calendar
- `src/services/google_calendar.py` — Google Calendar API: find/create calendar, CRUD events
- `src/services/sync_engine.py` — Orchestration: dedup check, create/update/delete calendar events
- `src/auth/oauth_manager.py` — Token storage, refresh logic for all three services
- `src/formatters/` — Pure functions converting API responses to Google Calendar event dicts
- `tests/` — pytest with async support; fixtures in `conftest.py`

## Key Patterns
- **Async everywhere**: All DB access and HTTP calls are async (httpx, SQLAlchemy async sessions)
- **OAuth token flow**: Tokens stored in `OAuthToken` table, auto-refreshed via `oauth_manager.get_valid_token()`
- **Deduplication**: `SyncRecord` table tracks source/source_id → google_event_id to prevent duplicate events; existing records get updated instead of re-created
- **Formatters are pure functions**: They take an API response dict and return a Google Calendar event body dict — easy to test with no side effects
- **Whoop requires `state` param**: The OAuth flow includes a CSRF state token (in-memory set)

## Style
- Python 3.11+, use `X | None` not `Optional[X]`
- Line length 100 (ruff)
- Keep things simple — no unnecessary abstractions
- Use `logging` (not print) for runtime output
- TODOs in code mark unfinished work — check `TODO.md` for the full list

## Current State
Phases 1-4 are implemented and deployed to Railway. All three OAuth services are connected. Whoop polls every 15 minutes. Strava webhook endpoint is built but the webhook subscription hasn't been registered yet (one-time curl command). See `TODO.md` for remaining work — next priorities are basic auth for the site and registering the Strava webhook.
