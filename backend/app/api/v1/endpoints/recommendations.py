from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.recommendations import recommend_workouts

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("")
def get_recommendations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return recommend_workouts(db, user.id)
