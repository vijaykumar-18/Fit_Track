export type User = { id: number; username: string; email: string; created_at: string }

export type Workout = {
  id: number
  user_id: number
  workout_name: string
  category: 'Cardio' | 'Strength' | 'Yoga'
  duration: number
  calories_burned: number
  workout_date: string
  created_at: string
}

export type Goal = {
  id: number
  user_id: number
  goal_type: 'Weight Loss' | 'Muscle Gain' | 'Steps'
  target_value: number
  current_value: number
  deadline: string | null
  status: string
  created_at: string
}

export type Notification = {
  id: number
  title: string
  message: string
  is_read: boolean
  created_at: string
}

export type WorkoutPlan = {
  id: number
  user_id: number
  title: string
  description: string
  scheduled_date: string
  created_at: string
}

export type Exercise = {
  id: number
  name: string
  category: 'Cardio' | 'Strength' | 'Yoga'
  description: string
  duration: number
}

export type Streak = {
  current_streak: number
  longest_streak: number
  last_workout_date: string | null
}

export type Badge = {
  id: number
  name: string
  description: string
  icon: string
  category: string
}

export type ProgressSummary = {
  date: string
  total_workouts: number
  total_calories: number
  total_duration: number
}
