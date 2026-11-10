from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate, WorkoutRead, WorkoutUpdate
from app.services.badges import refresh_streak_and_badges
from app.services.progress import refresh_progress
from app.crud.workout import get_owned, list_for_user

router = APIRouter(prefix="/workouts", tags=["Workouts"])

@router.post("", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(payload: WorkoutCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workout = Workout(user_id=user.id, **payload.model_dump())
    db.add(workout)
    db.flush()
    refresh_progress(db, user.id, [workout.workout_date])
    refresh_streak_and_badges(db, user.id)
    db.commit()
    db.refresh(workout)
    return workout

@router.get("", response_model=list[WorkoutRead])
def list_workouts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_for_user(db, user.id)

@router.get("/{workout_id}", response_model=WorkoutRead)
def get_workout(workout_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workout = get_owned(db, workout_id, user.id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

@router.patch("/{workout_id}", response_model=WorkoutRead)
def update_workout(workout_id: int, payload: WorkoutUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workout = get_owned(db, workout_id, user.id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    previous_date = workout.workout_date
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(workout, key, value)
    db.flush()
    refresh_progress(db, user.id, [previous_date, workout.workout_date])
    refresh_streak_and_badges(db, user.id)
    db.commit()
    db.refresh(workout)
    return workout

@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workout = get_owned(db, workout_id, user.id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    workout_date = workout.workout_date
    db.delete(workout)
    db.flush()
    refresh_progress(db, user.id, [workout_date])
    refresh_streak_and_badges(db, user.id)
    db.commit()
