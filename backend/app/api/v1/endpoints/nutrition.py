from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.nutrition import get_meal, list_meals, meal_totals
from app.database.connection import get_db
from app.models.meal import Meal
from app.models.user import User
from app.schemas.nutrition import MealCreate, MealRead, MealUpdate

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


@router.get("/meals", response_model=list[MealRead])
def meals_for_day(
    on_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return list_meals(db, user.id, on_date)


@router.get("/summary")
def nutrition_summary(
    on_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return {"date": on_date, **meal_totals(db, user.id, on_date)}


@router.post("/meals", response_model=MealRead, status_code=status.HTTP_201_CREATED)
def create_meal(payload: MealCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    meal = Meal(user_id=user.id, **payload.model_dump())
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


@router.patch("/meals/{meal_id}", response_model=MealRead)
def update_meal(
    meal_id: int,
    payload: MealUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    meal = get_meal(db, meal_id, user.id)
    if meal is None:
        raise HTTPException(status_code=404, detail="Meal not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(meal, field, value)
    db.commit()
    db.refresh(meal)
    return meal


@router.delete("/meals/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(meal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    meal = get_meal(db, meal_id, user.id)
    if meal is None:
        raise HTTPException(status_code=404, detail="Meal not found")
    db.delete(meal)
    db.commit()
