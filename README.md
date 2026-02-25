# Strava + Whoop → Google Calendar Sync

Automatically sync your Strava activities and Whoop workouts/sleep/recovery data to Google Calendar.

## How It Works

- **Strava**: Receives webhook notifications when you complete an activity, then creates a calendar event with distance, pace, HR, and more.
- **Whoop**: Polls every 15 minutes for new workouts, sleep, and recovery data, creating rich calendar events.
- **Google Calendar**: Events land in a dedicated "Fitness Sync" calendar so you can toggle visibility without cluttering your main calendar.

## Quick Start

### 1. Register API Apps

**Strava** — https://www.strava.com/settings/api
- Set callback domain to your `APP_BASE_URL`

**Whoop** — https://developer-dashboard.whoop.com
- Set redirect URI to `{APP_BASE_URL}/auth/whoop/callback`

**Google Calendar** — https://console.cloud.google.com
- Create a project, enable Calendar API
- Create OAuth 2.0 credentials (Web application)
- Add `{APP_BASE_URL}/auth/google/callback` as authorized redirect URI

### 2. Configure

```bash
cp .env.example .env
# Fill in your client IDs and secrets
```

### 3. Run Locally

```bash
# With uv
uv sync
uv run uvicorn src.main:app --reload

# Or with pip
pip install -e .
uvicorn src.main:app --reload
```

### 4. Run with Docker

```bash
docker compose up

# For local development with ngrok (needed for Strava webhooks):
docker compose --profile dev up
```

### 5. Connect Services

Visit `http://localhost:8000/auth/strava` to connect Strava, then `/auth/whoop` for Whoop, and `/auth/google` for Google Calendar.

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Lint
uv run ruff check src/ tests/
```

## Deployment

Works on any platform that runs Docker containers — Railway, Fly.io, Render, etc. Set the environment variables from `.env.example` in your hosting platform's dashboard.

**Important**: For Strava webhooks to work, your app must be publicly accessible. Update `APP_BASE_URL` to your deployment URL and register the webhook subscription via the Strava API.
