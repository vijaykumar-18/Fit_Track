from datetime import date, datetime, timezone

from app import main as app_module
from app.models.notification import Notification
from app.services import reminders
from conftest import register_and_login


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_meals_and_water_are_daily_and_owner_scoped(client):
    owner_token = register_and_login(client, "nutrition_owner")
    other_token = register_and_login(client, "nutrition_other")
    owner = headers(owner_token)
    other = headers(other_token)

    meal_response = client.post(
        "/api/nutrition/meals",
        headers=owner,
        json={
            "meal_type": "Breakfast",
            "food_name": "Oats",
            "calories": 320,
            "protein": 14,
            "carbs": 50,
            "fats": 8,
            "meal_date": str(date.today()),
        },
    )
    assert meal_response.status_code == 201
    meal = meal_response.json()
    assert client.get("/api/nutrition/summary", headers=owner).json()["calories"] == 320
    assert client.get("/api/nutrition/meals", headers=other).json() == []
    assert client.patch(f"/api/nutrition/meals/{meal['id']}", headers=other, json={"calories": 1}).status_code == 404

    water_response = client.post("/api/water", headers=owner, json={"quantity": 500, "date": str(date.today())})
    assert water_response.status_code == 201
    water = water_response.json()
    summary = client.get("/api/water", headers=owner).json()
    assert summary["total_ml"] == 500
    assert summary["goal_ml"] == 2000
    assert summary["progress_percent"] == 25
    assert client.get("/api/water", headers=other).json()["total_ml"] == 0
    assert client.delete(f"/api/water/{water['id']}", headers=other).status_code == 404


def test_reminder_preferences_validate_and_schedule_once_per_local_day(client, monkeypatch):
    token = register_and_login(client, "reminder_user")
    owner = headers(token)
    saved = client.patch(
        "/api/settings/reminders",
        headers=owner,
        json={
            "timezone": "UTC",
            "water_goal_ml": 1500,
            "workout_reminder_time": "00:00",
            "meal_reminder_enabled": True,
            "meal_reminder_time": "00:00",
            "water_reminder_enabled": True,
            "water_reminder_time": "00:00",
        },
    )
    assert saved.status_code == 200
    assert saved.json()["water_goal_ml"] == 1500
    assert client.patch("/api/settings/reminders", headers=owner, json={"timezone": "Not/AZone"}).status_code == 422
    assert client.patch("/api/settings/reminders", headers=owner, json={"meal_reminder_time": "25:61"}).status_code == 422

    monkeypatch.setattr(reminders, "SessionLocal", app_module.SessionLocal)
    reminders.create_due_reminders(datetime.now(timezone.utc))
    reminders.create_due_reminders(datetime.now(timezone.utc))
    items = client.get("/api/notifications", headers=owner).json()
    titles = [item["title"] for item in items]
    assert titles.count("Daily workout reminder") == 1
    assert titles.count("Meal reminder") == 1
    assert titles.count("Hydration reminder") == 1


def test_recommendations_and_advanced_analytics_are_personalized(client):
    token = register_and_login(client, "insights_user")
    owner = headers(token)
    workout = client.post(
        "/api/workouts",
        headers=owner,
        json={
            "workout_name": "Evening strength",
            "category": "Strength",
            "duration": 40,
            "calories_burned": 250,
            "workout_date": str(date.today()),
        },
    )
    assert workout.status_code == 201
    goal = client.post(
        "/api/goals",
        headers=owner,
        json={"goal_type": "Muscle Gain", "target_value": 5, "current_value": 1},
    )
    assert goal.status_code == 201

    recommendations = client.get("/api/recommendations", headers=owner)
    assert recommendations.status_code == 200
    assert recommendations.json()
    assert any(item["exercise"]["category"] == "Strength" for item in recommendations.json())

    analytics = client.get("/api/analytics/advanced", headers=owner)
    assert analytics.status_code == 200
    assert analytics.json()["consistency"]["active_days"] == 1
    assert analytics.json()["consistency"]["rate_percent"] == 3
    assert analytics.json()["goal_completion"]["rate_percent"] == 0
    assert len(analytics.json()["weekly_trend"]) == 8
    assert len(analytics.json()["daily_trend"]) == 30
