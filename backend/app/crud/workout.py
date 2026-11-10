from sqlalchemy.orm import Session

from app.models.workout import Workout


def get_owned(db: Session, workout_id: int, user_id: int) -> Workout | None:
    return db.query(Workout).filter(Workout.id == workout_id, Workout.user_id == user_id).first()


def list_for_user(db: Session, user_id: int) -> list[Workout]:
    return (
        db.query(Workout)
        .filter(Workout.user_id == user_id)
        .order_by(Workout.workout_date.desc(), Workout.id.desc())
        .all()
    )
