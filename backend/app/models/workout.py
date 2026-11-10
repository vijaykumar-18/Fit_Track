from datetime import date, datetime, timezone
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Workout(Base):
    __tablename__ = "workouts"
    __table_args__ = (
        CheckConstraint("duration > 0", name="ck_workout_duration_positive"),
        CheckConstraint("calories_burned >= 0", name="ck_workout_calories_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    workout_name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(20))
    duration: Mapped[int] = mapped_column(Integer)
    calories_burned: Mapped[int] = mapped_column(Integer, default=0)
    workout_date: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="workouts")
    exercise_links = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")
