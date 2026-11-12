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

export type Meal = {
  id: number
  user_id: number
  meal_type: 'Breakfast' | 'Lunch' | 'Dinner' | 'Snacks'
  food_name: string
  calories: number
  protein: number
  carbs: number
  fats: number
  meal_date: string
  created_at: string
}

export type NutritionSummary = {
  date: string
  calories: number
  protein: number
  carbs: number
  fats: number
}

export type WaterEntry = {
  id: number
  user_id: number
  quantity: number
  date: string
  created_at: string
}

export type WaterSummary = {
  date: string
  total_ml: number
  goal_ml: number
  progress_percent: number
  entries: WaterEntry[]
}

export type UserPreferences = {
  timezone: string
  water_goal_ml: number
  workout_reminder_enabled: boolean
  workout_reminder_time: string
  meal_reminder_enabled: boolean
  meal_reminder_time: string
  water_reminder_enabled: boolean
  water_reminder_time: string
}

export type WorkoutRecommendation = {
  exercise: Exercise
  reason: string
}
