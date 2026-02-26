# TODO

## Phase 2: OAuth2 Flows
- [x] Strava callback: exchange auth code for tokens in `src/routers/strava.py`, store via `oauth_manager`
- [x] Whoop callback: exchange auth code for tokens in `src/routers/whoop.py`, store via `oauth_manager`
- [x] Google callback: exchange auth code for tokens in `src/routers/google.py`, store via `oauth_manager`
- [x] Build a landing page at `/` showing auth status per service with "Connect" buttons

## Phase 3: Strava Integration
- [ ] Add webhook router at `/webhook/strava` (GET for validation challenge, POST for events)
- [ ] Wire POST handler to fetch full activity via `strava_service.get_activity()` and pass to sync engine
- [ ] Handle activity update and delete webhook events
- [ ] Register Strava webhook subscription (document the curl command in README)

## Phase 4: Whoop Integration
- [ ] Start APScheduler in `main.py` lifespan to poll Whoop every N minutes
- [ ] Poll job: fetch new workouts, sleep, and recovery since last poll
- [ ] Pass each new item through the appropriate formatter and into the sync engine
- [ ] Track last poll timestamp (can use a simple DB row or in-memory)

## Phase 5: Google Calendar Integration
- [ ] Call `find_or_create_calendar()` on first sync to set up the "Fitness Sync" calendar
- [ ] Set Google Calendar color IDs per activity type (run=green, ride=blue, sleep=purple, etc.)
- [ ] Add Strava/Whoop deep links in event descriptions

## Phase 6: Sync Engine Hardening
- [ ] Add retry logic (e.g. tenacity) for transient Google API failures
- [ ] Handle token expiration mid-sync — refresh and retry
- [ ] Add structured logging throughout sync flow

## Phase 7: CLI Backfill
- [ ] Create `src/cli.py` with typer
- [ ] `backfill --source strava --days N` — fetches historical activities via `list_activities()`
- [ ] `backfill --source whoop --days N` — fetches historical workouts/sleep/recovery
- [ ] Add CLI entry point to `pyproject.toml`

## Phase 8: Deployment & Polish
- [ ] Add `structlog` or improve logging format
- [ ] Handle API rate limits (Strava: 100 req/15min, 1000/day)
- [ ] Write tests for sync engine with mocked Google Calendar API (`tests/test_sync_engine.py`)
- [ ] Add more formatter edge case tests
- [ ] Update README with screenshots/examples of calendar events
- [ ] Add deployment instructions for Railway / Fly.io
- [ ] Set up a GitHub Actions CI workflow (lint + test)
