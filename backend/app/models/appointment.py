from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint("status IN ('PENDING', 'CONFIRMED', 'CANCELLED')", name="ck_appointment_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), index=True)
    appointment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    time_slot: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    doctor = relationship("Doctor")
