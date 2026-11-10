from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class GoalType(str, Enum):
    weight_loss = "Weight Loss"
    muscle_gain = "Muscle Gain"
    steps = "Steps"


class GoalCreate(BaseModel):
    goal_type: GoalType
    target_value: float = Field(gt=0, le=100000000)
    current_value: float = Field(default=0, ge=0, le=100000000)
    deadline: date | None = None


class GoalUpdate(BaseModel):
    target_value: float | None = Field(default=None, gt=0, le=100000000)
    current_value: float | None = Field(default=None, ge=0, le=100000000)
    deadline: date | None = None


class GoalRead(BaseModel):
    id: int
    user_id: int
    goal_type: GoalType
    target_value: float
    current_value: float
    deadline: date | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
