from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.engagement import StreakRead
from app.services.badges import refresh_streak_and_badges

router = APIRouter(prefix="/streak", tags=["Streaks"])


@router.get("", response_model=StreakRead)
def get_streak(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    streak = refresh_streak_and_badges(db, user.id)
    db.commit()
    db.refresh(streak)
    return streak
