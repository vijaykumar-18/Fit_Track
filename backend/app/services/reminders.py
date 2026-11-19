import asyncio
import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func

from app.database.connection import SessionLocal
from app.models.meal import Meal
from app.models.notification import Notification
from app.models.appointment import Appointment
from app.models.nutritionist import Consultation
from app.models.subscription import UserSubscription
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
        subscription_deadline = current_time + timedelta(days=3)
        for item in db.query(UserSubscription).filter(
            UserSubscription.end_date > current_time,
            UserSubscription.end_date <= subscription_deadline,
        ).all():
            end_date = item.end_date
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
            message = f"Your subscription ends on {end_date.date().isoformat()}. Review your plan."
            exists = db.query(Notification.id).filter(
                Notification.user_id == item.user_id,
                Notification.title == "Subscription expiry alert",
                Notification.message == message,
            ).first()
            if not exists:
                db.add(Notification(
                    user_id=item.user_id,
                    title="Subscription expiry alert",
                    message=message,
                ))
        upcoming_cutoff = current_time + timedelta(hours=24)
        for booking in db.query(Consultation).filter(
            Consultation.scheduled_time > current_time,
            Consultation.scheduled_time <= upcoming_cutoff,
            Consultation.status.in_(("PENDING", "CONFIRMED")),
        ).all():
            scheduled_time = booking.scheduled_time
            message = f"You have a nutritionist consultation scheduled for {scheduled_time.isoformat()}."
            exists = db.query(Notification.id).filter(
                Notification.user_id == booking.user_id,
                Notification.title == "Consultation reminder",
                Notification.message == message,
            ).first()
            if not exists:
                db.add(Notification(
                    user_id=booking.user_id,
                    title="Consultation reminder",
                    message=message,
                ))
        for booking in db.query(Appointment).filter(
            Appointment.appointment_date > current_time,
            Appointment.appointment_date <= upcoming_cutoff,
            Appointment.status.in_(("PENDING", "CONFIRMED")),
        ).all():
            message = f"You have a doctor appointment scheduled for {booking.appointment_date.isoformat()}."
            exists = db.query(Notification.id).filter(
                Notification.user_id == booking.user_id,
                Notification.title == "Appointment reminder",
                Notification.message == message,
            ).first()
            if not exists:
                db.add(Notification(
                    user_id=booking.user_id,
                    title="Appointment reminder",
                    message=message,
                ))
        db.commit()


async def reminder_loop() -> None:
    while True:
        await asyncio.sleep(30)
        try:
            create_due_reminders()
        except Exception:
            logger.exception("Could not create scheduled user reminders")
