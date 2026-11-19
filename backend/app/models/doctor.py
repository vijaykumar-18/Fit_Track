from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Doctor(Base):
    __tablename__ = "doctors"
    __table_args__ = (CheckConstraint("experience >= 0", name="ck_doctor_experience_nonnegative"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    specialization: Mapped[str] = mapped_column(String(40))
    experience: Mapped[int] = mapped_column(Integer)
    contact_info: Mapped[str] = mapped_column(String(255))
    availability_status: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
