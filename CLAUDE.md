# CLAUDE.md

## Project Overview
Python service that syncs Strava activities and Whoop workout/sleep/recovery data to Google Calendar. Built with FastAPI, SQLAlchemy (async SQLite), and OAuth2 for all three services.

## Commands
- **Run dev server**: `uv run uvicorn src.main:app --reload`
- **Run tests**: `uv run pytest`
- **Run single test file**: `uv run pytest tests/test_formatters.py`
- **Lint**: `uv run ruff check src/ tests/`
- **Lint fix**: `uv run ruff check --fix src/ tests/`
- **Format**: `uv run ruff format src/ tests/`
- **Install deps**: `uv sync` (or `uv sync --extra dev` for dev deps)

## Architecture
- `src/main.py` — FastAPI app entrypoint with lifespan (DB init, scheduler startup)
- `src/config.py` — All settings via pydantic-settings, loaded from `.env`
- `src/models.py` — SQLAlchemy models: `OAuthToken`, `SyncRecord`
- `src/routers/` — HTTP endpoints: OAuth callbacks per service, health check, Strava webhooks
- `src/services/` — API clients (Strava, Whoop, Google Calendar) and sync orchestration
- `src/auth/oauth_manager.py` — Token storage and refresh for all three OAuth services
- `src/formatters/` — Convert raw API data into Google Calendar event dicts
- `tests/` — pytest with async support; fixtures in `conftest.py`

## Key Patterns
- **Async everywhere**: All DB access and HTTP calls are async (httpx, SQLAlchemy async sessions)
- **OAuth token flow**: Tokens stored in `OAuthToken` table, auto-refreshed via `oauth_manager.get_valid_token()`
- **Deduplication**: `SyncRecord` table tracks source/source_id → google_event_id to prevent duplicate events; existing records get updated instead of re-created
- **Formatters are pure functions**: They take an API response dict and return a Google Calendar event body dict — easy to test with no side effects

## Style
- Python 3.11+, use `X | None` not `Optional[X]`
- Line length 100 (ruff)
- Keep things simple — no unnecessary abstractions
- Use `logging` (not print) for runtime output
- TODOs in code mark unfinished work — check `TODO.md` for the full list

## Current State
Phase 1 (scaffolding) is complete. OAuth callbacks have the redirect flow but still need token exchange implementation. See `TODO.md` for the ordered list of remaining work.
