// Shared priority/status badge constants and components

export const PRIORITY_STYLES = {
  'A+': 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  'A':  'bg-blue-500/20 text-blue-300 border-blue-500/30',
  'B':  'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  'C':  'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

export const STATUS_STYLES = {
  new:        'bg-gray-500/20 text-gray-300',
  researching:'bg-blue-500/20 text-blue-300',
  qualified:  'bg-indigo-500/20 text-indigo-300',
  contacted:  'bg-purple-500/20 text-purple-300',
  replied:    'bg-violet-500/20 text-violet-300',
  meeting:    'bg-amber-500/20 text-amber-300',
  proposal:   'bg-orange-500/20 text-orange-300',
  won:        'bg-green-500/20 text-green-300',
  lost:       'bg-red-500/20 text-red-300',
  archived:   'bg-gray-700/40 text-gray-500',
}

export function PriorityBadge({ priority, className = '' }) {
  const style = PRIORITY_STYLES[priority] || PRIORITY_STYLES['C']
  return (
    <span className={`inline-flex items-center px-2.5 py-1 text-sm font-semibold rounded-lg border ${style} ${className}`}>
      {priority}
    </span>
  )
}

export function StatusBadge({ status, className = '' }) {
  const style = STATUS_STYLES[status] || STATUS_STYLES.new
  return (
    <span className={`inline-flex items-center px-2.5 py-1 text-sm rounded-lg capitalize font-medium ${style} ${className}`}>
      {status}
    </span>
  )
}

export function SourceBadge({ source, className = '' }) {
  const colors = {
    linkedin: 'bg-blue-900/30 text-blue-300',
    artstation: 'bg-indigo-900/30 text-indigo-300',
    wamda: 'bg-emerald-900/30 text-emerald-300',
    upwork: 'bg-green-900/30 text-green-300',
    manual: 'bg-gray-800 text-gray-400',
  }
  const style = colors[source?.toLowerCase()] || 'bg-gray-800 text-gray-400'
  return (
    <span className={`inline-flex items-center px-2.5 py-1 text-sm rounded-lg capitalize font-medium ${style} ${className}`}>
      {source}
    </span>
  )
}
