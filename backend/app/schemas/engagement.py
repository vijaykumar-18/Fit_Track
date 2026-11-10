from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class StreakRead(BaseModel):
    current_streak: int
    longest_streak: int
    last_workout_date: date | None


class BadgeRead(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    category: str


class UserBadgeRead(BaseModel):
    badge: BadgeRead
    earned_at: datetime

    model_config = ConfigDict(from_attributes=True)
