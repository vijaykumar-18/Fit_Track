import { api } from './api'
import type { User } from '../types'

export async function register(credentials: { username: string; email: string; password: string }): Promise<User> {
  const response = await api.post<User>('/auth/register', credentials)
  return response.data
}

export async function login(identifier: string, password: string): Promise<{ access_token: string; user: User }> {
  const form = new URLSearchParams({ username: identifier, password })
  const response = await api.post<{ access_token: string; user: User }>('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  localStorage.setItem('fittrack_token', response.data.access_token)
  return response.data
}

export function logout(): void {
  localStorage.removeItem('fittrack_token')
}
