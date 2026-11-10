import asyncio
import logging
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from app.database.connection import SessionLocal
from app.models.notification import Notification
from app.models.user import User
from app.models.workout import Workout

logger = logging.getLogger(__name__)


def create_daily_reminders() -> None:
    from app.core.config import settings

    tz = ZoneInfo(settings.reminder_timezone)
    now = datetime.now(tz)
    start = datetime.combine(now.date(), time.min, tzinfo=tz).astimezone(timezone.utc)
    end = datetime.combine(now.date() + timedelta(days=1), time.min, tzinfo=tz).astimezone(timezone.utc)
    with SessionLocal() as db:
        user_ids = [user_id for (user_id,) in db.query(User.id).all()]
        for user_id in user_ids:
            has_workout = db.query(Workout.id).filter(
                Workout.user_id == user_id,
                Workout.workout_date == now.date(),
            ).first()
            already_notified = db.query(Notification.id).filter(
                Notification.user_id == user_id,
                Notification.title == "Daily workout reminder",
                Notification.created_at >= start,
                Notification.created_at < end,
            ).first()
            if not has_workout and not already_notified:
                db.add(Notification(
                    user_id=user_id,
                    title="Daily workout reminder",
                    message="Make time for movement today and keep building your routine.",
                ))
        db.commit()


async def daily_reminder_loop(hour: int, minute: int, timezone_name: str) -> None:
    tz = ZoneInfo(timezone_name)
    while True:
        now = datetime.now(tz)
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        await asyncio.sleep((next_run - now).total_seconds())
        try:
            create_daily_reminders()
        except Exception:
            logger.exception("Could not create scheduled daily workout reminders")
