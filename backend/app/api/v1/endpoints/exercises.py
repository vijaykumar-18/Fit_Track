from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.exercise import Exercise
from app.models.workout_exercise import WorkoutExercise
from app.models.user import User
from app.models.workout import Workout
from app.schemas.exercise import ExerciseLinkCreate, ExerciseRead
from app.crud.exercise import search_exercises

router = APIRouter(tags=["Exercise Library"])


@router.get("/exercises", response_model=list[ExerciseRead])
def list_exercises(
    search: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, pattern="^(Cardio|Strength|Yoga)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return search_exercises(db, name=search, category=category)


@router.get("/workouts/{workout_id}/exercises", response_model=list[ExerciseRead])
def list_workout_exercises(
    workout_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workout = db.query(Workout).filter(Workout.id == workout_id, Workout.user_id == user.id).first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return (
        db.query(Exercise)
        .join(WorkoutExercise)
        .filter(WorkoutExercise.workout_id == workout_id)
        .order_by(Exercise.name)
        .all()
    )


@router.post("/workouts/{workout_id}/exercises", response_model=list[ExerciseRead], status_code=status.HTTP_200_OK)
def add_workout_exercise(
    workout_id: int,
    payload: ExerciseLinkCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workout = db.query(Workout).filter(Workout.id == workout_id, Workout.user_id == user.id).first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    exercise = db.query(Exercise).filter(Exercise.id == payload.exercise_id).first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    link = db.query(WorkoutExercise).filter_by(workout_id=workout_id, exercise_id=exercise.id).first()
    if link is None:
        db.add(WorkoutExercise(workout_id=workout_id, exercise_id=exercise.id))
        db.commit()
    return list_workout_exercises(workout_id, db, user)
