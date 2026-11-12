from datetime import date, datetime, timezone

from sqlalchemy import CheckConstraint, Date, DateTime, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Meal(Base):
    __tablename__ = "meals"
    __table_args__ = (
        CheckConstraint("calories >= 0", name="ck_meal_calories_nonnegative"),
        CheckConstraint("protein >= 0 AND carbs >= 0 AND fats >= 0", name="ck_meal_macros_nonnegative"),
        Index("ix_meals_user_date", "user_id", "meal_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    meal_type: Mapped[str] = mapped_column(String(20))
    food_name: Mapped[str] = mapped_column(String(120))
    calories: Mapped[int] = mapped_column()
    protein: Mapped[float] = mapped_column(Float, default=0)
    carbs: Mapped[float] = mapped_column(Float, default=0)
    fats: Mapped[float] = mapped_column(Float, default=0)
    meal_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
