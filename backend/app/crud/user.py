from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User


def find_by_identifier(db: Session, identifier: str) -> User | None:
    return db.query(User).filter(
        or_(User.username == identifier, User.email == identifier.lower())
    ).first()
