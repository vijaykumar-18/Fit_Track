from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, badges, comparisons, dashboard, exercises, goals, notifications, reports,
    streaks, workout_plans, workouts,
)

router = APIRouter()

router.include_router(auth.router)
router.include_router(workouts.router)
router.include_router(goals.router)
router.include_router(reports.router)
router.include_router(notifications.router)
router.include_router(workout_plans.router)
router.include_router(exercises.router)
router.include_router(comparisons.router)
router.include_router(streaks.router)
router.include_router(badges.router)
router.include_router(dashboard.router)
