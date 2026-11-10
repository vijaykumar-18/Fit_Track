from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.dashboard import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def personalized_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_dashboard_data(db, user)
