from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.streak import Streak
from app.models.workout import Workout


def refresh_streak(db: Session, user_id: int) -> Streak:
    today = date.today()
    dates = [
        row[0]
        for row in db.query(Workout.workout_date)
        .filter(Workout.user_id == user_id, Workout.workout_date <= today)
        .distinct()
        .order_by(Workout.workout_date.desc())
        .all()
    ]

    current = 0
    longest = 0
    if dates:
        last_date = dates[0]
        expected = last_date
        for workout_date in dates:
            if workout_date != expected:
                break
            current += 1
            expected -= timedelta(days=1)

        run = 1
        for previous, workout_date in zip(dates, dates[1:]):
            if previous - workout_date == timedelta(days=1):
                run += 1
            else:
                longest = max(longest, run)
                run = 1
        longest = max(longest, run)
        if last_date < today - timedelta(days=1):
            current = 0
    else:
        last_date = None

    streak = db.query(Streak).filter(Streak.user_id == user_id).first()
    if streak is None:
        streak = Streak(user_id=user_id)
        db.add(streak)
    streak.current_streak = current
    streak.longest_streak = max(longest, streak.longest_streak or 0)
    streak.last_workout_date = last_date
    return streak
