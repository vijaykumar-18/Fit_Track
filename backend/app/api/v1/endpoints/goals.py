from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.goal import Goal
from app.models.notification import Notification
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate
from app.services.badges import refresh_streak_and_badges
from app.crud.goal import get_owned, list_for_user

router = APIRouter(prefix="/goals", tags=["Goals"])

def refresh_status(goal: Goal):
    goal.status = "COMPLETED" if goal.current_value >= goal.target_value else "IN_PROGRESS"

@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = Goal(user_id=user.id, **payload.model_dump())
    refresh_status(goal)
    db.add(goal)
    db.flush()
    refresh_streak_and_badges(db, user.id)
    db.commit()
    db.refresh(goal)
    return goal

@router.get("", response_model=list[GoalRead])
def list_goals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_for_user(db, user.id)

@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(goal_id: int, payload: GoalUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = get_owned(db, goal_id, user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    previous_status = goal.status
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, key, value)
    refresh_status(goal)
    if goal.status == "COMPLETED" and previous_status != "COMPLETED":
        db.add(Notification(user_id=user.id, title="Goal achieved!", message=f"Congratulations! You completed your {goal.goal_type} goal."))
    refresh_streak_and_badges(db, user.id)
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = get_owned(db, goal_id, user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
