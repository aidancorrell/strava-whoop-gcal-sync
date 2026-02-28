# Strava + Whoop → Google Calendar Sync

Automatically sync your Strava activities and Whoop workouts/sleep data to a dedicated Google Calendar.

## What It Does

- **Strava** — Real-time sync via webhooks. When you finish a run, ride, or workout, a calendar event appears with distance (miles), pace, heart rate, elevation, and a link back to Strava.
- **Whoop** — Polls hourly for new workouts and sleep. Workout events show the activity name, strain, heart rate, and distance. Sleep events show time asleep (not time in bed), stage breakdown (light/deep/REM), and recovery metrics (HRV, resting HR).
- **Deduplication** — If Strava and Whoop both track the same workout, only the Strava event shows up (richer data).
- **Google Calendar** — Everything lands in a dedicated "Fitness Sync" calendar so you can toggle visibility without cluttering your main calendar.

## Setup

### 1. Register API Apps

**Strava** — https://www.strava.com/settings/api
- Set "Authorization Callback Domain" to your deployment domain (e.g., `your-app.up.railway.app`)

**Whoop** — https://developer-dashboard.whoop.com
- Create an app and set the redirect URI to `{APP_BASE_URL}/auth/whoop/callback`
- Required scopes: `offline`, `read:workout`, `read:sleep`, `read:recovery`, `read:profile`

**Google Calendar** — https://console.cloud.google.com
- Create a project and enable the Google Calendar API
- Create OAuth 2.0 credentials (Web application type)
- Add `{APP_BASE_URL}/auth/google/callback` as an authorized redirect URI
- Add yourself as a test user in the OAuth consent screen (unless you publish the app)

### 2. Configure

```bash
cp .env.example .env
# Fill in your client IDs, secrets, and admin credentials
```

Key environment variables:

| Variable | Description |
|---|---|
| `STRAVA_CLIENT_ID` / `STRAVA_CLIENT_SECRET` | From Strava API settings |
| `WHOOP_CLIENT_ID` / `WHOOP_CLIENT_SECRET` | From Whoop developer dashboard |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Basic auth credentials for the web UI |
| `STRAVA_WEBHOOK_VERIFY_TOKEN` | Random string for Strava webhook validation |
| `APP_BASE_URL` | Your public deployment URL |
| `DATABASE_URL` | SQLite connection string (default: `sqlite+aiosqlite:///./sync.db`) |

### 3. Run

```bash
# With uv (recommended)
uv sync
uv run uvicorn src.main:app --reload

# Or with Docker
docker compose up
```

### 4. Connect Services

Visit your app's root URL and click through to connect each service:
1. **Google Calendar** — Authorizes calendar access
2. **Strava** — Authorizes activity read access
3. **Whoop** — Authorizes workout/sleep/recovery read access

Each service only needs to be connected once. Tokens auto-refresh.

### 5. Register Strava Webhook

One-time setup to receive real-time activity updates:

```bash
curl -X POST https://www.strava.com/api/v3/push_subscriptions \
  -d client_id=YOUR_CLIENT_ID \
  -d client_secret=YOUR_CLIENT_SECRET \
  -d callback_url=YOUR_APP_BASE_URL/webhook/strava \
  -d verify_token=YOUR_VERIFY_TOKEN
```

## Deployment

Designed to run on any platform that supports Docker — Railway, Fly.io, Render, etc.

Requirements for production:
- **Persistent storage** for the SQLite database (e.g., Railway volumes, mounted at `/data`)
- **Always-on** — the app needs to be running to receive Strava webhooks and poll Whoop
- **HTTPS** — required for OAuth callbacks and webhooks
- Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` to protect the web UI with basic auth

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Lint
uv run ruff check src/ tests/

# Format
uv run ruff format src/ tests/
```

## Architecture

```
src/
├── main.py                  # FastAPI app, scheduler setup
├── config.py                # Pydantic settings from env vars
├── models.py                # SQLAlchemy models (OAuthToken, SyncRecord)
├── database.py              # Async DB engine + migrations
├── auth/
│   ├── oauth_manager.py     # Token storage + auto-refresh
│   └── basic_auth.py        # Basic auth for web UI
├── routers/
│   ├── home.py              # Landing page with connection status
│   ├── strava.py            # Strava OAuth flow
│   ├── whoop.py             # Whoop OAuth flow
│   ├── google.py            # Google OAuth flow
│   ├── webhook.py           # Strava webhook handler
│   └── health.py            # Health check endpoint
├── services/
│   ├── sync_engine.py       # Dedup + create/update/delete calendar events
│   ├── strava_service.py    # Strava API client
│   ├── whoop_service.py     # Whoop API client
│   ├── whoop_poller.py      # Hourly Whoop poll job
│   ├── strava_backfill.py   # Backfill recent Strava activities on startup
│   └── google_calendar.py   # Google Calendar API client
└── formatters/
    ├── strava_formatter.py  # Strava activity → calendar event
    └── whoop_formatter.py   # Whoop workout/sleep → calendar event
```

## License

MIT
