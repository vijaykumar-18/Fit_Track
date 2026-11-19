from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.appointment import Appointment
from app.models.diet_plan import DietPlan
from app.models.doctor import Doctor
from app.models.goal import Goal
from app.models.nutritionist import Consultation, Nutritionist
from app.models.subscription import Subscription, UserSubscription
from app.models.user_diet_plan import UserDietPlan


def list_diet_plans(db: Session) -> list[DietPlan]:
    return db.query(DietPlan).order_by(DietPlan.goal_type, DietPlan.daily_calories).all()


def get_diet_plan(db: Session, plan_id: int) -> DietPlan | None:
    return db.query(DietPlan).filter(DietPlan.id == plan_id).first()


def list_assigned_diet_plans(db: Session, user_id: int) -> list[UserDietPlan]:
    return db.query(UserDietPlan).options(joinedload(UserDietPlan.diet_plan)).filter(
        UserDietPlan.user_id == user_id,
    ).order_by(UserDietPlan.assigned_at.desc()).all()


def has_diet_plan_assignment(db: Session, user_id: int, plan_id: int) -> bool:
    return db.query(UserDietPlan.id).filter(
        UserDietPlan.user_id == user_id,
        UserDietPlan.diet_plan_id == plan_id,
    ).first() is not None


def list_subscriptions(db: Session) -> list[Subscription]:
    return db.query(Subscription).order_by(Subscription.price).all()


def get_subscription(db: Session, subscription_id: int) -> Subscription | None:
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()


def current_user_subscription(db: Session, user_id: int) -> UserSubscription | None:
    now = datetime.now(timezone.utc)
    return db.query(UserSubscription).options(joinedload(UserSubscription.subscription)).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.start_date <= now,
        UserSubscription.end_date > now,
    ).order_by(UserSubscription.start_date.desc(), UserSubscription.id.desc()).first()


def list_nutritionists(db: Session) -> list[Nutritionist]:
    return db.query(Nutritionist).order_by(Nutritionist.name).all()


def list_user_consultations(db: Session, user_id: int) -> list[Consultation]:
    return db.query(Consultation).options(joinedload(Consultation.nutritionist)).filter(
        Consultation.user_id == user_id,
    ).order_by(Consultation.scheduled_time.desc()).all()


def get_user_consultation(db: Session, consultation_id: int, user_id: int) -> Consultation | None:
    return db.query(Consultation).filter(
        Consultation.id == consultation_id, Consultation.user_id == user_id,
    ).first()


def list_doctors(db: Session) -> list[Doctor]:
    return db.query(Doctor).order_by(Doctor.name).all()


def get_doctor(db: Session, doctor_id: int) -> Doctor | None:
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()


def list_user_appointments(db: Session, user_id: int) -> list[Appointment]:
    return db.query(Appointment).options(joinedload(Appointment.doctor)).filter(
        Appointment.user_id == user_id,
    ).order_by(Appointment.appointment_date.desc()).all()


def get_user_appointment(db: Session, appointment_id: int, user_id: int) -> Appointment | None:
    return db.query(Appointment).filter(
        Appointment.id == appointment_id, Appointment.user_id == user_id,
    ).first()


def get_active_goal(db: Session, user_id: int) -> Goal | None:
    return db.query(Goal).filter(
        Goal.user_id == user_id, Goal.status != "COMPLETED",
        Goal.goal_type.in_(("Weight Loss", "Muscle Gain")),
    ).order_by(Goal.created_at.desc()).first()
