from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_subscription_price_nonnegative"),
        CheckConstraint("duration >= 0", name="ck_subscription_duration_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    price: Mapped[float] = mapped_column(Float)
    duration: Mapped[int] = mapped_column(Integer)
    features: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    __table_args__ = (
        CheckConstraint("end_date > start_date", name="ck_user_subscription_dates"),
        Index("ix_user_subscriptions_user_dates", "user_id", "start_date", "end_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"), index=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    subscription = relationship("Subscription")
