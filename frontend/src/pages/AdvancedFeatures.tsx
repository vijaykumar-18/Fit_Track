import { FormEvent, useEffect, useState } from 'react'
import { Award, CalendarDays, ChevronLeft, ChevronRight, Flame, Pencil, Plus, Search, Trash2 } from 'lucide-react'
import { api } from '../services/api'
import type { Badge, Exercise, Streak, WorkoutPlan } from '../types'
import { localDateString } from '../utils/date'

export function WorkoutPlans({ refresh, onRefresh }: { refresh: number; onRefresh: () => void }) {
  const [plans, setPlans] = useState<WorkoutPlan[]>([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [scheduledDate, setScheduledDate] = useState(localDateString())
  const [visibleMonth, setVisibleMonth] = useState(() => new Date())
  const [error, setError] = useState('')
  const [editingPlan, setEditingPlan] = useState<WorkoutPlan | null>(null)

  async function loadPlans() {
    try {
      const response = await api.get<WorkoutPlan[]>('/plans')
      setPlans(response.data)
      setError('')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Could not load workout plans.')
    }
  }

  useEffect(() => { void loadPlans() }, [refresh])

  async function createPlan(event: FormEvent) {
    event.preventDefault()
    try {
      const payload = { title, description, scheduled_date: scheduledDate }
      if (editingPlan) {
        await api.patch(`/plans/${editingPlan.id}`, payload)
        setEditingPlan(null)
      } else {
        await api.post('/plans', payload)
      }
      setTitle('')
      setDescription('')
      await loadPlans()
      onRefresh()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Could not create workout plan.')
    }
  }

  async function deletePlan(id: number) {
    if (!window.confirm('Delete this scheduled workout?')) return
    try {
      await api.delete(`/plans/${id}`)
      await loadPlans()
      onRefresh()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Could not delete workout plan.')
    }
  }

  const monthStart = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth(), 1)
  const monthDays = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() + 1, 0).getDate()
  const calendarDays = [
    ...Array.from({ length: monthStart.getDay() }, () => null),
    ...Array.from({ length: monthDays }, (_, index) => index + 1),
  ]
  const planDates = new Set(plans.map(plan => plan.scheduled_date))
  const upcomingPlans = plans.filter(plan => plan.scheduled_date >= localDateString())
  const formatLocalDate = (day: number) =>
    `${visibleMonth.getFullYear()}-${String(visibleMonth.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`

  return <div className="page-stack">
    <div className="section-heading"><div><h2>Plan your next sessions</h2><p className="muted">Schedule workouts and keep upcoming plans in view.</p></div></div>
    <div className="content-grid workout-layout">
      <form className="panel form-panel" onSubmit={createPlan}>
        <div className="panel-heading"><div><h3>Schedule a workout</h3><p className="muted">Add a future session to your planner.</p></div><CalendarDays size={19} /></div>
        <label>Workout title<input required minLength={2} maxLength={120} value={title} onChange={event => setTitle(event.target.value)} placeholder="e.g. Upper-body strength" /></label>
        <label>Description<textarea maxLength={2000} rows={4} value={description} onChange={event => setDescription(event.target.value)} placeholder="Optional notes or focus for this session" /></label>
        <label>Scheduled date<input type="date" min={localDateString()} required value={scheduledDate} onChange={event => setScheduledDate(event.target.value)} /></label>
        {error && <p className="error">{error}</p>}
        <button className="primary full"><Plus size={16} /> {editingPlan ? 'Update workout plan' : 'Schedule workout'}</button>
        {editingPlan && <button type="button" className="secondary full" onClick={() => { setEditingPlan(null); setTitle(''); setDescription(''); setScheduledDate(localDateString()) }}>Cancel edit</button>}
      </form>
      <section className="panel">
        <div className="panel-heading"><div><h3>Workout calendar</h3><p className="muted">Scheduled workout dates.</p></div></div>
        <div className="calendar-month"><button className="icon-button" aria-label="Previous month" onClick={() => setVisibleMonth(new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() - 1, 1))}><ChevronLeft size={17} /></button><strong>{visibleMonth.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}</strong><button className="icon-button" aria-label="Next month" onClick={() => setVisibleMonth(new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() + 1, 1))}><ChevronRight size={17} /></button></div>
        <div className="calendar-grid">{['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => <span className="calendar-weekday" key={day}>{day}</span>)}
          {calendarDays.map((day, index) => <div className={`calendar-cell ${day && planDates.has(formatLocalDate(day)) ? 'has-plan' : ''}`} key={day ?? `blank-${index}`}>
            {day && <><span>{day}</span>{planDates.has(formatLocalDate(day)) && <i aria-label="Workout scheduled" />}</>}
          </div>)}
        </div>
        <div className="panel-heading upcoming-heading"><div><h3>Upcoming sessions</h3><p className="muted">Your next planned workouts.</p></div></div>
        {upcomingPlans.length ? <div className="planned-list">{upcomingPlans.map(plan => <article className="planned-item" key={plan.id}>
          <div className="planned-date"><strong>{new Date(`${plan.scheduled_date}T12:00:00`).getDate()}</strong><span>{new Date(`${plan.scheduled_date}T12:00:00`).toLocaleDateString(undefined, { month: 'short' })}</span></div>
          <div className="planned-copy"><strong>{plan.title}</strong><span>{plan.scheduled_date}</span>{plan.description && <p>{plan.description}</p>}</div>
          <div className="plan-actions"><button className="icon-button" title="Edit plan" onClick={() => { setEditingPlan(plan); setTitle(plan.title); setDescription(plan.description); setScheduledDate(plan.scheduled_date) }}><Pencil size={15} /></button><button className="icon-button danger" title="Delete plan" onClick={() => void deletePlan(plan.id)}><Trash2 size={16} /></button></div>
        </article>)}</div> : <div className="empty-state">No upcoming workouts scheduled.</div>}
      </section>
    </div>
  </div>
}

export function ExerciseLibrary({ refresh, workouts, onRefresh }: {
  refresh: number
  workouts: { id: number; workout_name: string }[]
  onRefresh: () => void
}) {
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const timer = window.setTimeout(() => {
      api.get<Exercise[]>('/exercises', { params: { search: search || undefined, category: category || undefined } })
        .then(response => setExercises(response.data))
        .catch((e: any) => setMessage(e?.response?.data?.detail || 'Could not load the exercise library.'))
    }, 200)
    return () => window.clearTimeout(timer)
  }, [search, category, refresh])

  async function addExercise(exercise: Exercise) {
    const workout = workouts[0]
    if (!workout) {
      setMessage('Log a workout first, then select an exercise to add it.')
      return
    }
    try {
      await api.post(`/workouts/${workout.id}/exercises`, { exercise_id: exercise.id })
      setMessage(`${exercise.name} added to ${workout.workout_name}.`)
      onRefresh()
    } catch (e: any) {
      setMessage(e?.response?.data?.detail || 'Could not add exercise to workout.')
    }
  }

  return <div className="page-stack">
    <div className="section-heading"><div><h2>Exercise library</h2><p className="muted">Search curated Cardio, Strength, and Yoga exercises.</p></div></div>
    <section className="panel">
      <div className="library-filters">
        <label className="search-field"><Search size={17} /><input value={search} onChange={event => setSearch(event.target.value)} placeholder="Search exercises" aria-label="Search exercises" /></label>
        <select value={category} onChange={event => setCategory(event.target.value)} aria-label="Filter by category">
          <option value="">All categories</option><option>Cardio</option><option>Strength</option><option>Yoga</option>
        </select>
      </div>
      {message && <p className="muted">{message}</p>}
      <div className="exercise-grid">{exercises.map(exercise => <article className="exercise-card" key={exercise.id}>
        <div className="exercise-card-top"><span className="category-chip">{exercise.category}</span><span className="muted small">{exercise.duration} min</span></div>
        <h3>{exercise.name}</h3><p>{exercise.description}</p>
        <button className="text-button" onClick={() => void addExercise(exercise)}><Plus size={15} /> Add to latest workout</button>
      </article>)}</div>
      {!exercises.length && <div className="empty-state">No exercises match these filters.</div>}
    </section>
  </div>
}

export function Achievements({ refresh }: { refresh: number }) {
  const [streak, setStreak] = useState<Streak | null>(null)
  const [earned, setEarned] = useState<Badge[]>([])
  const [catalog, setCatalog] = useState<Badge[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      api.get<Streak>('/streak'),
      api.get<{ badge: Badge; earned_at: string }[]>('/badges'),
      api.get<Badge[]>('/badges/catalog'),
    ]).then(([streakResponse, earnedResponse, catalogResponse]) => {
      setStreak(streakResponse.data)
      setEarned(earnedResponse.data.map(item => item.badge))
      setCatalog(catalogResponse.data)
      setError('')
    }).catch((e: any) => setError(e?.response?.data?.detail || 'Could not load achievements.'))
  }, [refresh])

  const earnedIds = new Set(earned.map(badge => badge.id))
  return <div className="page-stack">
    <div className="section-heading"><div><h2>Consistency & achievements</h2><p className="muted">Celebrate the sessions and milestones you have completed.</p></div></div>
    {error && <div className="error">{error}</div>}
    <div className="stats-grid three">
      <div className="stat-card streak-card"><div className="stat-icon orange"><Flame /></div><p>Current streak</p><div className="stat-value">{streak?.current_streak ?? 0}<span>days</span></div></div>
      <div className="stat-card"><div className="stat-icon purple"><Award /></div><p>Longest streak</p><div className="stat-value">{streak?.longest_streak ?? 0}<span>days</span></div></div>
      <div className="stat-card"><div className="stat-icon green"><Award /></div><p>Badges earned</p><div className="stat-value">{earned.length}<span>of {catalog.length}</span></div></div>
    </div>
    <section className="panel"><div className="panel-heading"><div><h3>Badge collection</h3><p className="muted">Your earned milestones and what is still ahead.</p></div></div>
      <div className="badge-grid">{catalog.map(badge => <article className={`badge-card ${earnedIds.has(badge.id) ? 'earned' : ''}`} key={badge.id}>
        <div className="badge-icon"><Award size={22} /></div><div><strong>{badge.name}</strong><p>{badge.description}</p><span className="muted small">{earnedIds.has(badge.id) ? 'Earned' : 'Not earned yet'}</span></div>
      </article>)}</div>
    </section>
  </div>
}

export function DashboardEngagement({ refresh, onNavigate }: { refresh: number; onNavigate: (page: string) => void }) {
  const [data, setData] = useState<{
    upcoming_workouts: WorkoutPlan[]
    streak: Streak
    badges: { badge: Badge }[]
  } | null>(null)
  const [error, setError] = useState('')
  const [newBadge, setNewBadge] = useState<Badge | null>(null)

  useEffect(() => {
    api.get('/dashboard').then(response => {
      setData(response.data)
      const earned = response.data.badges.map((item: { badge: Badge }) => item.badge)
      const storageKey = 'fittrack_seen_badges'
      const previous = sessionStorage.getItem(storageKey)
      if (previous !== null) {
        const previousIds = new Set(previous.split(',').filter(Boolean))
        setNewBadge(earned.find((badge: Badge) => !previousIds.has(String(badge.id))) || null)
      }
      sessionStorage.setItem(storageKey, earned.map((badge: Badge) => badge.id).join(','))
      setError('')
    }).catch((e: any) => setError(e?.response?.data?.detail || 'Could not load personalized dashboard data.'))
  }, [refresh])

  return <>
    {error && <div className="error">{error}</div>}
    {newBadge && <div className="achievement-backdrop" role="presentation" onClick={() => setNewBadge(null)}>
      <section className="achievement-dialog" role="dialog" aria-modal="true" aria-labelledby="achievement-title" onClick={event => event.stopPropagation()}>
        <div className="badge-icon earned"><Award size={28} /></div><p className="eyebrow">MILESTONE UNLOCKED</p><h2 id="achievement-title">{newBadge.name}</h2><p>{newBadge.description}</p>
        <button className="primary" onClick={() => setNewBadge(null)}>Celebrate</button>
      </section>
    </div>}
    <div className="content-grid">
      <section className="panel"><div className="panel-heading"><div><h3>Upcoming workouts</h3><p className="muted">Your next planned sessions</p></div><button className="text-button" onClick={() => onNavigate('Schedule')}>Plan →</button></div>
        {data?.upcoming_workouts.length ? <div className="planned-list">{data.upcoming_workouts.slice(0, 3).map(plan => <article className="planned-item compact" key={plan.id}><div className="planned-date"><strong>{new Date(`${plan.scheduled_date}T12:00:00`).getDate()}</strong><span>{new Date(`${plan.scheduled_date}T12:00:00`).toLocaleDateString(undefined, { month: 'short' })}</span></div><div className="planned-copy"><strong>{plan.title}</strong><span>{plan.scheduled_date}</span></div></article>)}</div> : <div className="empty-state">No future sessions yet. Add one to your schedule.</div>}
      </section>
      <section className="panel"><div className="panel-heading"><div><h3>Streak & achievements</h3><p className="muted">Small habits add up over time.</p></div><button className="text-button" onClick={() => onNavigate('Achievements')}>View all →</button></div>
        <div className="dashboard-streak"><Flame size={22} /><strong>{data?.streak.current_streak ?? 0} day streak</strong><span>Best: {data?.streak.longest_streak ?? 0} days</span></div>
        {data?.badges.length ? <div className="dashboard-badges">{data.badges.slice(0, 3).map(item => <span className="category-chip" key={item.badge.id}><Award size={13} /> {item.badge.name}</span>)}</div> : <p className="muted small">Log workouts to earn your first badge.</p>}
      </section>
    </div>
  </>
}
