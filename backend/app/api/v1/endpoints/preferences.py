from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.schemas.preferences import PreferencesRead, PreferencesUpdate

router = APIRouter(prefix="/settings", tags=["Settings & Reminders"])


def get_or_create_preferences(db: Session, user: User) -> UserPreferences:
    preferences = db.get(UserPreferences, user.id)
    if preferences is None:
        preferences = UserPreferences(user_id=user.id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    return preferences


@router.get("/reminders", response_model=PreferencesRead)
def read_preferences(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_or_create_preferences(db, user)


@router.patch("/reminders", response_model=PreferencesRead)
def update_preferences(
    payload: PreferencesUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    preferences = get_or_create_preferences(db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(preferences, field, value)
    db.commit()
    db.refresh(preferences)
    return preferences
