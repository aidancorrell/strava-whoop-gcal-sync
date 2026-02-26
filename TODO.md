# TODO

## Phase 2: OAuth2 Flows
- [x] Strava callback: exchange auth code for tokens in `src/routers/strava.py`, store via `oauth_manager`
- [x] Whoop callback: exchange auth code for tokens in `src/routers/whoop.py`, store via `oauth_manager`
- [x] Google callback: exchange auth code for tokens in `src/routers/google.py`, store via `oauth_manager`
- [x] Build a landing page at `/` showing auth status per service with "Connect" buttons

## Phase 3: Strava Integration
- [x] Add webhook router at `/webhook/strava` (GET for validation challenge, POST for events)
- [x] Wire POST handler to fetch full activity via `strava_service.get_activity()` and pass to sync engine
- [x] Handle activity update and delete webhook events
- [ ] Register Strava webhook subscription — run the curl command documented in README (one-time manual step)

## Phase 4: Whoop Integration
- [x] Start APScheduler in `main.py` lifespan to poll Whoop every N minutes
- [x] Poll job: fetch new workouts, sleep, and recovery since last poll
- [x] Pass each new item through the appropriate formatter and into the sync engine
- [x] Track last poll timestamp (in-memory, resets on deploy but dedup handles overlap)

## Phase 5: Google Calendar Integration
- [x] Call `find_or_create_calendar()` on first sync to set up the "Fitness Sync" calendar
- [ ] Set Google Calendar color IDs per activity type (run=green, ride=blue, sleep=purple, etc.)
- [ ] Add Strava/Whoop deep links in event descriptions

## Security
- [ ] Add basic auth to lock down the Railway site (landing page, OAuth routes)

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
- [ ] Update README with Railway deployment details and webhook registration command
- [ ] Set up a GitHub Actions CI workflow (lint + test)
