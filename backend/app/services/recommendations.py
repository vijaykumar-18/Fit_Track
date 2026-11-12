from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.goal import Goal
from app.models.streak import Streak
from app.models.workout import Workout


GOAL_CATEGORY = {
    "Weight Loss": "Cardio",
    "Muscle Gain": "Strength",
    "Steps": "Cardio",
}


def recommend_workouts(db: Session, user_id: int) -> list[dict]:
    today = date.today()
    recent_counts = dict(db.query(Workout.category, func.count(Workout.id)).filter(
        Workout.user_id == user_id,
        Workout.workout_date >= today - timedelta(days=30),
    ).group_by(Workout.category).all())
    goal = db.query(Goal).filter(
        Goal.user_id == user_id, Goal.status != "COMPLETED",
    ).order_by(Goal.created_at.desc()).first()
    streak = db.query(Streak).filter(Streak.user_id == user_id).first()
    goal_category = GOAL_CATEGORY.get(goal.goal_type) if goal else None
    exercises = db.query(Exercise).all()
    exercises.sort(key=lambda exercise: (
        exercise.category != goal_category if goal_category else False,
        recent_counts.get(exercise.category, 0),
        exercise.name,
    ))

    recommendations = []
    for exercise in exercises[:3]:
        if goal and exercise.category == goal_category:
            reason = f"Supports your {goal.goal_type.lower()} goal."
        elif recent_counts.get(exercise.category, 0) == 0:
            reason = "Adds variety to your recent workout routine."
        else:
            reason = "A practical next session based on your recent activity."
        if streak and streak.current_streak > 0:
            reason += " A short session can help maintain your current streak."
        recommendations.append({"exercise": exercise, "reason": reason})
    return recommendations
