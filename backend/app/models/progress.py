from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_progress_user_date"),
        CheckConstraint("total_workouts >= 0", name="ck_progress_workouts_nonnegative"),
        CheckConstraint("total_calories >= 0", name="ck_progress_calories_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    total_workouts: Mapped[int] = mapped_column(Integer, default=0)
    total_calories: Mapped[int] = mapped_column(Integer, default=0)
