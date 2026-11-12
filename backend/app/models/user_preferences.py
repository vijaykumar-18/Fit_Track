from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    timezone: Mapped[str] = mapped_column(String(80), default="UTC")
    water_goal_ml: Mapped[int] = mapped_column(Integer, default=2000)
    workout_reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    workout_reminder_time: Mapped[str] = mapped_column(String(5), default="09:00")
    meal_reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    meal_reminder_time: Mapped[str] = mapped_column(String(5), default="12:00")
    water_reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    water_reminder_time: Mapped[str] = mapped_column(String(5), default="15:00")
    last_workout_reminder_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_meal_reminder_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_water_reminder_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
