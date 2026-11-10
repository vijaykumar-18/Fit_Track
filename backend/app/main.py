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
from app.services.reminders import daily_reminder_loop

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    ZoneInfo(settings.reminder_timezone)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        known = {name for (name,) in db.query(Exercise.name).all()}
        for name, category, description, duration in DEFAULT_EXERCISES:
            if name not in known:
                db.add(Exercise(name=name, category=category, description=description, duration=duration))
        db.commit()
        seed_badges(db)
        rebuild_progress(db)
        db.commit()
    reminder_task = asyncio.create_task(
        daily_reminder_loop(settings.reminder_hour, settings.reminder_minute, settings.reminder_timezone)
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
