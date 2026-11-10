import { useEffect, useState } from 'react'

import { api } from '../services/api'
import type { Goal, Notification, ProgressSummary, Workout } from '../types'
import { localDateString } from '../utils/date'

export function useFitnessData(refresh: number) {
  const [workouts, setWorkouts] = useState<Workout[]>([])
  const [goals, setGoals] = useState<Goal[]>([])
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [summary, setSummary] = useState<ProgressSummary | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    Promise.all([
      api.get<Workout[]>('/workouts'),
      api.get<Goal[]>('/goals'),
      api.get<Notification[]>('/notifications'),
      api.get<ProgressSummary>('/progress/daily', { params: { on_date: localDateString() } }),
    ]).then(([workoutResponse, goalResponse, notificationResponse, summaryResponse]) => {
      if (!active) return
      setWorkouts(workoutResponse.data)
      setGoals(goalResponse.data)
      setNotifications(notificationResponse.data)
      setSummary(summaryResponse.data)
      setError('')
    }).catch((error: any) => {
      if (active) setError(error?.response?.data?.detail || 'Could not load fitness data.')
    })

    return () => { active = false }
  }, [refresh])

  return { workouts, goals, notifications, summary, error }
}
