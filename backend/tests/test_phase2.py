from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.models.badge import Badge, UserBadge
from app.models.progress import Progress
from app.models.user import User
from app.models.workout import Workout
from app.services.badges import refresh_streak_and_badges, seed_badges
from app.services.progress import refresh_progress

from conftest import register_and_login


def test_workout_plan_is_private_and_editable(client):
    owner_token = register_and_login(client, "owner_user")
    other_token = register_and_login(client, "other_user")
    owner = {"Authorization": f"Bearer {owner_token}"}
    other = {"Authorization": f"Bearer {other_token}"}

    response = client.post(
        "/api/plans",
        headers=owner,
        json={"title": "Strength day", "description": "Upper body", "scheduled_date": str(date.today() + timedelta(days=1))},
    )
    assert response.status_code == 201
    plan_id = response.json()["id"]

    assert client.get(f"/api/plans/{plan_id}", headers=other).status_code == 404
    update = client.patch(f"/api/plans/{plan_id}", headers=owner, json={"title": "Updated session"})
    assert update.status_code == 200
    assert update.json()["title"] == "Updated session"
    assert client.get("/api/plans", headers=other).json() == []


def test_progress_comparison_and_personalized_dashboard(client):
    token = register_and_login(client, "dashboard_user")
    headers = {"Authorization": f"Bearer {token}"}
    workout = client.post(
        "/api/workouts",
        headers=headers,
        json={
            "workout_name": "Morning run",
            "category": "Cardio",
            "duration": 30,
            "calories_burned": 250,
            "workout_date": str(date.today()),
        },
    )
    assert workout.status_code == 201
    dashboard = client.get("/api/dashboard", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["daily_summary"]["total_workouts"] == 1
    assert client.get("/api/progress/comparison?period=weekly", headers=headers).status_code == 200
    assert client.get("/api/progress/comparison?period=monthly", headers=headers).status_code == 200


def test_workout_and_exercise_links_are_owner_scoped(client):
    owner_token = register_and_login(client, "workout_owner")
    other_token = register_and_login(client, "workout_other")
    owner = {"Authorization": f"Bearer {owner_token}"}
    other = {"Authorization": f"Bearer {other_token}"}
    workout = client.post(
        "/api/workouts",
        headers=owner,
        json={
            "workout_name": "Morning walk",
            "category": "Cardio",
            "duration": 30,
            "calories_burned": 100,
            "workout_date": str(date.today()),
        },
    ).json()
    assert client.get(f"/api/workouts/{workout['id']}", headers=other).status_code == 404
    exercise = client.get("/api/exercises?search=walk", headers=owner).json()[0]
    attached = client.post(
        f"/api/workouts/{workout['id']}/exercises",
        headers=owner,
        json={"exercise_id": exercise["id"]},
    )
    assert attached.status_code == 200
    assert attached.json()[0]["name"] == "Walking"
    assert client.get(f"/api/workouts/{workout['id']}/exercises", headers=other).status_code == 404


def test_streak_and_workout_badge_are_derived_from_activity():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user = User(username="streak_user", email="streak@example.com", hashed_password="not-used")
        db.add(user)
        db.flush()
        today = date.today()
        db.add_all([
            Workout(user_id=user.id, workout_name="Walk", category="Cardio", duration=20, calories_burned=80, workout_date=today - timedelta(days=1)),
            Workout(user_id=user.id, workout_name="Run", category="Cardio", duration=30, calories_burned=150, workout_date=today),
        ])
        seed_badges(db)
        streak = refresh_streak_and_badges(db, user.id)
        refresh_progress(db, user.id, [today - timedelta(days=1), today])
        db.commit()
        assert streak.current_streak == 2
        assert streak.longest_streak == 2
        assert db.query(User.id).filter(User.id == user.id).count() == 1
        assert db.query(UserBadge).join(Badge).filter(Badge.name == "First Workout").count() == 1
        summary = db.query(Progress).filter(Progress.user_id == user.id, Progress.date == today).one()
        assert summary.total_workouts == 1
        assert summary.total_calories == 150
    Base.metadata.drop_all(engine)
    engine.dispose()
