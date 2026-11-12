from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.badge import UserBadge
from app.models.goal import Goal
from app.models.user import User
from app.models.workout import Workout
from app.models.workout_plan import WorkoutPlan
from app.services.badges import refresh_streak_and_badges


def get_dashboard_data(db: Session, user: User) -> dict:
    today = date.today()
    summary = db.query(
        func.count(Workout.id),
        func.coalesce(func.sum(Workout.calories_burned), 0),
        func.coalesce(func.sum(Workout.duration), 0),
    ).filter(Workout.user_id == user.id, Workout.workout_date == today).one()
    streak = refresh_streak_and_badges(db, user.id)
    db.commit()
    upcoming = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user.id, WorkoutPlan.scheduled_date >= today)
        .order_by(WorkoutPlan.scheduled_date, WorkoutPlan.id)
        .limit(5)
        .all()
    )
    goals = db.query(Goal).filter(Goal.user_id == user.id).order_by(Goal.created_at.desc()).all()
    earned = (
        db.query(UserBadge)
        .options(joinedload(UserBadge.badge))
        .filter(UserBadge.user_id == user.id)
        .order_by(UserBadge.earned_at.desc())
        .all()
    )
    return {
        "date": today,
        "daily_summary": {
            "total_workouts": summary[0],
            "total_calories": int(summary[1]),
            "total_duration": int(summary[2]),
        },
        "upcoming_workouts": upcoming,
        "goals": goals,
        "streak": streak,
        "badges": earned,
    }
