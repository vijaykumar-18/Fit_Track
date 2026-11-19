from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Nutritionist(Base):
    __tablename__ = "nutritionists"
    __table_args__ = (CheckConstraint("experience >= 0", name="ck_nutritionist_experience_nonnegative"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    specialization: Mapped[str] = mapped_column(String(120))
    experience: Mapped[int] = mapped_column(Integer)
    contact_info: Mapped[str] = mapped_column(String(255))


class Consultation(Base):
    __tablename__ = "consultations"
    __table_args__ = (
        CheckConstraint("status IN ('PENDING', 'CONFIRMED', 'CANCELLED')", name="ck_consultation_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    nutritionist_id: Mapped[int] = mapped_column(ForeignKey("nutritionists.id"), index=True)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    nutritionist = relationship("Nutritionist")
