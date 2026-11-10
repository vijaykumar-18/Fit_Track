from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.badge import Badge, UserBadge
from app.models.goal import Goal
from app.models.notification import Notification
from app.models.workout import Workout
from app.services.streak import refresh_streak

DEFAULT_BADGES = (
    ("First Workout", "Log your first workout.", "Dumbbell", 1, "workouts"),
    ("Ten Workouts", "Complete ten workouts.", "Medal", 10, "workouts"),
    ("Fifty Workouts", "Complete fifty workouts.", "Trophy", 50, "workouts"),
    ("Week of Consistency", "Work out on seven consecutive days.", "Flame", 7, "streak"),
    ("Goal Getter", "Complete your first fitness goal.", "Flag", 1, "goals"),
)


def seed_badges(db: Session) -> None:
    existing = {name for (name,) in db.query(Badge.name).all()}
    for name, description, icon, threshold, category in DEFAULT_BADGES:
        if name not in existing:
            db.add(Badge(name=name, description=description, icon=icon, threshold=threshold, category=category))
    db.commit()


def refresh_streak_and_badges(db: Session, user_id: int):
    streak = refresh_streak(db, user_id)
    workout_count = db.query(func.count(Workout.id)).filter(Workout.user_id == user_id).scalar() or 0
    completed_goal_count = db.query(func.count(Goal.id)).filter(
        Goal.user_id == user_id, Goal.status == "COMPLETED"
    ).scalar() or 0
    badges = db.query(Badge).all()
    earned_ids = {
        badge_id
        for (badge_id,) in db.query(UserBadge.badge_id).filter(UserBadge.user_id == user_id).all()
    }

    for badge in badges:
        if badge.category == "workouts":
            achieved = workout_count >= badge.threshold
        elif badge.category == "goals":
            achieved = completed_goal_count >= badge.threshold
        else:
            achieved = streak.longest_streak >= badge.threshold
        if achieved and badge.id not in earned_ids:
            db.add(UserBadge(user_id=user_id, badge_id=badge.id))
            db.add(Notification(
                user_id=user_id,
                title="New achievement!",
                message=f"You earned the {badge.name} badge.",
            ))
    return streak
