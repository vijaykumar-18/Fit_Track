import axios from 'axios'

export const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api' })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('fittrack_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export type User = { id: number; username: string; email: string; created_at: string }
export type Workout = {
  id: number; user_id: number; workout_name: string; category: 'Cardio' | 'Strength' | 'Yoga'
  duration: number; calories_burned: number; workout_date: string; created_at: string
}
export type Goal = {
  id: number; user_id: number; goal_type: 'Weight Loss' | 'Muscle Gain' | 'Steps'
  target_value: number; current_value: number; deadline: string | null; status: string; created_at: string
}
export type Notification = { id: number; title: string; message: string; is_read: boolean; created_at: string }
