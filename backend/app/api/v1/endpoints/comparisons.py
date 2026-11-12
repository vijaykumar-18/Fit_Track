from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.analytics import advanced_analytics, compare_progress as compare_periods

router = APIRouter(tags=["Progress Comparisons"])


@router.get("/progress/comparison")
def compare_progress(
    period: str = Query(default="weekly", pattern="^(weekly|monthly)$"),
    on_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return compare_periods(db, user, period, on_date)


@router.get("/analytics/advanced")
def get_advanced_analytics(
    on_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return advanced_analytics(db, user, on_date)
