from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.workout import Workout
from app.schemas.progress import ProgressSummary
from app.crud.progress import totals_for_date

router = APIRouter(prefix="/progress", tags=["Progress & Analytics"])

@router.get("/daily", response_model=ProgressSummary)
def daily_progress(on_date: date = Query(default_factory=date.today), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = totals_for_date(db, user.id, on_date)
    return {"date": on_date, "total_workouts": rows[0], "total_calories": int(rows[1]), "total_duration": int(rows[2])}

@router.get("/weekly")
def weekly_progress(week_start: date | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    start = week_start or (date.today() - timedelta(days=date.today().weekday()))
    end = start + timedelta(days=6)
    rows = db.query(Workout.workout_date, func.count(Workout.id), func.coalesce(func.sum(Workout.calories_burned), 0), func.coalesce(func.sum(Workout.duration), 0)).filter(
        Workout.user_id == user.id, Workout.workout_date >= start, Workout.workout_date <= end
    ).group_by(Workout.workout_date).order_by(Workout.workout_date).all()
    by_day = {str(row[0]): {"total_workouts": row[1], "total_calories": int(row[2]), "total_duration": int(row[3])} for row in rows}
    return {"start_date": start, "end_date": end, "days": [
        {"date": str(start + timedelta(days=i)), **by_day.get(str(start + timedelta(days=i)), {"total_workouts": 0, "total_calories": 0, "total_duration": 0})}
        for i in range(7)
    ]}

@router.get("/monthly")
def monthly_progress(year: int, month: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if month < 1 or month > 12:
        raise HTTPException(status_code=422, detail="month must be between 1 and 12")
    start = date(year, month, 1)
    end = date(year + (month == 12), 1 if month == 12 else month + 1, 1) - timedelta(days=1)
    rows = db.query(func.count(Workout.id), func.coalesce(func.sum(Workout.calories_burned), 0), func.coalesce(func.sum(Workout.duration), 0)).filter(
        Workout.user_id == user.id, Workout.workout_date >= start, Workout.workout_date <= end
    ).one()
    return {"year": year, "month": month, "total_workouts": rows[0], "total_calories": int(rows[1]), "total_duration": int(rows[2])}
