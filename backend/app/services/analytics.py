from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
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
