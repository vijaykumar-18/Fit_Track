import axios from 'axios'
import type { Badge, Exercise, Goal, Meal, Notification, ProgressSummary, Streak, User, UserPreferences, WaterSummary, Workout, WorkoutPlan, WorkoutRecommendation } from '../types'

export type { Badge, Exercise, Goal, Meal, Notification, ProgressSummary, Streak, User, UserPreferences, WaterSummary, Workout, WorkoutPlan, WorkoutRecommendation } from '../types'

const apiOrigin = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')
export const api = axios.create({ baseURL: `${apiOrigin}/api` })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('fittrack_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
