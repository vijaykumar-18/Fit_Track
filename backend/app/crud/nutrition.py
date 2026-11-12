from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.meal import Meal
from app.models.water_tracking import WaterTracking


def list_meals(db: Session, user_id: int, on_date: date) -> list[Meal]:
    return db.query(Meal).filter(Meal.user_id == user_id, Meal.meal_date == on_date).order_by(Meal.created_at.desc()).all()


def get_meal(db: Session, meal_id: int, user_id: int) -> Meal | None:
    return db.query(Meal).filter(Meal.id == meal_id, Meal.user_id == user_id).first()


def meal_totals(db: Session, user_id: int, on_date: date) -> dict:
    row = db.query(
        func.coalesce(func.sum(Meal.calories), 0),
        func.coalesce(func.sum(Meal.protein), 0),
        func.coalesce(func.sum(Meal.carbs), 0),
        func.coalesce(func.sum(Meal.fats), 0),
    ).filter(Meal.user_id == user_id, Meal.meal_date == on_date).one()
    return {"calories": int(row[0]), "protein": float(row[1]), "carbs": float(row[2]), "fats": float(row[3])}


def list_water(db: Session, user_id: int, on_date: date) -> list[WaterTracking]:
    return db.query(WaterTracking).filter(
        WaterTracking.user_id == user_id, WaterTracking.date == on_date,
    ).order_by(WaterTracking.created_at.desc()).all()


def get_water(db: Session, entry_id: int, user_id: int) -> WaterTracking | None:
    return db.query(WaterTracking).filter(
        WaterTracking.id == entry_id, WaterTracking.user_id == user_id,
    ).first()


def water_total(db: Session, user_id: int, on_date: date) -> int:
    return int(db.query(func.coalesce(func.sum(WaterTracking.quantity), 0)).filter(
        WaterTracking.user_id == user_id, WaterTracking.date == on_date,
    ).scalar())
