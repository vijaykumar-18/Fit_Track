from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class UserDietPlan(Base):
    __tablename__ = "user_diet_plans"
    __table_args__ = (
        Index("ix_user_diet_plans_user_assigned", "user_id", "assigned_at"),
        UniqueConstraint("user_id", "diet_plan_id", name="uq_user_diet_plan"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    diet_plan_id: Mapped[int] = mapped_column(ForeignKey("diet_plans.id", ondelete="CASCADE"), index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    diet_plan = relationship("DietPlan")
