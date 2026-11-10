import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { Activity, Award, Bell, BookOpen, CalendarDays, CalendarRange, ChartNoAxesCombined, Check, Dumbbell, Flag, Flame, LayoutDashboard, LogOut, Pencil, Plus, Trash2, UserRound } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from './services/api'
import { logout as clearAuth } from './services/authService'
import type { Goal, Notification, User, Workout } from './types'
import { Achievements, DashboardEngagement, ExerciseLibrary, WorkoutPlans } from './pages/AdvancedFeatures'
import { AuthPage } from './pages/AuthPage'
import { useFitnessData } from './hooks/useFitnessData'
import { EmptyState as Empty, StatCard } from './components/StatCard'
import { localDateString } from './utils/date'

const today = () => localDateString()

function Protected({ children }: { children: JSX.Element }) {
  return localStorage.getItem('fittrack_token') ? children : <Navigate to="/login" replace />
}

export default function App() {
  const [user, setUser] = useState<User | null>(null)
  const [refresh, setRefresh] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    if (!localStorage.getItem('fittrack_token')) return
    api.get<User>('/auth/me').then(r => setUser(r.data)).catch(() => {
      localStorage.removeItem('fittrack_token'); setUser(null)
    })
  }, [refresh])

  const logout = () => {
    clearAuth()
    setUser(null)
    navigate('/login')
  }

  return (
    <Routes>
      <Route path="/login" element={<AuthPage mode="login" onAuth={u => { setUser(u); setRefresh(v => v + 1); navigate('/') }} />} />
      <Route path="/register" element={<AuthPage mode="register" onAuth={() => navigate('/login')} />} />
      <Route path="/*" element={<Protected><Shell user={user} onLogout={logout} refresh={refresh} onRefresh={() => setRefresh(v => v + 1)} /></Protected>} />
    </Routes>
  )
}

function Shell({ user, onLogout, refresh, onRefresh }: { user: User | null; onLogout: () => void; refresh: number; onRefresh: () => void }) {
  const [page, setPage] = useState('Overview')
  const nav = [
    { name: 'Overview', icon: LayoutDashboard }, { name: 'Workouts', icon: Dumbbell },
    { name: 'Goals', icon: Flag }, { name: 'Analytics', icon: ChartNoAxesCombined },
    { name: 'Schedule', icon: CalendarRange }, { name: 'Exercise Library', icon: BookOpen },
    { name: 'Achievements', icon: Award }, { name: 'Notifications', icon: Bell },
  ]
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Activity /></div><span>FitTrack</span></div>
      <p className="nav-label">WORKSPACE</p>
      <nav>{nav.map(item => <button key={item.name} className={`nav-item ${page === item.name ? 'active' : ''}`} onClick={() => setPage(item.name)}><item.icon size={18} />{item.name}{item.name === 'Notifications' && <span className="nav-dot" />}</button>)}</nav>
      <div className="sidebar-bottom"><div className="user-avatar"><UserRound size={18} /></div><div className="user-meta"><strong>{user?.username || 'Your account'}</strong><span>Fitness member</span></div><button className="icon-button" title="Sign out" onClick={onLogout}><LogOut size={17} /></button></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div><p className="eyebrow">FITNESS MANAGEMENT</p><h1>{page}</h1></div><div className="topbar-right"><span className="date-pill"><CalendarDays size={15} /> {new Date().toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</span><div className="top-avatar">{(user?.username || 'F').slice(0, 1).toUpperCase()}</div></div></header>
      {page === 'Overview' && <Dashboard refresh={refresh} onNavigate={setPage} />}
      {page === 'Workouts' && <Workouts refresh={refresh} onRefresh={onRefresh} />}
      {page === 'Goals' && <Goals refresh={refresh} onRefresh={onRefresh} />}
      {page === 'Analytics' && <Analytics refresh={refresh} />}
      {page === 'Schedule' && <WorkoutPlans refresh={refresh} onRefresh={onRefresh} />}
      {page === 'Exercise Library' && <ExerciseLibraryPage refresh={refresh} onRefresh={onRefresh} />}
      {page === 'Achievements' && <Achievements refresh={refresh} />}
      {page === 'Notifications' && <Notifications refresh={refresh} />}
    </main>
  </div>
}

function ExerciseLibraryPage({ refresh, onRefresh }: { refresh: number; onRefresh: () => void }) {
  const { workouts } = useFitnessData(refresh)
  return <ExerciseLibrary refresh={refresh} workouts={workouts} onRefresh={onRefresh} />
}

function Dashboard({ refresh, onNavigate }: { refresh: number; onNavigate: (page: string) => void }) {
  const { workouts, goals, notifications, summary, error } = useFitnessData(refresh)
  const recent = workouts.slice(0, 4)
  return <div className="page-stack">
    <section className="welcome-banner"><div><p className="eyebrow light">YOUR JOURNEY CONTINUES</p><h2>Progress over perfection.</h2><p>Every workout is a step toward a stronger you.</p><button className="light-button" onClick={() => onNavigate('Workouts')}><Plus size={16} /> Log a workout</button></div><div className="banner-art"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><Dumbbell size={74} strokeWidth={1.2} /></div></section>
    {error && <div className="error">{error}</div>}
    <div className="section-heading"><div><h2>Today's activity</h2><p className="muted">A quick look at your effort today.</p></div></div>
    <div className="stats-grid">
      <StatCard icon={<Dumbbell />} label="Workouts today" value={summary?.total_workouts ?? 0} unit="sessions" color="green" />
      <StatCard icon={<Flame />} label="Calories burned" value={(summary?.total_calories ?? 0).toLocaleString()} unit="kcal" color="orange" />
      <StatCard icon={<Activity />} label="Active minutes" value={summary?.total_duration ?? 0} unit="minutes" color="blue" />
      <StatCard icon={<Flag />} label="Active goals" value={goals.filter(g => g.status !== 'COMPLETED').length} unit="goals" color="purple" />
    </div>
    <div className="content-grid">
      <section className="panel"><div className="panel-heading"><div><h3>Recent workouts</h3><p className="muted">Your latest sessions</p></div><button className="text-button" onClick={() => onNavigate('Workouts')}>View all →</button></div>
        {recent.length ? <div className="workout-mini-list">{recent.map(w => <div className="workout-mini" key={w.id}><div className="workout-symbol"><Dumbbell size={18} /></div><div className="workout-info"><strong>{w.workout_name}</strong><span>{w.category} · {w.duration} min · {w.workout_date}</span></div><span className="calorie-value">{w.calories_burned} kcal</span></div>)}</div> : <Empty text="No workouts yet. Log your first session to get started." />}
      </section>
      <section className="panel"><div className="panel-heading"><div><h3>Goal progress</h3><p className="muted">Keep your targets in sight</p></div><button className="text-button" onClick={() => onNavigate('Goals')}>Manage →</button></div>
        {goals.length ? <div className="goal-list">{goals.slice(0, 4).map(g => <div className="goal-row" key={g.id}><div className="goal-row-top"><strong>{g.goal_type}</strong><span>{Math.min(100, Math.round(g.current_value / g.target_value * 100))}%</span></div><div className="progress-track"><div className="progress-fill" style={{ width: `${Math.min(100, g.current_value / g.target_value * 100)}%` }} /></div><span className="muted small">{g.current_value} / {g.target_value}</span></div>)}</div> : <Empty text="Create a goal to start tracking progress." />}
      </section>
    </div>
    <div className="bottom-note"><Bell size={17} /><span>{notifications.filter(n => !n.is_read).length ? `You have ${notifications.filter(n => !n.is_read).length} unread notification(s).` : 'You are all caught up.'}</span><button className="text-button" onClick={() => onNavigate('Notifications')}>Notifications →</button></div>
    <DashboardEngagement refresh={refresh} onNavigate={onNavigate} />
  </div>
}

function Workouts({ refresh, onRefresh }: { refresh: number; onRefresh: () => void }) {
  const { workouts, error } = useFitnessData(refresh)
  const [name, setName] = useState('')
  const [category, setCategory] = useState<'Cardio' | 'Strength' | 'Yoga'>('Strength')
  const [duration, setDuration] = useState(30)
  const [calories, setCalories] = useState(200)
  const [date, setDate] = useState(today())
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const [editingWorkout, setEditingWorkout] = useState<Workout | null>(null)

  async function addWorkout(e: FormEvent) {
    e.preventDefault(); setMessage(''); setBusy(true)
    try {
      const payload = { workout_name: name, category, duration, calories_burned: calories, workout_date: date }
      if (editingWorkout) {
        await api.patch(`/workouts/${editingWorkout.id}`, payload)
        setEditingWorkout(null)
        setMessage('Workout updated successfully.')
      } else {
        await api.post('/workouts', payload)
        setMessage('Workout added successfully.')
      }
      setName(''); onRefresh()
    } catch (e: any) { setMessage(e?.response?.data?.detail || 'Could not add workout.') }
    finally { setBusy(false) }
  }
  function editWorkout(workout: Workout) {
    setEditingWorkout(workout)
    setName(workout.workout_name)
    setCategory(workout.category)
    setDuration(workout.duration)
    setCalories(workout.calories_burned)
    setDate(workout.workout_date)
  }
  async function deleteWorkout(id: number) {
    if (!confirm('Delete this workout?')) return
    try { await api.delete(`/workouts/${id}`); onRefresh() } catch { setMessage('Could not delete workout.') }
  }

  return <div className="page-stack">
    <div className="section-heading"><div><h2>Workout log</h2><p className="muted">Record your sessions and build consistency.</p></div><span className="count-pill">{workouts.length} sessions</span></div>
    <div className="content-grid workout-layout">
      <form className="panel form-panel" onSubmit={addWorkout}><div className="panel-heading"><div><h3>{editingWorkout ? 'Edit workout' : 'Log a workout'}</h3><p className="muted">{editingWorkout ? 'Update your completed session' : 'Add a completed session'}</p></div><div className="small-icon"><Plus size={18} /></div></div>
        <label>Workout name<input required minLength={2} maxLength={120} value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Morning run" /></label>
        <label>Category<select value={category} onChange={e => setCategory(e.target.value as any)}><option>Strength</option><option>Cardio</option><option>Yoga</option></select></label>
        <div className="form-two"><label>Duration (minutes)<input type="number" min="1" max="1440" required value={duration} onChange={e => setDuration(Number(e.target.value))} /></label><label>Calories (kcal)<input type="number" min="0" max="20000" required value={calories} onChange={e => setCalories(Number(e.target.value))} /></label></div>
        <label>Workout date<input type="date" required value={date} onChange={e => setDate(e.target.value)} /></label>
        {message && <p className={message.includes('successfully') ? 'success-text' : 'error'}>{message}</p>}
        <button className="primary full" disabled={busy}><Plus size={17} /> {busy ? 'Saving…' : editingWorkout ? 'Update workout' : 'Save workout'}</button>
        {editingWorkout && <button type="button" className="secondary full" onClick={() => { setEditingWorkout(null); setName('') }}>Cancel edit</button>}
      </form>
      <section className="panel"><div className="panel-heading"><div><h3>Workout history</h3><p className="muted">All your logged sessions</p></div></div>
        {error && <div className="error">{error}</div>}
        {workouts.length ? <div className="table-wrap"><table><thead><tr><th>Workout</th><th>Date</th><th>Duration</th><th>Calories</th><th></th></tr></thead><tbody>{workouts.map(w => <tr key={w.id}><td><strong>{w.workout_name}</strong><span className="table-sub">{w.category}</span></td><td>{w.workout_date}</td><td>{w.duration} min</td><td>{w.calories_burned} kcal</td><td><button className="icon-button" title="Edit workout" onClick={() => editWorkout(w)}><Pencil size={15} /></button><button className="icon-button danger" title="Delete workout" onClick={() => deleteWorkout(w.id)}><Trash2 size={16} /></button></td></tr>)}</tbody></table></div> : <Empty text="Your workout history will appear here." />}
      </section>
    </div>
  </div>
}

function Goals({ refresh, onRefresh }: { refresh: number; onRefresh: () => void }) {
  const { goals, error } = useFitnessData(refresh)
  const [type, setType] = useState<'Weight Loss' | 'Muscle Gain' | 'Steps'>('Steps')
  const [target, setTarget] = useState(10000)
  const [current, setCurrent] = useState(0)
  const [deadline, setDeadline] = useState('')
  const [message, setMessage] = useState('')

  async function addGoal(e: FormEvent) {
    e.preventDefault(); setMessage('')
    try { await api.post('/goals', { goal_type: type, target_value: target, current_value: current, deadline: deadline || null }); setMessage('Goal created.'); onRefresh() }
    catch (e: any) { setMessage(e?.response?.data?.detail || 'Could not create goal.') }
  }
  async function updateGoal(goal: Goal, value: number) {
    try { await api.patch(`/goals/${goal.id}`, { current_value: value }); onRefresh() }
    catch { setMessage('Could not update goal.') }
  }
  async function deleteGoal(id: number) {
    if (!confirm('Delete this goal?')) return
    try { await api.delete(`/goals/${id}`); onRefresh() } catch { setMessage('Could not delete goal.') }
  }

  return <div className="page-stack">
    <div className="section-heading"><div><h2>Your fitness goals</h2><p className="muted">Choose a target, track progress, and celebrate milestones.</p></div><span className="count-pill">{goals.length} total</span></div>
    <div className="content-grid workout-layout">
      <form className="panel form-panel" onSubmit={addGoal}><div className="panel-heading"><div><h3>Set a new goal</h3><p className="muted">Make your next milestone measurable.</p></div><Flag size={19} /></div>
        <label>Goal type<select value={type} onChange={e => { setType(e.target.value as any); setTarget(e.target.value === 'Steps' ? 10000 : 5); setCurrent(0) }}><option>Steps</option><option>Weight Loss</option><option>Muscle Gain</option></select></label>
        <div className="form-two"><label>Target value<input type="number" min="0.1" required value={target} onChange={e => setTarget(Number(e.target.value))} /></label><label>Current value<input type="number" min="0" required value={current} onChange={e => setCurrent(Number(e.target.value))} /></label></div>
        <label>Deadline (optional)<input type="date" value={deadline} onChange={e => setDeadline(e.target.value)} /></label>
        {message && <p className={message === 'Goal created.' ? 'success-text' : 'error'}>{message}</p>}
        <button className="primary full"><Plus size={17} /> Create goal</button>
      </form>
      <section className="panel"><div className="panel-heading"><div><h3>Goal tracker</h3><p className="muted">Update the current value as you progress.</p></div></div>
        {error && <div className="error">{error}</div>}
        {goals.length ? <div className="goal-list large">{goals.map(g => { const percent = Math.min(100, Math.round(g.current_value / g.target_value * 100)); return <div className="goal-card" key={g.id}><div className="goal-row-top"><div><strong>{g.goal_type}</strong><span className={`status ${g.status === 'COMPLETED' ? 'done' : ''}`}>{g.status === 'COMPLETED' ? 'Completed' : 'In progress'}</span></div><button className="icon-button danger" onClick={() => deleteGoal(g.id)} title="Delete goal"><Trash2 size={16} /></button></div><div className="goal-big-percent">{percent}<span>%</span></div><div className="progress-track"><div className="progress-fill" style={{ width: `${percent}%` }} /></div><div className="goal-footer"><span>{g.current_value} / {g.target_value}</span><span>{g.deadline ? `Due ${g.deadline}` : 'No deadline'}</span></div><label className="update-current">Update progress<input type="number" min="0" value={g.current_value} onChange={e => updateGoal(g, Number(e.target.value))} /></label></div> })}</div> : <Empty text="No goals yet. Create one to begin tracking." />}
      </section>
    </div>
  </div>
}

function Analytics({ refresh }: { refresh: number }) {
  const [weekly, setWeekly] = useState<any[]>([])
  const [monthly, setMonthly] = useState<any>(null)
  const [comparison, setComparison] = useState<any>(null)
  const [monthlyComparison, setMonthlyComparison] = useState<any>(null)
  const [error, setError] = useState('')
  useEffect(() => {
    const now = new Date()
    Promise.all([
      api.get('/progress/weekly'),
      api.get('/progress/monthly', { params: { year: now.getFullYear(), month: now.getMonth() + 1 } }),
      api.get('/progress/comparison', { params: { period: 'weekly' } }),
      api.get('/progress/comparison', { params: { period: 'monthly' } }),
    ]).then(([w, m, c, mc]) => { setWeekly(w.data.days); setMonthly(m.data); setComparison(c.data); setMonthlyComparison(mc.data); setError('') })
      .catch((e: any) => setError(e?.response?.data?.detail || 'Could not load analytics.'))
  }, [refresh])
  const chartData = useMemo(() => weekly.map(d => ({ day: new Date(`${d.date}T12:00:00`).toLocaleDateString(undefined, { weekday: 'short' }), workouts: d.total_workouts, calories: d.total_calories })), [weekly])
  return <div className="page-stack">
    <div className="section-heading"><div><h2>Your activity insights</h2><p className="muted">Understand your consistency and effort over time.</p></div></div>
    {error && <div className="error">{error}</div>}
    <div className="stats-grid three">
      <StatCard icon={<Dumbbell />} label="This month" value={monthly?.total_workouts ?? 0} unit="workouts" color="green" />
      <StatCard icon={<Flame />} label="Calories this month" value={(monthly?.total_calories ?? 0).toLocaleString()} unit="kcal" color="orange" />
      <StatCard icon={<Activity />} label="Active time this month" value={monthly?.total_duration ?? 0} unit="minutes" color="blue" />
    </div>
    {[{ title: 'Week-over-week comparison', data: comparison }, { title: 'Month-over-month comparison', data: monthlyComparison }].map(item => <section className="panel comparison-panel" key={item.title}><div className="panel-heading"><div><h3>{item.title}</h3><p className="muted">Change from the preceding period.</p></div></div>
      <div className="comparison-grid">{(['workouts', 'calories', 'duration'] as const).map(key => <div key={key}><span className="muted small">{key === 'workouts' ? 'Workouts' : key === 'calories' ? 'Calories' : 'Active minutes'}</span><strong>{item.data?.change?.[key] > 0 ? '+' : ''}{item.data?.change?.[key] ?? 0}{key === 'calories' ? ' kcal' : key === 'duration' ? ' min' : ''}</strong></div>)}</div>
    </section>)}
    <section className="panel chart-panel"><div className="panel-heading"><div><h3>Weekly calories burned</h3><p className="muted">Daily calories from your logged workouts</p></div><span className="count-pill">This week</span></div>
      <div className="chart-area">{chartData.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={chartData} margin={{ top: 12, right: 8, left: 0, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e7ece8" /><XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#849087', fontSize: 12 }} /><YAxis axisLine={false} tickLine={false} tick={{ fill: '#849087', fontSize: 12 }} /><Tooltip cursor={{ fill: '#f2f7f3' }} /><Bar dataKey="calories" fill="#53a875" radius={[6, 6, 0, 0]} /></BarChart></ResponsiveContainer> : <Empty text="Log workouts to see your weekly chart." />}</div>
    </section>
    <section className="panel"><div className="panel-heading"><div><h3>Weekly breakdown</h3><p className="muted">A day-by-day view of your sessions.</p></div></div>
      {weekly.length ? <div className="table-wrap"><table><thead><tr><th>Date</th><th>Workouts</th><th>Calories</th><th>Duration</th></tr></thead><tbody>{weekly.map(d => <tr key={d.date}><td>{d.date}</td><td>{d.total_workouts}</td><td>{d.total_calories} kcal</td><td>{d.total_duration} min</td></tr>)}</tbody></table></div> : <Empty text="No activity to report yet." />}
    </section>
  </div>
}

function Notifications({ refresh }: { refresh: number }) {
  const { notifications } = useFitnessData(refresh)
  const [items, setItems] = useState<Notification[]>([])
  const [message, setMessage] = useState('')
  useEffect(() => setItems(notifications), [notifications])
  async function markRead(item: Notification) {
    try { const response = await api.patch(`/notifications/${item.id}/read`); setItems(old => old.map(n => n.id === item.id ? response.data : n)) }
    catch { setMessage('Could not mark notification as read.') }
  }
  async function reminder() {
    try { const response = await api.post('/notifications/reminder'); setItems(old => [response.data, ...old]); setMessage('Reminder created.') }
    catch { setMessage('Could not create reminder.') }
  }
  return <div className="page-stack">
    <div className="section-heading"><div><h2>Notifications</h2><p className="muted">Stay on top of your fitness activity and milestones.</p></div><button className="primary" onClick={reminder}><Bell size={16} /> Create reminder</button></div>
    {message && <p className="success-text">{message}</p>}
    <section className="panel notification-panel">
      {items.length ? items.map(n => <div className={`notification-item ${n.is_read ? '' : 'unread'}`} key={n.id}><div className="notification-symbol"><Bell size={18} /></div><div className="notification-copy"><div className="notification-title">{n.title}{!n.is_read && <span className="unread-dot" />}</div><p>{n.message}</p><span className="muted small">{new Date(n.created_at).toLocaleString()}</span></div>{!n.is_read && <button className="text-button" onClick={() => markRead(n)}><Check size={15} /> Mark read</button>}</div>) : <Empty text="No notifications yet. Create a reminder to get started." />}
    </section>
  </div>
}
