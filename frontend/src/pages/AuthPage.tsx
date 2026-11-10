import { FormEvent, useState } from 'react'
import { Link } from 'react-router-dom'
import { Activity } from 'lucide-react'

import { login, register } from '../services/authService'
import type { User } from '../types'

export function AuthPage({ mode, onAuth }: { mode: 'login' | 'register'; onAuth: (user: User) => void }) {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const isRegister = mode === 'register'

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      if (isRegister) {
        await register({ username, email, password })
        onAuth({ id: 0, username, email, created_at: new Date().toISOString() })
      } else {
        const response = await login(username || email, password)
        onAuth(response.user)
      }
    } catch (requestError: any) {
      setError(requestError?.response?.data?.detail || 'Unable to complete request. Is the backend running?')
    } finally {
      setBusy(false)
    }
  }

  return <div className="auth-wrap">
    <div className="auth-brand"><div className="brand-mark"><Activity /></div><span>FitTrack</span></div>
    <form className="auth-card" onSubmit={submit}>
      <p className="eyebrow">YOUR FITNESS, IN FOCUS</p>
      <h1>{isRegister ? 'Create your account' : 'Welcome back'}</h1>
      <p className="muted">{isRegister ? 'Start building a routine that works for you.' : 'Sign in to continue your fitness journey.'}</p>
      {isRegister && <label>Username<input required minLength={3} value={username} onChange={event => setUsername(event.target.value)} placeholder="e.g. fit_vijay" /></label>}
      {!isRegister && <label>Username or email<input required value={username} onChange={event => setUsername(event.target.value)} placeholder="Enter username or email" /></label>}
      {isRegister && <label>Email address<input required type="email" value={email} onChange={event => setEmail(event.target.value)} placeholder="you@example.com" /></label>}
      <label>Password<input required type="password" minLength={8} value={password} onChange={event => setPassword(event.target.value)} placeholder="At least 8 characters" /></label>
      {error && <div className="error">{error}</div>}
      <button className="primary full" disabled={busy}>{busy ? 'Please wait…' : isRegister ? 'Create account' : 'Sign in'}</button>
      <p className="auth-switch">{isRegister ? 'Already have an account?' : "Don't have an account?"} <Link to={isRegister ? '/login' : '/register'}>{isRegister ? 'Sign in' : 'Register'}</Link></p>
    </form>
    <p className="auth-foot">Small steps. Strong habits. Real progress.</p>
  </div>
}
