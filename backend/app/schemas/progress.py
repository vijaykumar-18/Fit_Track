from datetime import date

from pydantic import BaseModel


class ProgressSummary(BaseModel):
    date: date
    total_workouts: int
    total_calories: int
    total_duration: int
