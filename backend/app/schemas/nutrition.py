from datetime import date as Date, datetime
from enum import Enum

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

FoodName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class MealType(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    SNACKS = "Snacks"


class MealCreate(BaseModel):
    meal_type: MealType
    food_name: FoodName
    calories: int = Field(ge=0, le=10000)
    protein: float = Field(default=0, ge=0, le=1000)
    carbs: float = Field(default=0, ge=0, le=1000)
    fats: float = Field(default=0, ge=0, le=1000)
    meal_date: Date = Field(default_factory=Date.today)


class MealUpdate(BaseModel):
    meal_type: MealType | None = None
    food_name: FoodName | None = None
    calories: int | None = Field(default=None, ge=0, le=10000)
    protein: float | None = Field(default=None, ge=0, le=1000)
    carbs: float | None = Field(default=None, ge=0, le=1000)
    fats: float | None = Field(default=None, ge=0, le=1000)
    meal_date: Date | None = None


class MealRead(BaseModel):
    id: int
    user_id: int
    meal_type: MealType
    food_name: str
    calories: int
    protein: float
    carbs: float
    fats: float
    meal_date: Date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WaterCreate(BaseModel):
    quantity: int = Field(gt=0, le=5000)
    date: Date = Field(default_factory=Date.today)


class WaterRead(BaseModel):
    id: int
    user_id: int
    quantity: int
    date: Date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WaterSummary(BaseModel):
    date: Date
    total_ml: int
    goal_ml: int
    progress_percent: int
    entries: list[WaterRead]
