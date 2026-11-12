import { FormEvent, useEffect, useState } from 'react'
import { Activity, Bell, Droplets, Flame, Plus, Sparkles, Trash2 } from 'lucide-react'

import { api } from '../services/api'
import type { Meal, NutritionSummary, UserPreferences, WaterSummary, WorkoutRecommendation } from '../types'
import { localDateString } from '../utils/date'

export function NutritionPage({ refresh }: { refresh: number }) {
  const [meals, setMeals] = useState<Meal[]>([])
  const [nutrition, setNutrition] = useState<NutritionSummary | null>(null)
  const [water, setWater] = useState<WaterSummary | null>(null)
  const [mealType, setMealType] = useState<Meal['meal_type']>('Breakfast')
  const [foodName, setFoodName] = useState('')
  const [calories, setCalories] = useState(0)
  const [protein, setProtein] = useState(0)
  const [carbs, setCarbs] = useState(0)
  const [fats, setFats] = useState(0)
  const [waterAmount, setWaterAmount] = useState(250)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function load() {
    try {
      const [mealResponse, nutritionResponse, waterResponse] = await Promise.all([
        api.get<Meal[]>('/nutrition/meals', { params: { on_date: localDateString() } }),
        api.get<NutritionSummary>('/nutrition/summary', { params: { on_date: localDateString() } }),
        api.get<WaterSummary>('/water', { params: { on_date: localDateString() } }),
      ])
      setMeals(mealResponse.data)
      setNutrition(nutritionResponse.data)
      setWater(waterResponse.data)
      setError('')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Could not load nutrition and hydration data.')
    }
  }
  useEffect(() => { void load() }, [refresh])

  async function addMeal(event: FormEvent) {
    event.preventDefault()
    try {
      await api.post('/nutrition/meals', { meal_type: mealType, food_name: foodName, calories, protein, carbs, fats, meal_date: localDateString() })
      setFoodName('')
      setMessage('Meal saved.')
      await load()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Could not save this meal.')
    }
  }
  async function deleteMeal(id: number) {
    try { await api.delete(`/nutrition/meals/${id}`); await load() }
    catch (e: any) { setError(e?.response?.data?.detail || 'Could not delete this meal.') }
  }
  async function addWater(event: FormEvent) {
    event.preventDefault()
    try {
      await api.post('/water', { quantity: waterAmount, date: localDateString() })
      setMessage('Water intake logged.')
      await load()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Could not log water intake.')
    }
  }
  async function deleteWater(id: number) {
    try { await api.delete(`/water/${id}`); await load() }
    catch (e: any) { setError(e?.response?.data?.detail || 'Could not delete this water entry.') }
  }

  return <div className="page-stack">
    <div className="section-heading"><div><h2>Nutrition & hydration</h2><p className="muted">Track what you eat and drink throughout the day.</p></div></div>
    {error && <p className="error">{error}</p>}
    {message && <p className="success-text">{message}</p>}
    <div className="stats-grid three">
      <div className="stat-card"><div className="stat-icon orange"><Flame /></div><p>Calories consumed</p><div className="stat-value">{nutrition?.calories ?? 0}<span>kcal</span></div></div>
      <div className="stat-card"><div className="stat-icon green"><Activity /></div><p>Protein</p><div className="stat-value">{Math.round(nutrition?.protein ?? 0)}<span>g</span></div></div>
      <div className="stat-card"><div className="stat-icon blue"><Droplets /></div><p>Water today</p><div className="stat-value">{((water?.total_ml ?? 0) / 1000).toFixed(1)}<span>/ {((water?.goal_ml ?? 2000) / 1000).toFixed(1)} L</span></div></div>
    </div>
    <div className="content-grid workout-layout">
      <form className="panel form-panel" onSubmit={addMeal}>
        <div className="panel-heading"><div><h3>Add a meal</h3><p className="muted">Log calories and macronutrients.</p></div><Flame size={18} /></div>
        <label>Meal type<select value={mealType} onChange={event => setMealType(event.target.value as Meal['meal_type'])}><option>Breakfast</option><option>Lunch</option><option>Dinner</option><option>Snacks</option></select></label>
        <label>Food name<input required maxLength={120} value={foodName} onChange={event => setFoodName(event.target.value)} placeholder="e.g. Oatmeal with berries" /></label>
        <label>Calories (kcal)<input type="number" min="0" max="10000" required value={calories} onChange={event => setCalories(Number(event.target.value))} /></label>
        <div className="form-two">
          <label>Protein (g)<input type="number" min="0" max="1000" step="0.1" value={protein} onChange={event => setProtein(Number(event.target.value))} /></label>
          <label>Carbs (g)<input type="number" min="0" max="1000" step="0.1" value={carbs} onChange={event => setCarbs(Number(event.target.value))} /></label>
        </div>
        <label>Fats (g)<input type="number" min="0" max="1000" step="0.1" value={fats} onChange={event => setFats(Number(event.target.value))} /></label>
        <button className="primary full"><Plus size={16} /> Save meal</button>
      </form>
      <section className="panel">
        <div className="panel-heading"><div><h3>Today's meals</h3><p className="muted">Macro summary: {Math.round(nutrition?.carbs ?? 0)}g carbs · {Math.round(nutrition?.fats ?? 0)}g fats</p></div><span className="count-pill">{localDateString()}</span></div>
        {meals.length ? <div className="planned-list">{meals.map(meal => <article className="planned-item" key={meal.id}>
          <div className="workout-symbol"><Flame size={17} /></div><div className="planned-copy"><strong>{meal.food_name}</strong><span>{meal.meal_type} · {meal.calories} kcal · P {meal.protein}g / C {meal.carbs}g / F {meal.fats}g</span></div>
          <button className="icon-button danger" title="Delete meal" onClick={() => void deleteMeal(meal.id)}><Trash2 size={16} /></button>
        </article>)}</div> : <div className="empty-state">No meals logged today.</div>}
      </section>
    </div>
    <section className="panel water-panel">
      <div className="panel-heading"><div><h3>Water tracker</h3><p className="muted">{water?.total_ml ?? 0} ml of {water?.goal_ml ?? 2000} ml today</p></div><Droplets /></div>
      <div className="progress-track water-progress"><div className="progress-fill" style={{ width: `${water?.progress_percent ?? 0}%` }} /></div>
      <div className="water-controls"><form onSubmit={addWater}><label>Add water<input type="number" min="1" max="5000" value={waterAmount} onChange={event => setWaterAmount(Number(event.target.value))} /><span>ml</span></label><button className="primary"><Plus size={16} /> Log water</button></form>
        <div className="water-entry-list">{water?.entries.map(entry => <span className="water-entry" key={entry.id}>{entry.quantity} ml<button className="icon-button danger" title="Remove water entry" onClick={() => void deleteWater(entry.id)}><Trash2 size={13} /></button></span>)}</div>
      </div>
    </section>
  </div>
}

export function RecommendationsPage({ onNavigate }: { onNavigate: (page: string) => void }) {
  const [items, setItems] = useState<WorkoutRecommendation[]>([])
  const [error, setError] = useState('')
  useEffect(() => {
    api.get<WorkoutRecommendation[]>('/recommendations')
      .then(response => { setItems(response.data); setError('') })
      .catch((e: any) => setError(e?.response?.data?.detail || 'Could not load workout recommendations.'))
  }, [])
  return <div className="page-stack">
    <div className="section-heading"><div><h2>Recommended workouts</h2><p className="muted">Suggestions adapt to your goals, recent activity, and consistency.</p></div><Sparkles /></div>
    {error && <p className="error">{error}</p>}
    <div className="recommendation-grid">{items.map(({ exercise, reason }) => <article className="panel recommendation-card" key={exercise.id}>
      <div className="exercise-card-top"><span className="category-chip">{exercise.category}</span><span className="muted small">{exercise.duration} min</span></div>
      <h3>{exercise.name}</h3><p>{exercise.description}</p><p className="recommendation-reason"><Sparkles size={14} /> {reason}</p>
      <button className="primary" onClick={() => onNavigate('Workouts')}>Start workout</button>
    </article>)}</div>
    {!items.length && !error && <div className="panel empty-state">The exercise library is empty. Recommendations will appear when exercises are available.</div>}
    <p className="muted small">Recommendations are rule-based fitness suggestions, not medical advice.</p>
  </div>
}

export function ReminderSettingsPage({ refresh }: { refresh: number }) {
  const [settings, setSettings] = useState<UserPreferences | null>(null)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => {
    api.get<UserPreferences>('/settings/reminders')
      .then(response => { setSettings(response.data); setError('') })
      .catch((e: any) => setError(e?.response?.data?.detail || 'Could not load reminder settings.'))
  }, [refresh])
  function update<K extends keyof UserPreferences>(key: K, value: UserPreferences[K]) {
    setSettings(previous => previous ? { ...previous, [key]: value } : previous)
  }
  async function save(event: FormEvent) {
    event.preventDefault()
    if (!settings) return
    try {
      const response = await api.patch<UserPreferences>('/settings/reminders', settings)
      setSettings(response.data)
      setSaved(true)
      setError('')
    } catch (e: any) {
      setSaved(false)
      setError(e?.response?.data?.detail || 'Could not save reminder settings.')
    }
  }
  if (!settings) return <div className="panel">{error || 'Loading reminder settings…'}</div>
  const reminders = [
    { label: 'Workout', enabled: 'workout_reminder_enabled', time: 'workout_reminder_time', description: 'Remind me to log a workout.' },
    { label: 'Meals', enabled: 'meal_reminder_enabled', time: 'meal_reminder_time', description: 'Remind me to track my meals.' },
    { label: 'Water', enabled: 'water_reminder_enabled', time: 'water_reminder_time', description: 'Remind me to stay hydrated.' },
  ] as const
  return <div className="page-stack">
    <div className="section-heading"><div><h2>Reminders & goals</h2><p className="muted">Choose daily in-app reminders and your hydration target.</p></div><Bell /></div>
    <form className="panel form-panel reminder-settings" onSubmit={save}>
      {reminders.map(reminder => <div className="reminder-setting" key={reminder.label}>
        <label className="reminder-toggle"><input type="checkbox" checked={settings[reminder.enabled]} onChange={event => update(reminder.enabled, event.target.checked)} /><span><strong>{reminder.label}</strong><small>{reminder.description}</small></span></label>
        <label>Time<input type="time" value={settings[reminder.time]} onChange={event => update(reminder.time, event.target.value)} disabled={!settings[reminder.enabled]} /></label>
      </div>)}
      <label>Time zone<input required maxLength={80} value={settings.timezone} onChange={event => update('timezone', event.target.value)} placeholder="e.g. America/New_York" /><small className="muted">Use an IANA zone such as Asia/Kolkata or America/Los_Angeles.</small></label>
      <label>Daily water goal (ml)<input type="number" min="250" max="10000" value={settings.water_goal_ml} onChange={event => update('water_goal_ml', Number(event.target.value))} /></label>
      {error && <p className="error">{error}</p>}
      {saved && <p className="success-text">Settings saved.</p>}
      <button className="primary full">Save settings</button>
    </form>
  </div>
}
