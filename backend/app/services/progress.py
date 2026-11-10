from datetime import date
from collections.abc import Iterable

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.progress import Progress
from app.models.workout import Workout


def refresh_progress(db: Session, user_id: int, workout_dates: Iterable[date]) -> None:
    for workout_date in set(workout_dates):
        totals = db.query(
            func.count(Workout.id),
            func.coalesce(func.sum(Workout.calories_burned), 0),
        ).filter(
            Workout.user_id == user_id,
            Workout.workout_date == workout_date,
        ).one()
        summary = db.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.date == workout_date,
        ).first()
        if totals[0] == 0:
            if summary is not None:
                db.delete(summary)
        elif summary is None:
            db.add(Progress(
                user_id=user_id,
                date=workout_date,
                total_workouts=totals[0],
                total_calories=int(totals[1]),
            ))
        else:
            summary.total_workouts = totals[0]
            summary.total_calories = int(totals[1])


def rebuild_progress(db: Session) -> None:
    rows = db.query(
        Workout.user_id,
        Workout.workout_date,
        func.count(Workout.id),
        func.coalesce(func.sum(Workout.calories_burned), 0),
    ).group_by(Workout.user_id, Workout.workout_date).all()
    existing = {
        (row.user_id, row.date): row
        for row in db.query(Progress).all()
    }
    active_keys = set()
    for user_id, workout_date, total_workouts, total_calories in rows:
        key = (user_id, workout_date)
        active_keys.add(key)
        summary = existing.get(key)
        if summary is None:
            summary = Progress(user_id=user_id, date=workout_date)
            db.add(summary)
        summary.total_workouts = total_workouts
        summary.total_calories = int(total_calories)
    for key, summary in existing.items():
        if key not in active_keys:
            db.delete(summary)
