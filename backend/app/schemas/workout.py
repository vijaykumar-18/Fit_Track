from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class WorkoutCategory(str, Enum):
    cardio = "Cardio"
    strength = "Strength"
    yoga = "Yoga"


class WorkoutBase(BaseModel):
    workout_name: str = Field(min_length=2, max_length=120)
    category: WorkoutCategory
    duration: int = Field(gt=0, le=1440)
    calories_burned: int = Field(ge=0, le=20000)
    workout_date: date


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutUpdate(BaseModel):
    workout_name: str | None = Field(default=None, min_length=2, max_length=120)
    category: WorkoutCategory | None = None
    duration: int | None = Field(default=None, gt=0, le=1440)
    calories_burned: int | None = Field(default=None, ge=0, le=20000)
    workout_date: date | None = None


class WorkoutRead(WorkoutBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
