from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead

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

class NotificationRead(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProgressSummary(BaseModel):
    date: date
    total_workouts: int
    total_calories: int
    total_duration: int
