export function Card({ children, className = '' }) {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}>
      {children}
    </div>
  )
}

export function CardHeader({ children }) {
  return <div className="border-b border-slate-100 px-6 py-4">{children}</div>
}

export function CardTitle({ children, icon: Icon }) {
  return (
    <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900">
      {Icon && <Icon className="h-5 w-5 text-indigo-600" />}
      {children}
    </h2>
  )
}

export function CardDescription({ children }) {
  return <p className="mt-1 text-sm text-slate-500">{children}</p>
}

export function CardContent({ children, className = '' }) {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>
}

export function Button({ children, onClick, disabled, variant = 'primary' }) {
  const styles =
    variant === 'outline'
      ? 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
      : 'bg-indigo-600 text-white hover:bg-indigo-700'
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg px-4 py-2 text-sm font-medium transition disabled:opacity-50 ${styles}`}
    >
      {children}
    </button>
  )
}

export function Badge({ children, tone = 'default', title }) {
  const tones = {
    default: 'bg-slate-100 text-slate-700',
    success: 'bg-emerald-100 text-emerald-800',
    warning: 'bg-amber-100 text-amber-800',
    danger: 'bg-red-100 text-red-800',
    info: 'bg-indigo-100 text-indigo-800',
  }
  return (
    <span
      title={title}
      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${tones[tone] || tones.default}`}
    >
      {children}
    </span>
  )
}
