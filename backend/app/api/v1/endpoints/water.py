from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.nutrition import get_water, list_water, water_total
from app.database.connection import get_db
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.models.water_tracking import WaterTracking
from app.schemas.nutrition import WaterCreate, WaterRead, WaterSummary

router = APIRouter(prefix="/water", tags=["Hydration"])


@router.get("", response_model=WaterSummary)
def water_summary(
    on_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    preferences = db.get(UserPreferences, user.id)
    goal = preferences.water_goal_ml if preferences else 2000
    entries = list_water(db, user.id, on_date)
    total = sum(entry.quantity for entry in entries)
    return {
        "date": on_date,
        "total_ml": total,
        "goal_ml": goal,
        "progress_percent": min(100, round(total / goal * 100)),
        "entries": entries,
    }


@router.post("", response_model=WaterRead, status_code=status.HTTP_201_CREATED)
def log_water(payload: WaterCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entry = WaterTracking(user_id=user.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_water(entry_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entry = get_water(db, entry_id, user.id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Water entry not found")
    db.delete(entry)
    db.commit()
