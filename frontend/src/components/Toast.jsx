import { CheckCircle2, XCircle, AlertTriangle, Info, X } from 'lucide-react'

const TYPE_STYLES = {
  success: {
    container: 'bg-gray-900 border border-green-500/30 text-green-400',
    icon: CheckCircle2,
  },
  error: {
    container: 'bg-gray-900 border border-red-500/30 text-red-400',
    icon: XCircle,
  },
  warning: {
    container: 'bg-gray-900 border border-amber-500/30 text-amber-400',
    icon: AlertTriangle,
  },
  info: {
    container: 'bg-gray-900 border border-indigo-500/30 text-indigo-400',
    icon: Info,
  },
}

function Toast({ toast, onRemove }) {
  const { container, icon: Icon } = TYPE_STYLES[toast.type] || TYPE_STYLES.info

  return (
    <div
      className={`pointer-events-auto flex items-start gap-3 rounded-xl px-4 py-3 shadow-lg transition-all duration-300 ${container}`}
    >
      <Icon className="w-4 h-4 mt-0.5 flex-shrink-0" />
      <p className="flex-1 text-sm leading-snug">{toast.message}</p>
      <button
        onClick={() => onRemove(toast.id)}
        className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity"
        aria-label="Dismiss"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

export function ToastContainer({ toasts, onRemove }) {
  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((t) => (
        <Toast key={t.id} toast={t} onRemove={onRemove} />
      ))}
    </div>
  )
}

export function ConfirmDialog({
  message,
  onConfirm,
  onCancel,
  confirmLabel = 'Delete',
  confirmClass = 'bg-red-600 hover:bg-red-700',
}) {
  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 max-w-sm w-full shadow-2xl">
        <p className="text-gray-200 mb-6">{message}</p>
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-sm rounded-lg text-white transition-colors ${confirmClass}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
