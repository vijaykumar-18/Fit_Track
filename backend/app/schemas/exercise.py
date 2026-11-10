from pydantic import BaseModel, ConfigDict

from app.schemas.workout import WorkoutCategory


class ExerciseRead(BaseModel):
    id: int
    name: str
    category: WorkoutCategory
    description: str
    duration: int

    model_config = ConfigDict(from_attributes=True)


class ExerciseLinkCreate(BaseModel):
    exercise_id: int
