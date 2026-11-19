from datetime import date, datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_serializer, field_validator
from typing import Annotated

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class DietGoal(str, Enum):
    WEIGHT_LOSS = "Weight Loss"
    MUSCLE_GAIN = "Muscle Gain"
    MAINTENANCE = "Maintenance"


class DietPlanRead(BaseModel):
    id: int
    title: str
    description: str
    goal_type: DietGoal
    daily_calories: int
    duration: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDietPlanRead(BaseModel):
    id: int
    user_id: int
    diet_plan_id: int
    assigned_at: datetime
    diet_plan: DietPlanRead

    model_config = ConfigDict(from_attributes=True)


class DietRecommendation(BaseModel):
    diet_plan: DietPlanRead
    reason: str


class SubscriptionRead(BaseModel):
    id: int
    name: str
    price: float
    duration: int
    features: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSubscriptionRead(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    start_date: datetime
    end_date: datetime
    subscription: SubscriptionRead

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("start_date", "end_date")
    def serialize_subscription_dates(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()


class NutritionistRead(BaseModel):
    id: int
    name: str
    specialization: str
    experience: int
    contact_info: str

    model_config = ConfigDict(from_attributes=True)


class ConsultationCreate(BaseModel):
    nutritionist_id: int = Field(gt=0)
    scheduled_time: datetime

    @field_validator("scheduled_time")
    @classmethod
    def require_future_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value <= datetime.now(timezone.utc):
            raise ValueError("scheduled_time must be a future datetime with a timezone")
        return value


class ConsultationRead(BaseModel):
    id: int
    user_id: int
    nutritionist_id: int
    scheduled_time: datetime
    status: str
    created_at: datetime
    nutritionist: NutritionistRead

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("scheduled_time")
    def serialize_scheduled_time(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()


class DoctorRead(BaseModel):
    id: int
    name: str
    specialization: str
    experience: int
    contact_info: str
    availability_status: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    appointment_date: date
    time_slot: Annotated[str, StringConstraints(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$", strip_whitespace=True)]

    @field_validator("appointment_date")
    @classmethod
    def require_future_date(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("appointment_date cannot be in the past")
        return value


class AppointmentRead(BaseModel):
    id: int
    user_id: int
    doctor_id: int
    appointment_date: datetime
    time_slot: str
    status: str
    created_at: datetime
    doctor: DoctorRead

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("appointment_date")
    def serialize_appointment_date(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
