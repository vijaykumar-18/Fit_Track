from sqlalchemy.orm import Session

from app.models.exercise import Exercise


def search_exercises(db: Session, name: str | None = None, category: str | None = None) -> list[Exercise]:
    query = db.query(Exercise)
    if name:
        query = query.filter(Exercise.name.ilike(f"%{name.strip()}%"))
    if category:
        query = query.filter(Exercise.category == category)
    return query.order_by(Exercise.category, Exercise.name).all()
