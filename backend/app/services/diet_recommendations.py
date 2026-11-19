from sqlalchemy.orm import Session

from app.crud.phase4 import get_active_goal
from app.models.diet_plan import DietPlan


ACTIVITY_CALORIE_ADJUSTMENT = {"Low": -150, "Moderate": 0, "High": 200}


def recommend_diet_plans(
    db: Session,
    user_id: int,
    daily_calories: int,
    activity_level: str,
    requested_goal: str | None,
) -> list[dict]:
    active_goal = get_active_goal(db, user_id) if requested_goal is None else None
    goal = requested_goal or (active_goal.goal_type if active_goal else "Maintenance")
    target_calories = daily_calories + ACTIVITY_CALORIE_ADJUSTMENT[activity_level]
    plans = db.query(DietPlan).all()
    plans.sort(key=lambda plan: (
        plan.goal_type != goal,
        abs(plan.daily_calories - target_calories),
        plan.title,
    ))
    results = []
    for plan in plans[:3]:
        goal_text = "matches your selected goal" if plan.goal_type == goal else "is an alternative goal option"
        difference = abs(plan.daily_calories - target_calories)
        calorie_text = "matches your calorie target" if difference <= 150 else f"is {difference} kcal from your adjusted target"
        results.append({
            "diet_plan": plan,
            "reason": f"This plan {goal_text} and {calorie_text} for a {activity_level.lower()} activity level.",
        })
    return results
