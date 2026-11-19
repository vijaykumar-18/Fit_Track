from datetime import datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.phase4 import (
    current_user_subscription, get_diet_plan, get_doctor, get_subscription,
    get_user_appointment, get_user_consultation, list_assigned_diet_plans,
    has_diet_plan_assignment, list_diet_plans, list_doctors, list_nutritionists, list_subscriptions,
    list_user_appointments, list_user_consultations,
)
from app.database.connection import get_db
from app.models.appointment import Appointment
from app.models.nutritionist import Consultation, Nutritionist
from app.models.notification import Notification
from app.models.subscription import Subscription, UserSubscription
from app.models.user import User
from app.models.user_diet_plan import UserDietPlan
from app.schemas.phase4 import (
    AppointmentCreate, AppointmentRead, ConsultationCreate, ConsultationRead, DietGoal,
    DietPlanRead, DietRecommendation, DoctorRead, NutritionistRead, SubscriptionRead,
    UserDietPlanRead, UserSubscriptionRead,
)
from app.services.diet_recommendations import recommend_diet_plans

router = APIRouter()


def active_subscription(db: Session, user_id: int) -> UserSubscription:
    current = current_user_subscription(db, user_id)
    if current:
        return current
    free = db.query(Subscription).filter_by(name="Free").first()
    if free is None:
        raise HTTPException(status_code=503, detail="Subscription plans are not configured")
    now = datetime.now(timezone.utc)
    current = UserSubscription(
        user_id=user_id, subscription_id=free.id, start_date=now,
        end_date=now + timedelta(days=36500),
    )
    db.add(current)
    db.commit()
    db.refresh(current)
    current.subscription = free
    return current


def require_expert_access(db: Session, user_id: int) -> UserSubscription:
    current = active_subscription(db, user_id)
    if current.subscription.name not in {"Premium", "Pro"}:
        raise HTTPException(status_code=403, detail="Upgrade to Premium or Pro to book an expert consultation")
    return current


@router.get("/diet-plans", response_model=list[DietPlanRead], tags=["Diet Plans"])
def diet_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_diet_plans(db)


@router.get("/diet-plans/recommendations", response_model=list[DietRecommendation], tags=["Diet Plans"])
def diet_recommendations(
    goal_type: DietGoal | None = None,
    daily_calories: int = Query(default=2000, ge=800, le=10000),
    activity_level: str = Query(default="Moderate", pattern="^(Low|Moderate|High)$"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return recommend_diet_plans(
        db, user.id, daily_calories, activity_level, goal_type.value if goal_type else None,
    )


@router.get("/diet-plans/assigned", response_model=list[UserDietPlanRead], tags=["Diet Plans"])
def assigned_diet_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_assigned_diet_plans(db, user.id)


@router.get("/diet-plans/{plan_id}", response_model=DietPlanRead, tags=["Diet Plans"])
def diet_plan_detail(plan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plan = get_diet_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Diet plan not found")
    return plan


@router.post(
    "/diet-plans/{plan_id}/assign", response_model=UserDietPlanRead,
    status_code=status.HTTP_201_CREATED, tags=["Diet Plans"],
)
def assign_diet_plan(plan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_expert_access(db, user.id)
    plan = get_diet_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Diet plan not found")
    if has_diet_plan_assignment(db, user.id, plan.id):
        raise HTTPException(status_code=409, detail="This diet plan is already assigned to your account")
    assignment = UserDietPlan(user_id=user.id, diet_plan_id=plan.id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    assignment.diet_plan = plan
    return assignment


@router.get("/subscriptions", response_model=list[SubscriptionRead], tags=["Subscriptions"])
def subscriptions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_subscriptions(db)


@router.get("/subscriptions/current", response_model=UserSubscriptionRead, tags=["Subscriptions"])
def current_subscription(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return active_subscription(db, user.id)


@router.post(
    "/subscriptions/{subscription_id}/select", response_model=UserSubscriptionRead,
    status_code=status.HTTP_201_CREATED, tags=["Subscriptions"],
)
def select_subscription(subscription_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plan = get_subscription(db, subscription_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    now = datetime.now(timezone.utc)
    previous = current_user_subscription(db, user.id)
    if previous:
        previous.end_date = now
    current = UserSubscription(
        user_id=user.id, subscription_id=plan.id, start_date=now,
        end_date=now + timedelta(days=plan.duration if plan.duration > 0 else 36500),
    )
    db.add(current)
    db.add(Notification(
        user_id=user.id,
        title="Subscription updated",
        message=f"Your FitTrack plan is now {plan.name}.",
    ))
    db.commit()
    db.refresh(current)
    current.subscription = plan
    return current


@router.get("/nutritionists", response_model=list[NutritionistRead], tags=["Nutritionists"])
def nutritionists(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_nutritionists(db)


@router.get("/consultations", response_model=list[ConsultationRead], tags=["Consultations"])
def consultations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_user_consultations(db, user.id)


@router.post(
    "/consultations", response_model=ConsultationRead,
    status_code=status.HTTP_201_CREATED, tags=["Consultations"],
)
def book_consultation(
    payload: ConsultationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_expert_access(db, user.id)
    nutritionist = db.query(Nutritionist).filter(Nutritionist.id == payload.nutritionist_id).first()
    if nutritionist is None:
        raise HTTPException(status_code=404, detail="Nutritionist not found")
    booking = Consultation(
        user_id=user.id,
        nutritionist_id=nutritionist.id,
        scheduled_time=payload.scheduled_time.astimezone(timezone.utc),
    )
    db.add(booking)
    db.add(Notification(
        user_id=user.id, title="Consultation booked",
        message=f"Your consultation with {nutritionist.name} is scheduled for {payload.scheduled_time.isoformat()}.",
    ))
    db.commit()
    db.refresh(booking)
    booking.nutritionist = nutritionist
    return booking


@router.patch(
    "/consultations/{consultation_id}/cancel",
    response_model=ConsultationRead, tags=["Consultations"],
)
def cancel_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = get_user_consultation(db, consultation_id, user.id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Consultation not found")
    if booking.status != "PENDING":
        raise HTTPException(status_code=409, detail="Only pending consultations can be cancelled")
    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/doctors", response_model=list[DoctorRead], tags=["Doctors"])
def doctors(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_doctors(db)


@router.get("/doctors/{doctor_id}", response_model=DoctorRead, tags=["Doctors"])
def doctor_detail(doctor_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doctor = get_doctor(db, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.get("/appointments", response_model=list[AppointmentRead], tags=["Appointments"])
def appointments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_user_appointments(db, user.id)


@router.post(
    "/appointments", response_model=AppointmentRead,
    status_code=status.HTTP_201_CREATED, tags=["Appointments"],
)
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doctor = get_doctor(db, payload.doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doctor.availability_status:
        raise HTTPException(status_code=409, detail="Doctor is not currently available")
    appointment_datetime = datetime.combine(
        payload.appointment_date, time.fromisoformat(payload.time_slot), tzinfo=timezone.utc,
    )
    if appointment_datetime <= datetime.now(timezone.utc):
        raise HTTPException(status_code=422, detail="Appointment time must be in the future")
    booking = Appointment(
        user_id=user.id,
        doctor_id=doctor.id,
        appointment_date=appointment_datetime,
        time_slot=payload.time_slot,
    )
    db.add(booking)
    db.add(Notification(
        user_id=user.id, title="Appointment requested",
        message=f"Your appointment request with {doctor.name} for {appointment_datetime.isoformat()} is pending confirmation.",
    ))
    db.commit()
    db.refresh(booking)
    booking.doctor = doctor
    return booking


@router.patch(
    "/appointments/{appointment_id}/cancel",
    response_model=AppointmentRead, tags=["Appointments"],
)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = get_user_appointment(db, appointment_id, user.id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if booking.status not in {"PENDING", "CONFIRMED"}:
        raise HTTPException(status_code=409, detail="Appointment cannot be cancelled")
    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)
    return booking
