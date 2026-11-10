import type { ReactNode } from 'react'

export function StatCard({
  icon,
  label,
  value,
  unit,
  color,
}: {
  icon: ReactNode
  label: string
  value: string | number
  unit: string
  color: string
}) {
  return <div className="stat-card">
    <div className={`stat-icon ${color}`}>{icon}</div>
    <p>{label}</p>
    <div className="stat-value">{value}<span>{unit}</span></div>
  </div>
}

export function EmptyState({ text }: { text: string }) {
  return <div className="empty-state">{text}</div>
}
