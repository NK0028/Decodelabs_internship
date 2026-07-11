'use client'
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, CheckCircle, X, RefreshCw } from 'lucide-react'

interface ToastProps {
  message: string
  type: 'error' | 'success' | 'warning'
  onClose: () => void
  onRetry?: () => void
  autoRetrySeconds?: number
}

export default function Toast({ message, type, onClose, onRetry, autoRetrySeconds }: ToastProps) {
  const [countdown, setCountdown] = useState(autoRetrySeconds ?? 0)

  useEffect(() => {
    if (!autoRetrySeconds || !onRetry) return
    if (countdown <= 0) {
      onRetry()
      return
    }
    const t = setTimeout(() => setCountdown(c => c - 1), 1000)
    return () => clearTimeout(t)
  }, [countdown, autoRetrySeconds, onRetry])

  const colors = {
    error:   'border-red-500/30 bg-red-950/40',
    success: 'border-emerald-500/30 bg-emerald-950/40',
    warning: 'border-amber-500/30 bg-amber-950/40',
  }
  const icons = {
    error:   <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />,
    success: <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />,
    warning: <AlertCircle className="w-5 h-5 text-amber-400 shrink-0" />,
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 40, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className={`flex items-start gap-3 p-4 rounded-2xl border backdrop-blur-xl shadow-2xl max-w-md ${colors[type]}`}
    >
      {icons[type]}
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-200 leading-relaxed">{message}</p>

        {autoRetrySeconds && onRetry && countdown > 0 && (
          <p className="text-xs text-slate-500 mt-1">
            Retrying automatically in {countdown}s...
          </p>
        )}

        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium"
          >
            <RefreshCw className="w-3 h-3" /> Retry now
          </button>
        )}
      </div>
      <button onClick={onClose} className="text-slate-500 hover:text-slate-300 transition-colors shrink-0">
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  )
}