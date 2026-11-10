from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkoutPlanCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=2000)
    scheduled_date: date


class WorkoutPlanUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    scheduled_date: date | None = None


class WorkoutPlanRead(WorkoutPlanCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
