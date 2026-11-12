from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.goal import Goal
from app.models.workout import Workout


def compare_progress(db: Session, user: User, period: str, on_date: date) -> dict:
    if period == "weekly":
        current_start = on_date - timedelta(days=on_date.weekday())
        previous_start = current_start - timedelta(days=7)
        current_end = current_start + timedelta(days=6)
        previous_end = current_start - timedelta(days=1)
    else:
        current_start = on_date.replace(day=1)
        previous_end = current_start - timedelta(days=1)
        previous_start = previous_end.replace(day=1)
        current_end = date(
            current_start.year + (current_start.month == 12),
            1 if current_start.month == 12 else current_start.month + 1,
            1,
        ) - timedelta(days=1)

    def totals(start: date, end: date) -> dict:
        row = db.query(
            func.count(Workout.id),
            func.coalesce(func.sum(Workout.calories_burned), 0),
            func.coalesce(func.sum(Workout.duration), 0),
        ).filter(
            Workout.user_id == user.id,
            Workout.workout_date >= start,
            Workout.workout_date <= end,
        ).one()
        return {"workouts": row[0], "calories": int(row[1]), "duration": int(row[2])}

    current = totals(current_start, current_end)
    previous = totals(previous_start, previous_end)
    return {
        "period": period,
        "current": {"start_date": current_start, "end_date": current_end, **current},
        "previous": {"start_date": previous_start, "end_date": previous_end, **previous},
        "change": {key: current[key] - previous[key] for key in current},
    }


def advanced_analytics(db: Session, user: User, on_date: date) -> dict:
    thirty_day_start = on_date - timedelta(days=29)
    active_days = db.query(func.count(func.distinct(Workout.workout_date))).filter(
        Workout.user_id == user.id,
        Workout.workout_date >= thirty_day_start,
        Workout.workout_date <= on_date,
    ).scalar()
    goals_total = db.query(func.count(Goal.id)).filter(Goal.user_id == user.id).scalar()
    goals_completed = db.query(func.count(Goal.id)).filter(
        Goal.user_id == user.id, Goal.status == "COMPLETED",
    ).scalar()
    daily_rows = db.query(
        Workout.workout_date,
        func.count(Workout.id),
        func.coalesce(func.sum(Workout.calories_burned), 0),
        func.coalesce(func.sum(Workout.duration), 0),
    ).filter(
        Workout.user_id == user.id,
        Workout.workout_date >= thirty_day_start,
        Workout.workout_date <= on_date,
    ).group_by(Workout.workout_date).all()
    daily_totals = {
        row[0]: {"workouts": row[1], "calories": int(row[2]), "duration": int(row[3])}
        for row in daily_rows
    }

    weekly_trend = []
    current_week = on_date - timedelta(days=on_date.weekday())
    for offset in range(7, -1, -1):
        start = current_week - timedelta(weeks=offset)
        end = start + timedelta(days=6)
        row = db.query(
            func.count(Workout.id),
            func.coalesce(func.sum(Workout.calories_burned), 0),
            func.coalesce(func.sum(Workout.duration), 0),
        ).filter(
            Workout.user_id == user.id,
            Workout.workout_date >= start,
            Workout.workout_date <= end,
        ).one()
        weekly_trend.append({
            "start_date": start,
            "workouts": row[0],
            "calories": int(row[1]),
            "duration": int(row[2]),
        })

    return {
        "consistency": {
            "active_days": int(active_days or 0),
            "period_days": 30,
            "rate_percent": round((int(active_days or 0) / 30) * 100),
        },
        "goal_completion": {
            "completed": int(goals_completed or 0),
            "total": int(goals_total or 0),
            "rate_percent": round((int(goals_completed or 0) / int(goals_total)) * 100) if goals_total else 0,
        },
        "daily_trend": [
            {"date": thirty_day_start + timedelta(days=offset), **daily_totals.get(
                thirty_day_start + timedelta(days=offset),
                {"workouts": 0, "calories": 0, "duration": 0},
            )}
            for offset in range(30)
        ],
        "weekly_trend": weekly_trend,
    }
