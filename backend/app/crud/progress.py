from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.workout import Workout


def totals_for_date(db: Session, user_id: int, workout_date: date):
    return db.query(
        func.count(Workout.id),
        func.coalesce(func.sum(Workout.calories_burned), 0),
        func.coalesce(func.sum(Workout.duration), 0),
    ).filter(
        Workout.user_id == user_id,
        Workout.workout_date == workout_date,
    ).one()
