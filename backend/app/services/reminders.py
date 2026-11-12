import asyncio
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func

from app.database.connection import SessionLocal
from app.models.meal import Meal
from app.models.notification import Notification
from app.models.user_preferences import UserPreferences
from app.models.water_tracking import WaterTracking
from app.models.workout import Workout

logger = logging.getLogger(__name__)


def create_due_reminders(now: datetime | None = None) -> None:
    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    with SessionLocal() as db:
        preferences = db.query(UserPreferences).all()
        for preference in preferences:
            local_now = current_time.astimezone(ZoneInfo(preference.timezone))
            local_date = local_now.date()
            local_time = local_now.strftime("%H:%M")
            reminder_rules = (
                ("workout", preference.workout_reminder_enabled, preference.workout_reminder_time,
                 preference.last_workout_reminder_date, "Daily workout reminder",
                 "Make time for movement today and keep building your routine."),
                ("meal", preference.meal_reminder_enabled, preference.meal_reminder_time,
                 preference.last_meal_reminder_date, "Meal reminder",
                 "Take a moment to log your meal and keep your nutrition goals in view."),
                ("water", preference.water_reminder_enabled, preference.water_reminder_time,
                 preference.last_water_reminder_date, "Hydration reminder",
                 "Log a glass of water and keep making progress toward your hydration goal."),
            )
            for kind, enabled, reminder_time, last_date, title, message in reminder_rules:
                if not enabled or local_time < reminder_time or last_date == local_date:
                    continue
                setattr(preference, f"last_{kind}_reminder_date", local_date)
                if kind == "workout":
                    completed = db.query(Workout.id).filter(
                        Workout.user_id == preference.user_id,
                        Workout.workout_date == local_date,
                    ).first()
                elif kind == "meal":
                    completed = db.query(Meal.id).filter(
                        Meal.user_id == preference.user_id,
                        Meal.meal_date == local_date,
                    ).first()
                else:
                    total = db.query(func.coalesce(func.sum(WaterTracking.quantity), 0)).filter(
                        WaterTracking.user_id == preference.user_id,
                        WaterTracking.date == local_date,
                    ).scalar()
                    completed = int(total) >= preference.water_goal_ml
                if not completed:
                    db.add(Notification(user_id=preference.user_id, title=title, message=message))
        db.commit()


async def reminder_loop() -> None:
    while True:
        await asyncio.sleep(30)
        try:
            create_due_reminders()
        except Exception:
            logger.exception("Could not create scheduled user reminders")
