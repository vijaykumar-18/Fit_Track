from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DietPlan(Base):
    __tablename__ = "diet_plans"
    __table_args__ = (
        CheckConstraint("daily_calories > 0", name="ck_diet_plan_calories_positive"),
        CheckConstraint("duration > 0", name="ck_diet_plan_duration_positive"),
        CheckConstraint(
            "goal_type IN ('Weight Loss', 'Muscle Gain', 'Maintenance')",
            name="ck_diet_plan_goal_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    goal_type: Mapped[str] = mapped_column(String(30), index=True)
    daily_calories: Mapped[int] = mapped_column(Integer)
    duration: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
