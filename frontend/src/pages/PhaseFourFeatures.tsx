import { FormEvent, useEffect, useState } from 'react'
import { Activity, CalendarDays, Check, Clock3, Crown, HeartPulse, Leaf, Sparkles, Stethoscope, UserRound } from 'lucide-react'

import { api } from '../services/api'
import type {
  Appointment, AssignedDietPlan, Consultation, DietPlan, DietRecommendation, Doctor,
  Nutritionist, SubscriptionPlan, UserSubscription,
} from '../types'

function requestError(error: any, fallback: string): string {
  return error?.response?.data?.detail || fallback
}

export function DietPlansPage({ onNavigate }: { onNavigate: (page: string) => void }) {
  const [plans, setPlans] = useState<DietPlan[]>([])
  const [suggestions, setSuggestions] = useState<DietRecommendation[]>([])
  const [assigned, setAssigned] = useState<AssignedDietPlan[]>([])
  const [current, setCurrent] = useState<UserSubscription | null>(null)
  const [selected, setSelected] = useState<DietPlan | null>(null)
  const [goal, setGoal] = useState<DietPlan['goal_type']>('Weight Loss')
  const [calories, setCalories] = useState(2000)
  const [activity, setActivity] = useState<'Low' | 'Moderate' | 'High'>('Moderate')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function load() {
    try {
      const [planResponse, assignedResponse, currentResponse] = await Promise.all([
        api.get<DietPlan[]>('/diet-plans'),
        api.get<AssignedDietPlan[]>('/diet-plans/assigned'),
        api.get<UserSubscription>('/subscriptions/current'),
      ])
      setPlans(planResponse.data)
      setAssigned(assignedResponse.data)
      setCurrent(currentResponse.data)
      setError('')
    } catch (e: any) { setError(requestError(e, 'Could not load diet plans.')) }
  }
  async function loadRecommendations(event?: FormEvent) {
    event?.preventDefault()
    try {
      const response = await api.get<DietRecommendation[]>('/diet-plans/recommendations', {
        params: { goal_type: goal, daily_calories: calories, activity_level: activity },
      })
      setSuggestions(response.data)
      setError('')
    } catch (e: any) { setError(requestError(e, 'Could not load personalized recommendations.')) }
  }
  useEffect(() => { void load(); void loadRecommendations() }, [])

  async function showDetails(plan: DietPlan) {
    if (selected?.id === plan.id) { setSelected(null); return }
    try {
      const response = await api.get<DietPlan>(`/diet-plans/${plan.id}`)
      setSelected(response.data)
    } catch (e: any) { setError(requestError(e, 'Could not load this diet plan.')) }
  }
  async function assign(plan: DietPlan) {
    try {
      await api.post(`/diet-plans/${plan.id}/assign`)
      setMessage(`${plan.title} assigned to your account.`)
      setError('')
      await load()
    } catch (e: any) { setError(requestError(e, 'Could not assign this diet plan.')) }
  }

  return <div className="page-stack">
    <div className="section-heading"><div><h2>Diet plans</h2><p className="muted">Browse structured plans and get suggestions matched to your goals.</p></div><Leaf /></div>
    {error && <p className="error">{error}</p>}{message && <p className="success-text">{message}</p>}
    <section className="panel">
      <div className="panel-heading"><div><h3>Personalized recommendations</h3><p className="muted">Based on your goal, calorie target, and activity level.</p></div><Sparkles /></div>
      <form className="phase4-filters" onSubmit={loadRecommendations}>
        <label>Goal<select value={goal} onChange={event => setGoal(event.target.value as DietPlan['goal_type'])}><option>Weight Loss</option><option>Muscle Gain</option><option>Maintenance</option></select></label>
        <label>Daily calorie requirement<input type="number" min="800" max="10000" value={calories} onChange={event => setCalories(Number(event.target.value))} /></label>
        <label>Activity level<select value={activity} onChange={event => setActivity(event.target.value as typeof activity)}><option>Low</option><option>Moderate</option><option>High</option></select></label>
        <button className="primary"><Sparkles size={15} /> Recommend</button>
      </form>
      <div className="recommendation-grid phase4-recommendations">{suggestions.map(({ diet_plan, reason }) => <article className="phase4-recommendation" key={diet_plan.id}><strong>{diet_plan.title}</strong><p>{reason}</p></article>)}</div>
    </section>
    <section className="panel">
      <div className="panel-heading"><div><h3>Available plans</h3><p className="muted">Choose a plan to view details. Assignment is included with Premium and Pro.</p></div><span className="count-pill">Current: {current?.subscription.name || 'Loading'}</span></div>
      {plans.length ? <div className="phase4-card-grid">{plans.map(plan => <article className="phase4-card" key={plan.id}>
        <div className="phase4-card-top"><span className="category-chip">{plan.goal_type}</span><span className="muted small">{plan.daily_calories.toLocaleString()} kcal/day</span></div>
        <h3>{plan.title}</h3><p>{plan.description}</p><p className="muted small">{plan.duration} days · Personalized meal structure</p>
        <div className="phase4-card-actions"><button className="secondary" onClick={() => void showDetails(plan)}>{selected?.id === plan.id ? 'Hide details' : 'View details'}</button>
          {current?.subscription.name === 'Premium' || current?.subscription.name === 'Pro'
            ? <button className="primary" onClick={() => void assign(plan)}>Assign plan</button>
            : <button className="primary" onClick={() => onNavigate('Subscriptions')}><Crown size={15} /> Upgrade to assign</button>}
        </div>
        {selected?.id === plan.id && <div className="phase4-detail"><strong>Plan details</strong><p>{selected.description}</p><span>Goal: {selected.goal_type} · Daily target: {selected.daily_calories} kcal · Duration: {selected.duration} days</span></div>}
      </article>)}</div> : <div className="empty-state">No diet plans are available.</div>}
    </section>
    <section className="panel"><div className="panel-heading"><div><h3>Assigned plans</h3><p className="muted">Your selected diet plans.</p></div></div>
      {assigned.length ? <div className="planned-list">{assigned.map(item => <article className="planned-item" key={item.id}><div className="workout-symbol"><Leaf size={17} /></div><div className="planned-copy"><strong>{item.diet_plan.title}</strong><span>{item.diet_plan.goal_type} · {item.diet_plan.daily_calories} kcal/day · Assigned {new Date(item.assigned_at).toLocaleDateString()}</span></div></article>)}</div> : <div className="empty-state">No plans assigned yet. Premium and Pro members can assign a plan.</div>}
    </section>
    <p className="muted small">Diet plans are general educational guidance, not individualized medical advice.</p>
  </div>
}

export function SubscriptionsPage({ refresh }: { refresh: number }) {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([])
  const [current, setCurrent] = useState<UserSubscription | null>(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  async function load() {
    try {
      const [planResponse, currentResponse] = await Promise.all([
        api.get<SubscriptionPlan[]>('/subscriptions'),
        api.get<UserSubscription>('/subscriptions/current'),
      ])
      setPlans(planResponse.data)
      setCurrent(currentResponse.data)
      setError('')
    } catch (e: any) { setError(requestError(e, 'Could not load subscription details.')) }
  }
  useEffect(() => { void load() }, [refresh])
  async function selectPlan(plan: SubscriptionPlan) {
    try {
      const response = await api.post<UserSubscription>(`/subscriptions/${plan.id}/select`)
      setCurrent(response.data)
      setMessage(`Your plan is now ${plan.name}.`)
      setError('')
    } catch (e: any) { setError(requestError(e, 'Could not update your subscription.')) }
  }
  return <div className="page-stack">
    <div className="section-heading"><div><h2>Subscription plans</h2><p className="muted">Manage your access to advanced diet and expert features.</p></div><Crown /></div>
    {error && <p className="error">{error}</p>}{message && <p className="success-text">{message}</p>}
    {current && <section className="panel current-plan"><div><span className="eyebrow">YOUR CURRENT PLAN</span><h3>{current.subscription.name}</h3><p className="muted">Active since {new Date(current.start_date).toLocaleDateString()}{current.subscription.duration > 0 ? ` · Renews/expires ${new Date(current.end_date).toLocaleDateString()}` : ''}</p></div><span className="category-chip">{current.subscription.name === 'Free' ? 'Basic access' : 'Premium access'}</span></section>}
    <div className="phase4-card-grid">{plans.map(plan => <article className={`phase4-card subscription-card ${current?.subscription.id === plan.id ? 'selected-plan' : ''}`} key={plan.id}>
      <div className="phase4-card-top"><span className="category-chip">{plan.name}</span>{current?.subscription.id === plan.id && <span className="muted small">Current plan</span>}</div>
      <h3>{plan.price === 0 ? 'Free' : `$${plan.price.toFixed(2)} / month`}</h3><p className="muted small">{plan.duration ? `${plan.duration} day billing period` : 'No expiry'}</p>
      <ul className="phase4-feature-list">{plan.features.map(feature => <li key={feature}><Check size={15} />{feature}</li>)}</ul>
      <button className={current?.subscription.id === plan.id ? 'secondary full' : 'primary full'} disabled={current?.subscription.id === plan.id} onClick={() => void selectPlan(plan)}>{current?.subscription.id === plan.id ? 'Current plan' : plan.price === 0 ? 'Switch to Free' : 'Select plan'}</button>
    </article>)}</div>
    <p className="muted small">Plan selection is a local demo entitlement; no payment is processed. Configure a payment provider before charging users.</p>
  </div>
}

export function NutritionistsPage() {
  const [people, setPeople] = useState<Nutritionist[]>([])
  const [history, setHistory] = useState<Consultation[]>([])
  const [current, setCurrent] = useState<UserSubscription | null>(null)
  const [personId, setPersonId] = useState(0)
  const [scheduled, setScheduled] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  async function load() {
    try {
      const [peopleResponse, historyResponse, currentResponse] = await Promise.all([
        api.get<Nutritionist[]>('/nutritionists'),
        api.get<Consultation[]>('/consultations'),
        api.get<UserSubscription>('/subscriptions/current'),
      ])
      setPeople(peopleResponse.data)
      setHistory(historyResponse.data)
      setCurrent(currentResponse.data)
      if (!personId && peopleResponse.data.length) setPersonId(peopleResponse.data[0].id)
      setError('')
    } catch (e: any) { setError(requestError(e, 'Could not load nutritionists and consultations.')) }
  }
  useEffect(() => { void load() }, [])
  async function book(event: FormEvent) {
    event.preventDefault()
    try {
      await api.post('/consultations', { nutritionist_id: personId, scheduled_time: new Date(scheduled).toISOString() })
      setMessage('Consultation request submitted.')
      setError('')
      await load()
    } catch (e: any) { setError(requestError(e, 'Could not book this consultation.')) }
  }
  async function cancel(item: Consultation) {
    try { await api.patch(`/consultations/${item.id}/cancel`); await load() }
    catch (e: any) { setError(requestError(e, 'Could not cancel this consultation.')) }
  }
  return <div className="page-stack">
    <div className="section-heading"><div><h2>Nutritionist consultations</h2><p className="muted">Explore nutrition professionals and manage consultation requests.</p></div><UserRound /></div>
    {error && <p className="error">{error}</p>}{message && <p className="success-text">{message}</p>}
    <section className="phase4-card-grid">{people.map(person => <article className="phase4-card" key={person.id}><div className="workout-symbol"><UserRound /></div><h3>{person.name}</h3><p>{person.specialization}</p><p className="muted small">{person.experience} years' experience</p><a href={`mailto:${person.contact_info}`}>{person.contact_info}</a></article>)}</section>
    <div className="content-grid workout-layout">
      <form className="panel form-panel" onSubmit={book}><div className="panel-heading"><div><h3>Request a consultation</h3><p className="muted">Choose an expert and a future time.</p></div><CalendarDays /></div>
        <label>Nutritionist<select required value={personId} onChange={event => setPersonId(Number(event.target.value))}>{people.map(person => <option value={person.id} key={person.id}>{person.name} · {person.specialization}</option>)}</select></label>
        <label>Date and time<input required type="datetime-local" value={scheduled} onChange={event => setScheduled(event.target.value)} /></label>
        {current?.subscription.name === 'Free' && <p className="muted small">Nutritionist consultations are available with Premium and Pro plans.</p>}
        <button className="primary full"><CalendarDays size={15} /> Request booking</button>
      </form>
      <section className="panel"><div className="panel-heading"><div><h3>Consultation history</h3><p className="muted">Your booking status and scheduled sessions.</p></div></div>
        {history.length ? <div className="planned-list">{history.map(item => <article className="planned-item" key={item.id}><div className="workout-symbol"><Clock3 size={17} /></div><div className="planned-copy"><strong>{item.nutritionist.name}</strong><span>{new Date(item.scheduled_time).toLocaleString()} · {item.status}</span></div>{item.status === 'PENDING' && <button className="text-button" onClick={() => void cancel(item)}>Cancel</button>}</article>)}</div> : <div className="empty-state">No consultations booked.</div>}
      </section>
    </div>
    <p className="muted small">These seeded contacts are demo profiles, not real providers. Confirm credentials and availability before real-world use.</p>
  </div>
}

export function DoctorsPage() {
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [history, setHistory] = useState<Appointment[]>([])
  const [selected, setSelected] = useState<Doctor | null>(null)
  const [doctorId, setDoctorId] = useState(0)
  const [appointmentDate, setAppointmentDate] = useState('')
  const [timeSlot, setTimeSlot] = useState('09:00')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  async function load() {
    try {
      const [doctorsResponse, historyResponse] = await Promise.all([
        api.get<Doctor[]>('/doctors'), api.get<Appointment[]>('/appointments'),
      ])
      setDoctors(doctorsResponse.data)
      setHistory(historyResponse.data)
      if (!doctorId && doctorsResponse.data.length) setDoctorId(doctorsResponse.data[0].id)
      setError('')
    } catch (e: any) { setError(requestError(e, 'Could not load doctors and appointments.')) }
  }
  useEffect(() => { void load() }, [])
  async function showProfile(id: number) {
    try { const response = await api.get<Doctor>(`/doctors/${id}`); setSelected(response.data) }
    catch (e: any) { setError(requestError(e, 'Could not load doctor profile.')) }
  }
  async function book(event: FormEvent) {
    event.preventDefault()
    try {
      await api.post('/appointments', { doctor_id: doctorId, appointment_date: appointmentDate, time_slot: timeSlot })
      setMessage('Appointment request submitted.')
      setError('')
      await load()
    } catch (e: any) { setError(requestError(e, 'Could not book this appointment.')) }
  }
  async function cancel(item: Appointment) {
    try { await api.patch(`/appointments/${item.id}/cancel`); await load() }
    catch (e: any) { setError(requestError(e, 'Could not cancel this appointment.')) }
  }
  return <div className="page-stack">
    <div className="section-heading"><div><h2>Doctor support</h2><p className="muted">Find a medical professional and request an appointment.</p></div><Stethoscope /></div>
    {error && <p className="error">{error}</p>}{message && <p className="success-text">{message}</p>}
    <section className="phase4-card-grid">{doctors.map(doctor => <article className="phase4-card" key={doctor.id}><div className="phase4-card-top"><div className="workout-symbol"><HeartPulse /></div><span className={`status ${doctor.availability_status ? 'done' : ''}`}>{doctor.availability_status ? 'Available' : 'Unavailable'}</span></div><h3>{doctor.name}</h3><p>{doctor.specialization}</p><p className="muted small">{doctor.experience} years' experience</p><a href={`mailto:${doctor.contact_info}`}>{doctor.contact_info}</a><button className="secondary" onClick={() => void showProfile(doctor.id)}>View profile</button></article>)}</section>
    {selected && <section className="panel phase4-detail"><button className="text-button" onClick={() => setSelected(null)}>Close profile</button><h3>{selected.name}</h3><p>{selected.specialization} · {selected.experience} years' experience</p><p>Availability: {selected.availability_status ? 'Accepting appointment requests' : 'Not currently available'}</p><a href={`mailto:${selected.contact_info}`}>Contact {selected.contact_info}</a></section>}
    <div className="content-grid workout-layout">
      <form className="panel form-panel" onSubmit={book}><div className="panel-heading"><div><h3>Request an appointment</h3><p className="muted">Choose a doctor, date, and time.</p></div><CalendarDays /></div>
        <label>Doctor<select required value={doctorId} onChange={event => setDoctorId(Number(event.target.value))}>{doctors.map(doctor => <option value={doctor.id} key={doctor.id} disabled={!doctor.availability_status}>{doctor.name} · {doctor.specialization}</option>)}</select></label>
        <label>Appointment date<input required type="date" min={new Date().toISOString().slice(0, 10)} value={appointmentDate} onChange={event => setAppointmentDate(event.target.value)} /></label>
        <label>Time slot (UTC)<input required type="time" value={timeSlot} onChange={event => setTimeSlot(event.target.value)} /></label>
        <button className="primary full"><CalendarDays size={15} /> Request appointment</button>
      </form>
      <section className="panel"><div className="panel-heading"><div><h3>Appointment history</h3><p className="muted">Track pending, confirmed, or cancelled requests.</p></div></div>
        {history.length ? <div className="planned-list">{history.map(item => <article className="planned-item" key={item.id}><div className="workout-symbol"><Activity size={17} /></div><div className="planned-copy"><strong>{item.doctor.name}</strong><span>{new Date(item.appointment_date).toLocaleDateString()} · {item.time_slot} UTC · {item.status}</span></div>{item.status !== 'CANCELLED' && <button className="text-button" onClick={() => void cancel(item)}>Cancel</button>}</article>)}</div> : <div className="empty-state">No appointments booked.</div>}
      </section>
    </div>
    <p className="muted small">These seeded contacts are demo profiles, not real providers. Appointment requests are pending until confirmed; this starter does not provide medical advice.</p>
  </div>
}
