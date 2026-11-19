from contextlib import asynccontextmanager
import asyncio
from zoneinfo import ZoneInfo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.base import Base
from app.database.connection import SessionLocal, engine
from app import models  # registers ORM models
from app.api.v1.router import router as api_router
from app.models.exercise import Exercise
from app.services.badges import seed_badges
from app.services.progress import rebuild_progress
from app.models.user_preferences import UserPreferences
from app.models.user import User
from app.services.reminders import reminder_loop
from app.models.diet_plan import DietPlan
from app.models.doctor import Doctor
from app.models.nutritionist import Nutritionist
from app.models.subscription import Subscription

DEFAULT_EXERCISES = (
    ("Walking", "Cardio", "Steady, low-impact aerobic movement.", 30),
    ("Jogging", "Cardio", "Moderate-paced running for cardiovascular endurance.", 30),
    ("Cycling", "Cardio", "Stationary or outdoor cycling at a comfortable pace.", 30),
    ("Bodyweight Squats", "Strength", "Lower-body exercise using your body weight.", 15),
    ("Push-ups", "Strength", "Upper-body bodyweight pressing exercise.", 15),
    ("Dumbbell Rows", "Strength", "Upper-body pulling exercise using dumbbells.", 20),
    ("Sun Salutation", "Yoga", "A flowing sequence linking movement and breath.", 15),
    ("Child's Pose", "Yoga", "A gentle resting posture for mobility and relaxation.", 5),
    ("Warrior II", "Yoga", "A standing posture that builds balance and endurance.", 5),
)

DEFAULT_DIET_PLANS = (
    ("Balanced Weight Loss", "A balanced, portion-aware menu emphasizing vegetables, lean proteins, and fiber.", "Weight Loss", 1800, 28),
    ("Mediterranean Cut", "A calorie-conscious Mediterranean-inspired pattern with whole foods and unsaturated fats.", "Weight Loss", 1600, 28),
    ("Plant-forward Strength", "A protein-conscious plant-forward menu designed to support strength training.", "Muscle Gain", 2400, 42),
    ("Lean Muscle Builder", "A higher-energy balanced plan with regular protein-rich meals.", "Muscle Gain", 2800, 42),
    ("Balanced Maintenance", "A flexible, balanced meal pattern aimed at maintaining daily energy needs.", "Maintenance", 2000, 30),
    ("Active Lifestyle Maintenance", "A balanced higher-energy plan for people with regular activity.", "Maintenance", 2400, 30),
)

DEFAULT_SUBSCRIPTIONS = (
    ("Free", 0, 0, ["Meal and nutrition tracking", "Basic diet recommendations"]),
    ("Premium", 9.99, 30, ["Everything in Free", "Diet plan assignment", "Nutritionist consultations"]),
    ("Pro", 19.99, 30, ["Everything in Premium", "Priority expert access", "Personalized diet recommendations"]),
)

# Seeded profiles are demo listings, not real healthcare providers.
DEFAULT_NUTRITIONISTS = (
    ("Demo Nutritionist One", "Sports Nutrition", 5, "nutritionist1@example.com"),
    ("Demo Nutritionist Two", "Weight Management", 8, "nutritionist2@example.com"),
)

DEFAULT_DOCTORS = (
    ("Demo Doctor One", "Dietician", 7, "doctor1@example.com", True),
    ("Demo Doctor Two", "General Doctor", 10, "doctor2@example.com", True),
    ("Demo Doctor Three", "Nutrition Expert", 6, "doctor3@example.com", True),
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    ZoneInfo(settings.reminder_timezone)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        known = {name for (name,) in db.query(Exercise.name).all()}
        for name, category, description, duration in DEFAULT_EXERCISES:
            if name not in known:
                db.add(Exercise(name=name, category=category, description=description, duration=duration))
        existing_diets = {title for (title,) in db.query(DietPlan.title).all()}
        for title, description, goal, calories, duration in DEFAULT_DIET_PLANS:
            if title not in existing_diets:
                db.add(DietPlan(
                    title=title, description=description, goal_type=goal,
                    daily_calories=calories, duration=duration,
                ))
        existing_subscriptions = {name for (name,) in db.query(Subscription.name).all()}
        for name, price, duration, features in DEFAULT_SUBSCRIPTIONS:
            if name not in existing_subscriptions:
                db.add(Subscription(name=name, price=price, duration=duration, features=features))
        existing_nutritionists = {contact for (contact,) in db.query(Nutritionist.contact_info).all()}
        for name, specialization, experience, contact in DEFAULT_NUTRITIONISTS:
            if contact not in existing_nutritionists:
                db.add(Nutritionist(
                    name=name, specialization=specialization, experience=experience, contact_info=contact,
                ))
        existing_doctors = {contact for (contact,) in db.query(Doctor.contact_info).all()}
        for name, specialization, experience, contact, available in DEFAULT_DOCTORS:
            if contact not in existing_doctors:
                db.add(Doctor(
                    name=name, specialization=specialization, experience=experience,
                    contact_info=contact, availability_status=available,
                ))
        db.commit()
        configured_users = {user_id for (user_id,) in db.query(UserPreferences.user_id).all()}
        for (user_id,) in db.query(User.id).all():
            if user_id not in configured_users:
                db.add(UserPreferences(
                    user_id=user_id,
                    timezone=settings.reminder_timezone,
                    workout_reminder_time=f"{settings.reminder_hour:02d}:{settings.reminder_minute:02d}",
                ))
        db.commit()
        seed_badges(db)
        rebuild_progress(db)
        db.commit()
    reminder_task = asyncio.create_task(
        reminder_loop()
    )
    try:
        yield
    finally:
        reminder_task.cancel()
        try:
            await reminder_task
        except asyncio.CancelledError:
            pass

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to FitTrack API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
