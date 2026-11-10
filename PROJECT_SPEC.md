# FitTrack – Project Specification and Implementation Prompt

## Project objective

Build and maintain FitTrack, a secure, full-stack fitness and workout management platform. The product helps each user log completed workouts, monitor daily and longer-term progress, plan future sessions, and stay motivated through goals, streaks, and achievements.

The implementation must use FastAPI and SQLAlchemy on the backend, Pydantic for request/response validation, and React with TypeScript on the frontend. The default local database is SQLite; the database URL must remain configurable. Keep ownership checks server-side for every user-owned record.

## Phase 1 – Fitness tracking platform

### 1. Authentication

- Users have `id`, `username`, `email`, `hashed_password`, and `created_at`.
- Provide registration, login, and current-user endpoints.
- Hash passwords with bcrypt; never return or log password hashes.
- Issue expiring JWT bearer tokens and protect every private API route.
- Validate credentials, email, username, and password inputs.
- The frontend provides registration and login screens, persists the requested JWT in `localStorage`, and blocks private pages when unauthenticated.

### 2. Workout management

- A workout has `id`, `user_id`, `workout_name`, `category` (`Cardio`, `Strength`, `Yoga`), `duration`, `calories_burned`, `workout_date`, and `created_at`.
- Authenticated users can create, list, read, edit, and delete only their workouts.
- The UI provides a workout form and history with edit/delete controls.
- Validate non-empty names, supported categories, positive bounded duration, and non-negative bounded calorie values.

### 3. Daily progress and goals

- Daily progress is calculated from workouts and includes workout count, calories, and duration.
- Goals have `id`, `user_id`, `goal_type` (`Weight Loss`, `Muscle Gain`, `Steps`), `target_value`, `current_value`, optional `deadline`, status, and `created_at`.
- Users can create, list, update, and delete their goals; completed goals receive a status and notification.
- The dashboard presents daily summary cards and goal progress.

### 4. Reports and notifications

- Provide weekly per-day summaries, monthly totals, and comparison of current versus prior weekly/monthly totals.
- Notifications have `id`, `user_id`, `title`, `message`, `is_read`, and `created_at`; users can list and mark their own notifications as read.
- Produce goal-completion and achievement alerts, plus a configurable daily in-app workout reminder.

## Phase 2 – Advanced tracking and engagement

### 5. Workout plans and scheduling

- Plans have `id`, `user_id`, `title`, `description`, `scheduled_date`, and `created_at`.
- Support create, list, read, edit, and delete operations with ownership validation.
- The frontend displays a calendar/planner and upcoming sessions.

### 6. Exercise library

- Exercises have `id`, `name`, `category` (`Cardio`, `Strength`, `Yoga`), `description`, and `duration`.
- Provide a predefined searchable, category-filterable library.
- Users can add one or more library exercises to their own workouts; an association table supports the many-to-many relationship.

### 7. Progress comparison

- Compare weekly and monthly workout, calorie, and duration totals with the preceding period.
- Show differences in the analytics UI and preserve existing daily/weekly/monthly reports.

### 8. Streaks and achievement badges

- Keep one streak record per user: `id`, `user_id`, `current_streak`, `longest_streak`, and `last_workout_date`.
- Recalculate streaks from distinct workout dates; a missed day breaks the current streak, and longest streak remains historical.
- Maintain a badge catalog (`id`, `name`, `description`, `icon`) and unique user awards (`id`, `user_id`, `badge_id`, `earned_at`).
- Award badges for workout-count, streak, and completed-goal milestones. Do not award the same badge more than once.
- Show streaks and badges in the UI and notify users when they earn a badge.

### 9. Personalized dashboard

Provide a protected dashboard response and layout with daily summary, upcoming scheduled workouts, current goals, streak state, and earned badges. The interface should update after relevant workout, goal, plan, or achievement changes.

## Data model checklist

Required tables:

- `users`
- `workouts`
- `progress`
- `goals`
- `notifications`
- `workout_plans`
- `exercises`
- `workout_exercises` (many-to-many links between workouts and library exercises)
- `streaks`
- `badges`
- `user_badges`

Use foreign keys and indexes for user/date lookups, uniqueness constraints for usernames, emails, and duplicate associations/awards, and cascading cleanup for user-owned records. Persist daily progress snapshots and synchronize them when workout records change.

## Recommended repository structure

```text
README.md
PROJECT_SPEC.md
backend/
  .env.example
  requirements.txt
  requirements-dev.txt
  app/
    main.py
    core/
      config.py
      security.py
      dependencies.py
    database/
      base.py
      connection.py
    models/
      user.py
      workout.py
      progress.py
      goal.py
      notification.py
      workout_plan.py
      exercise.py
      streak.py
      badge.py
      workout_exercise.py
    schemas/
      auth.py
      workout.py
      progress.py
      goal.py
      notification.py
      workout_plan.py
      exercise.py
      engagement.py
    crud/
      user.py
      workout.py
      progress.py
      goal.py
      notification.py
      workout_plan.py
      exercise.py
    api/v1/
      router.py
      endpoints/
        auth.py
        workouts.py
        goals.py
        reports.py
        comparisons.py
        notifications.py
        workout_plans.py
        exercises.py
        streaks.py
        badges.py
        dashboard.py
    services/
      analytics.py
      badges.py
      dashboard.py
      progress.py
      reminders.py
      streak.py
  tests/
    conftest.py
    test_health.py
    test_phase2.py
frontend/
  .env.example
  package.json
  src/
    components/StatCard.tsx
    pages/
      AuthPage.tsx
      AdvancedFeatures.tsx
    services/
      api.ts
      authService.ts
    hooks/useFitnessData.ts
    types/index.ts
    utils/date.ts
    styles/
      index.css
      advanced.css
    App.tsx
    main.tsx
    vite-env.d.ts
  index.html
  vite.config.ts
  tsconfig.json
```

Keep route handlers in the versioned API package, persistence queries in CRUD modules, business rules in services, and request/response types in domain schema modules. Add focused tests whenever a new route, ownership rule, calculation, or achievement rule is introduced. Add `public/` or `assets/` only when static assets are needed.

The current frontend keeps dashboard, workout, goal, report, and notification screens in `App.tsx`; split these into dedicated page modules as they grow. Tests are currently grouped in `test_phase2.py`; split them by feature if the suite expands. Static `public/` and `assets/` directories are intentionally omitted until the app needs image or font assets.

## Security, reliability, and quality requirements

- All private endpoints require JWT authentication; queries must scope user-owned resources by authenticated `user_id`.
- Validate every API payload with Pydantic and enforce database constraints where appropriate.
- Load secrets and database/CORS/scheduler configuration from environment settings. Never commit `.env` or production secrets.
- Return explicit errors for unauthorized access, missing resources, and invalid input; do not silently succeed.
- Keep frontend API access centralized, provide useful loading/error/empty states, and use typed API data.
- Preserve existing behavior when adding features; run backend tests and the frontend production build.
- Use HTTPS, production database migrations, rate limiting, backup/monitoring, and production-grade secrets before deployment.

## Acceptance criteria

1. A new user can register, log in, and access private pages; another user cannot read or mutate their data.
2. Workout create/read/update/delete is available in both API and frontend.
3. Daily, weekly, monthly, and comparison reports agree with stored workouts.
4. Users can create/edit/delete future plans and see them in a calendar and upcoming list.
5. Exercise search/filter works and selected exercises can be associated with an owned workout.
6. Streaks recalculate after workout changes; thresholds award unique badges and create notifications.
7. Dashboard shows daily metrics, active goals, upcoming plans, streak, and achievements.
8. Daily in-app reminder schedule is configurable; it is sent at most once per user per local day when that user has no workout logged that day.
9. Backend tests pass, frontend type-check/build passes, and README setup works on Windows PowerShell.

## Current project notes

The current implementation uses SQLAlchemy `create_all` for the starter database lifecycle; this does not update schemas already deployed. Add reviewed Alembic migrations before production schema changes. The daily scheduler is in-process, so use one API worker or move reminders to a dedicated scheduler when scaling out.
