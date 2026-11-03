from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.workout import Workout
from app.schemas import WorkoutCreate, WorkoutRead, WorkoutUpdate

router = APIRouter(prefix="/workouts", tags=["Workouts"])

@router.post("", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(payload: WorkoutCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workout = Workout(user_id=user.id, **payload.model_dump())
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout

@router.get("", response_model=list[WorkoutRead])
def list_workouts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Workout).filter(Workout.user_id == user.id).order_by(Workout.workout_date.desc(), Workout.id.desc()).all()

@router.get("/{workout_id}", response_model=WorkoutRead)
def get_workout(workout_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workout = db.query(Workout).filter(Workout.id == workout_id, Workout.user_id == user.id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

@router.patch("/{workout_id}", response_model=WorkoutRead)
def update_workout(workout_id: int, payload: WorkoutUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workout = db.query(Workout).filter(Workout.id == workout_id, Workout.user_id == user.id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(workout, key, value)
    db.commit()
    db.refresh(workout)
    return workout

@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    workout = db.query(Workout).filter(Workout.id == workout_id, Workout.user_id == user.id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(workout)
    db.commit()
