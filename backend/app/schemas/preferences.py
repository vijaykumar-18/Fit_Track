from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PreferencesUpdate(BaseModel):
    timezone: str | None = Field(default=None, min_length=1, max_length=80)
    water_goal_ml: int | None = Field(default=None, ge=250, le=10000)
    workout_reminder_enabled: bool | None = None
    workout_reminder_time: str | None = Field(default=None, pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")
    meal_reminder_enabled: bool | None = None
    meal_reminder_time: str | None = Field(default=None, pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")
    water_reminder_enabled: bool | None = None
    water_reminder_time: str | None = Field(default=None, pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str | None) -> str | None:
        if value is not None:
            try:
                ZoneInfo(value)
            except (ZoneInfoNotFoundError, ValueError) as exc:
                raise ValueError("timezone must be a valid IANA timezone") from exc
        return value


class PreferencesRead(BaseModel):
    timezone: str
    water_goal_ml: int
    workout_reminder_enabled: bool
    workout_reminder_time: str
    meal_reminder_enabled: bool
    meal_reminder_time: str
    water_reminder_enabled: bool
    water_reminder_time: str

    model_config = ConfigDict(from_attributes=True)
