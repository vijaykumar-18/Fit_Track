from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.badge import Badge, UserBadge
from app.models.user import User
from app.schemas.engagement import UserBadgeRead
from app.services.badges import refresh_streak_and_badges

router = APIRouter(prefix="/badges", tags=["Badges"])


@router.get("", response_model=list[UserBadgeRead])
def list_badges(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    refresh_streak_and_badges(db, user.id)
    db.commit()
    return (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user.id)
        .order_by(UserBadge.earned_at.desc())
        .all()
    )


@router.get("/catalog")
def badge_catalog(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Badge).order_by(Badge.category, Badge.threshold).all()
