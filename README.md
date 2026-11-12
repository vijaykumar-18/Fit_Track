# FitTrack – Fitness & Workout Management Platform

FitTrack is a full-stack fitness tracker built with FastAPI, SQLAlchemy, SQLite, React, TypeScript, and Vite. It supports Phase 1 fitness tracking, Phase 2 planning and engagement, and Phase 3 nutrition, hydration, recommendations, workout timing, reminders, and advanced analytics.

The full implementation brief, scope, file checklist, and acceptance criteria are in [PROJECT_SPEC.md](./PROJECT_SPEC.md).

## What is included

### Phase 1
- JWT registration/login, bcrypt password hashing, protected API routes, and per-user ownership checks.
- Create, list, edit, and delete workouts; persisted daily progress summaries; goal creation and tracking.
- Weekly/monthly activity reports and weekly/monthly comparisons.
- In-app notifications, including goal/badge alerts and configurable daily workout reminders.
- React pages for overview, workouts, goals, analytics, and notifications.

### Phase 2
- Create, edit, delete, and list scheduled workout plans; monthly calendar and upcoming-workout list.
- Searchable, category-filtered exercise library; add library exercises to an owned workout.
- Current and longest streak tracking; milestone badges and achievement notifications.
- Personalized dashboard with daily stats, goals, upcoming workouts, streak, and earned badges.

### Phase 3
- Daily meal logging with calorie and macro summaries; configurable water goals and intake tracking.
- Personalized, rule-based workout suggestions based on goals, recent activity, and streaks.
- Live workout timer that saves a workout and estimated calorie count to the workout history.
- Eight-week and 30-day trends, workout consistency, and goal-completion analytics.
- Per-user, timezone-aware in-app workout, meal, and hydration reminders.
- Google Fit and Apple Health are optional future integrations and are not configured in this starter.

## Requirements
- Python 3.10 or newer
- Node.js 18 or newer and npm

## Run locally (Windows PowerShell)

Open two terminals from the repository root.

### 1. Backend

```powershell
Set-Location .\backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Before deploying, replace `SECRET_KEY` in `backend\.env` with a random value of at least 32 characters. For example:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Run the API:

```powershell
uvicorn app.main:app --reload
```

API: <http://127.0.0.1:8000>

Interactive API documentation: <http://127.0.0.1:8000/docs>

### 2. Frontend

```powershell
Set-Location .\frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open the Vite URL printed in the terminal (normally <http://localhost:5173>). `VITE_API_URL` sets the backend origin; it defaults to `http://127.0.0.1:8000`.

If PowerShell blocks virtual-environment activation, run this once in that terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

## Configuration

`backend\.env`:

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `FitTrack API` | API title |
| `ENVIRONMENT` | `development` | In production, requires a unique `SECRET_KEY` of at least 32 characters |
| `DATABASE_URL` | `sqlite:///./fittrack.db` | SQLAlchemy database URL |
| `SECRET_KEY` | Development placeholder | Set a unique random secret before deployment |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT lifetime |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed frontend origins |
| `REMINDER_HOUR` | `9` | Daily reminder hour, 0–23 |
| `REMINDER_MINUTE` | `0` | Daily reminder minute, 0–59 |
| `REMINDER_TIMEZONE` | `UTC` | IANA timezone used by the reminder scheduler |

SQLite is used by default. To use PostgreSQL, install a compatible SQLAlchemy driver and set `DATABASE_URL` to the PostgreSQL connection URL.

## API areas

All application endpoints are under `/api`; interactive OpenAPI docs are available at `/docs`.

| Area | Routes |
|---|---|
| Authentication | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Workouts | `GET/POST /workouts`, `GET/PATCH/DELETE /workouts/{id}` |
| Workout exercises | `GET/POST /workouts/{id}/exercises` |
| Progress and reports | `GET /progress/daily`, `/weekly`, `/monthly`, `/comparison` |
| Goals | `GET/POST /goals`, `PATCH/DELETE /goals/{id}` |
| Notifications | `GET /notifications`, `PATCH /notifications/{id}/read`, `POST /notifications/reminder` |
| Workout plans | `GET/POST /plans`, `GET/PATCH/DELETE /plans/{id}` |
| Exercise library | `GET /exercises?search=...&category=...` |
| Dashboard and engagement | `GET /dashboard`, `/streak`, `/badges`, `/badges/catalog` |
| Nutrition | `GET/POST /nutrition/meals`, `PATCH/DELETE /nutrition/meals/{id}`, `GET /nutrition/summary` |
| Hydration | `GET/POST /water`, `DELETE /water/{id}` |
| Reminders and preferences | `GET/PATCH /settings/reminders` |
| Recommendations | `GET /recommendations` |
| Advanced analytics | `GET /analytics/advanced` |

Authenticated routes require an `Authorization: Bearer <token>` header. User-owned data is always queried by both resource ID and authenticated user ID.

## Project layout

```text
Fit_Track/
├── PROJECT_SPEC.md
├── README.md
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── router.py
│   │   │   └── endpoints/       # auth, workouts, reports, comparisons, goals,
│   │   │                        # notifications, workout_plans, exercises,
│   │   │                        # streaks, badges, dashboard
│   │   ├── core/                # config.py, security.py, dependencies.py
│   │   ├── crud/                # user, workout, progress, goal, notification,
│   │   │                        # workout_plan, exercise
│   │   ├── database/            # base.py, connection.py
│   │   ├── models/              # one SQLAlchemy entity per file
│   │   ├── schemas/             # request/response types grouped by domain
│   │   ├── services/            # analytics, badges, dashboard, progress,
│   │   │                        # reminders, streak
│   │   └── main.py
│   └── tests/                   # conftest.py, test_health.py, test_phase2.py
└── frontend/
    ├── .env.example
    ├── package.json
    └── src/
        ├── components/          # reusable UI components
        ├── hooks/               # shared React data hooks
        ├── pages/               # authentication, Phase 2 and Phase 3 feature screens
        ├── services/            # API client and authentication
        ├── styles/              # application styles
        ├── types/               # shared frontend data types
        ├── utils/               # shared helpers
        ├── App.tsx              # navigation shell, analytics, workout timer
        ├── main.tsx
        └── vite-env.d.ts
```

`public/` and `assets/` are not currently needed because the app has no static media files. Add them when the UI introduces assets.

Phase 3 implementation files include `backend/app/models/meal.py`, `water_tracking.py`, and `user_preferences.py`; their API routes are in `backend/app/api/v1/endpoints/nutrition.py`, `water.py`, `preferences.py`, and `recommendations.py`. Nutrition persistence is grouped in `backend/app/crud/nutrition.py`; recommendation and reminder logic lives in `backend/app/services/recommendations.py` and `reminders.py`. The Phase 3 frontend is in `frontend/src/pages/PhaseThreeFeatures.tsx`, with the workout timer and analytics in `frontend/src/App.tsx`. New ownership and calculation tests are in `backend/tests/test_phase3.py`.

## Tests and build

Backend tests (from `backend`):

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

Frontend production build (from `frontend`):

```powershell
npm run build
```

## Security and operations

- Passwords are bcrypt-hashed. JWTs are signed with `SECRET_KEY`; use a unique secret and HTTPS in deployed environments.
- The frontend stores the JWT in `localStorage` as requested. This is vulnerable to token theft if a cross-site scripting flaw is introduced; production deployments should assess an HttpOnly-cookie design.
- The reminder scheduler runs inside the API process and creates per-user, timezone-aware in-app notifications for enabled workout, meal, and hydration reminders when the activity remains incomplete. Run a single API worker when using this in-process scheduler; move scheduling to a dedicated worker for multi-worker or multi-instance deployments.
- Tables are created from SQLAlchemy metadata at application startup for this starter. `create_all` is not a schema-migration system; add and apply reviewed Alembic migrations before evolving a deployed database.
- Calories and goals are user-entered estimates, not medical measurements. The app is not medical advice.
- Before production, configure HTTPS, a production database, schema migrations, rate limiting, structured logging, backups, monitoring, and a reviewed secret-management process.
