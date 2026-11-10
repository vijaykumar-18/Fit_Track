from sqlalchemy.orm import Session

from app.models.workout_plan import WorkoutPlan


def get_owned(db: Session, plan_id: int, user_id: int) -> WorkoutPlan | None:
    return db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == user_id,
    ).first()


def list_for_user(db: Session, user_id: int) -> list[WorkoutPlan]:
    return (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user_id)
        .order_by(WorkoutPlan.scheduled_date, WorkoutPlan.id)
        .all()
    )
