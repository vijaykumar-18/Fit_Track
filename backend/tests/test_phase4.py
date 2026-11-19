from datetime import datetime, timedelta, timezone

from app import main as app_module
from app.models.subscription import UserSubscription
from app.services import reminders
from conftest import register_and_login


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_phase_four_endpoints_are_grouped_by_feature_in_openapi(client):
    schema = client.get("/openapi.json").json()
    tags = {tag["name"] for tag in schema.get("tags", [])}
    operation_tags = {
        tag
        for path in schema["paths"].values()
        for operation in path.values()
        for tag in operation.get("tags", [])
    }

    assert "Phase 4" not in tags | operation_tags
    assert {
        "Diet Plans", "Subscriptions", "Nutritionists",
        "Consultations", "Doctors", "Appointments",
    } <= operation_tags


def test_diet_plans_recommendations_and_premium_access_are_user_scoped(client):
    owner = headers(register_and_login(client, "phase4_diet_owner"))
    other = headers(register_and_login(client, "phase4_diet_other"))

    plans = client.get("/api/diet-plans", headers=owner)
    assert plans.status_code == 200
    assert len(plans.json()) >= 3
    recommendations = client.get(
        "/api/diet-plans/recommendations",
        headers=owner,
        params={"goal_type": "Weight Loss", "daily_calories": 1800, "activity_level": "Low"},
    )
    assert recommendations.status_code == 200
    assert recommendations.json()[0]["diet_plan"]["goal_type"] == "Weight Loss"
    assert "activity level" in recommendations.json()[0]["reason"]
    assert client.get(
        "/api/diet-plans/recommendations", headers=owner, params={"activity_level": "Extreme"},
    ).status_code == 422

    plan = plans.json()[0]
    assert client.post(f"/api/diet-plans/{plan['id']}/assign", headers=owner).status_code == 403
    tiers = client.get("/api/subscriptions", headers=owner).json()
    premium = next(item for item in tiers if item["name"] == "Premium")
    upgraded = client.post(f"/api/subscriptions/{premium['id']}/select", headers=owner)
    assert upgraded.status_code == 201
    assert upgraded.json()["subscription"]["name"] == "Premium"
    assignment = client.post(f"/api/diet-plans/{plan['id']}/assign", headers=owner)
    assert assignment.status_code == 201
    assert assignment.json()["diet_plan"]["id"] == plan["id"]
    assert client.post(f"/api/diet-plans/{plan['id']}/assign", headers=owner).status_code == 409
    assert client.get("/api/diet-plans/assigned", headers=other).json() == []


def test_consultations_and_doctor_appointments_validate_ownership(client):
    owner = headers(register_and_login(client, "phase4_booking_owner"))
    other = headers(register_and_login(client, "phase4_booking_other"))
    nutritionists = client.get("/api/nutritionists", headers=owner).json()
    doctors = client.get("/api/doctors", headers=owner).json()
    assert nutritionists and doctors
    assert client.post(
        "/api/consultations",
        headers=owner,
        json={
            "nutritionist_id": nutritionists[0]["id"],
            "scheduled_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        },
    ).status_code == 403

    premium = next(
        plan for plan in client.get("/api/subscriptions", headers=owner).json()
        if plan["name"] == "Premium"
    )
    assert client.post(f"/api/subscriptions/{premium['id']}/select", headers=owner).status_code == 201
    consultation = client.post(
        "/api/consultations",
        headers=owner,
        json={
            "nutritionist_id": nutritionists[0]["id"],
            "scheduled_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        },
    )
    assert consultation.status_code == 201
    assert consultation.json()["scheduled_time"].endswith("+00:00")
    consultation_id = consultation.json()["id"]
    assert client.get("/api/consultations", headers=other).json() == []
    assert client.patch(f"/api/consultations/{consultation_id}/cancel", headers=other).status_code == 404
    assert client.patch(f"/api/consultations/{consultation_id}/cancel", headers=owner).json()["status"] == "CANCELLED"
    assert client.post(
        "/api/consultations",
        headers=owner,
        json={"nutritionist_id": nutritionists[0]["id"], "scheduled_time": "2020-01-01T10:00:00Z"},
    ).status_code == 422

    appointment_date = (datetime.now(timezone.utc) + timedelta(days=3)).date().isoformat()
    appointment = client.post(
        "/api/appointments",
        headers=owner,
        json={"doctor_id": doctors[0]["id"], "appointment_date": appointment_date, "time_slot": "10:30"},
    )
    assert appointment.status_code == 201
    assert appointment.json()["appointment_date"].endswith("+00:00")
    appointment_id = appointment.json()["id"]
    assert client.get("/api/appointments", headers=other).json() == []
    assert client.patch(f"/api/appointments/{appointment_id}/cancel", headers=other).status_code == 404
    assert client.patch(f"/api/appointments/{appointment_id}/cancel", headers=owner).json()["status"] == "CANCELLED"
    assert client.post(
        "/api/appointments",
        headers=owner,
        json={"doctor_id": doctors[0]["id"], "appointment_date": appointment_date, "time_slot": "29:90"},
    ).status_code == 422


def test_subscription_and_consultation_reminders_are_idempotent(client, monkeypatch):
    owner = headers(register_and_login(client, "phase4_reminders"))
    premium = next(
        plan for plan in client.get("/api/subscriptions", headers=owner).json()
        if plan["name"] == "Premium"
    )
    client.post(f"/api/subscriptions/{premium['id']}/select", headers=owner)
    nutritionist = client.get("/api/nutritionists", headers=owner).json()[0]
    scheduled = datetime.now(timezone.utc) + timedelta(hours=2)
    booking = client.post(
        "/api/consultations", headers=owner,
        json={"nutritionist_id": nutritionist["id"], "scheduled_time": scheduled.isoformat()},
    )
    assert booking.status_code == 201

    with app_module.SessionLocal() as db:
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == booking.json()["user_id"],
        ).order_by(UserSubscription.start_date.desc()).first()
        subscription.end_date = datetime.now(timezone.utc) + timedelta(days=1)
        db.commit()

    monkeypatch.setattr(reminders, "SessionLocal", app_module.SessionLocal)
    reminders.create_due_reminders()
    reminders.create_due_reminders()
    notifications = client.get("/api/notifications", headers=owner).json()
    titles = [item["title"] for item in notifications]
    assert titles.count("Subscription expiry alert") == 1
    assert titles.count("Consultation reminder") == 1
