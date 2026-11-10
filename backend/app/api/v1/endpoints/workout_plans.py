from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.workout_plan import WorkoutPlan
from app.models.user import User
from app.schemas.workout_plan import WorkoutPlanCreate, WorkoutPlanRead, WorkoutPlanUpdate
from app.crud.workout_plan import get_owned, list_for_user

router = APIRouter(prefix="/plans", tags=["Workout Plans"])


@router.post("", response_model=WorkoutPlanRead, status_code=status.HTTP_201_CREATED)
def create_plan(payload: WorkoutPlanCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plan = WorkoutPlan(user_id=user.id, **payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("", response_model=list[WorkoutPlanRead])
def list_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_for_user(db, user.id)


@router.get("/{plan_id}", response_model=WorkoutPlanRead)
def get_plan(plan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plan = get_owned(db, plan_id, user.id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    return plan


@router.patch("/{plan_id}", response_model=WorkoutPlanRead)
def update_plan(
    plan_id: int,
    payload: WorkoutPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plan = get_owned(db, plan_id, user.id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plan = get_owned(db, plan_id, user.id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    db.delete(plan)
    db.commit()
