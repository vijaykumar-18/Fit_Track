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

## Phase 3 – Smart features and advanced analytics

### 10. Nutrition and meals

- Store meals with `id`, `user_id`, `meal_type` (`Breakfast`, `Lunch`, `Dinner`, `Snacks`), `food_name`, `calories`, `protein`, `carbs`, `fats`, `meal_date`, and `created_at`.
- Authenticated users can add, list by day, update, and delete their own meal entries.
- Validate non-negative nutrition values and calculate daily calorie and macro totals.
- The frontend provides a meal-entry form, daily summary cards, and a meal list.

### 11. Water intake

- Store water entries with `id`, `user_id`, `quantity` (ml), `date`, and `created_at`.
- Authenticated users can log and remove their own entries; daily summaries include total intake, target, and percentage.
- Allow users to configure a daily water goal (250–10,000 ml) and display progress toward it.

### 12. Personalized workout recommendations

- Analyze active goals, workouts from the last 30 days, and the current streak to recommend entries from the exercise library.
- Return a short reason for each suggestion. Recommendations are explainable, deterministic in-app rules and do not require an external AI service or user data to leave the platform.
- Present recommendations in a protected frontend page with a path to start a timed workout.

### 13. Workout timer

- Provide a live start/stop timer with workout name and category.
- On stop, save a workout using measured elapsed time and a clearly identified category-based calorie estimate.
- Users can edit or delete the saved workout using the existing workout-management controls.

### 14. Third-party fitness integrations (optional)

- Google Fit and Apple Health integrations are optional and are not enabled in the starter implementation.
- An integration requires provider credentials, user consent, platform-specific authorization, token storage/refresh, and an explicit data-mapping/privacy review before implementation.
- Do not simulate a successful external sync when no provider integration is configured.

### 15. Advanced analytics

- Preserve daily/weekly/monthly reports and comparisons.
- Provide eight-week workout trends, a rolling 30-day activity trend, workout consistency (active days / 30), and goal completion rate.
- Visualize trends and summary indicators in the protected analytics page.

### 16. Custom in-app reminders

- Let each user configure enabled state and local time for workout, meal, and hydration reminders, plus an IANA timezone.
- Send at most one reminder of each enabled type per user and local calendar day, only when the corresponding activity is still unlogged or the water goal is unmet.
- Store reminders as in-app notifications. The scheduler must check each user in their configured timezone.
- Keep reminder state private to the authenticated user and validate time, timezone, and goal inputs.

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
- `meals`
- `water_tracking`
- `user_preferences` (timezone, hydration goal, reminder settings and per-day delivery guards)

Use foreign keys and indexes for user/date lookups, uniqueness constraints for usernames, emails, and duplicate associations/awards, and cascading cleanup for user-owned records. Persist daily progress snapshots and synchronize them when workout records change.

For meals, retain a `meal_date` independent of the creation timestamp so users can summarize a local calendar day. The timer creates a regular workout row rather than a separate timer table. Reminder preferences and reminder delivery dates are stored per user; a delivery-date field prevents repeated scheduler sends.

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
      meal.py
      water_tracking.py
      user_preferences.py
    schemas/
      auth.py
      workout.py
      progress.py
      goal.py
      notification.py
      workout_plan.py
      exercise.py
      nutrition.py
      preferences.py
      engagement.py
    crud/
      user.py
      workout.py
      progress.py
      goal.py
      notification.py
      workout_plan.py
      exercise.py
      nutrition.py
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
        nutrition.py
        water.py
        preferences.py
        recommendations.py
    services/
      analytics.py
      badges.py
      dashboard.py
      progress.py
      reminders.py
      recommendations.py
      streak.py
  tests/
    conftest.py
    test_health.py
    test_phase2.py
    test_phase3.py
frontend/
  .env.example
  package.json
  src/
    components/StatCard.tsx
    pages/
      AuthPage.tsx
      AdvancedFeatures.tsx
      PhaseThreeFeatures.tsx
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

The current frontend keeps dashboard, workout, goal, report, and notification screens in `App.tsx`; Phase 3 screens are in `PhaseThreeFeatures.tsx`. Tests are split by phase. Static `public/` and `assets/` directories are intentionally omitted until the app needs image or font assets.

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
8. Workout, meal, and hydration reminders respect per-user enablement, time zone, schedule, activity state, and once-per-day delivery.
9. Meal and water entries are validated, user-owned, and reflected in daily summaries; water progress uses each user's configured target.
10. Recommendations use each user's goals/activity/streak and disclose their reason without claiming an external AI integration.
11. The timer saves elapsed workout time and estimated calories as a normal workout entry.
12. Advanced analytics provide weekly trends, 30-day trends, consistency, and goal completion with charts.
13. Optional provider sync is clearly identified as not configured until credentials and consent flows exist.
14. Backend tests pass, frontend type-check/build passes, and README setup works on Windows PowerShell.

## Current project notes

The current implementation uses SQLAlchemy `create_all` for the starter database lifecycle; existing databases receive new tables but production schema evolution requires reviewed Alembic migrations. The reminder scheduler is in-process, so use one API worker or move reminders to a dedicated scheduler when scaling out.
