'use client'
import { motion } from 'framer-motion'
import { Cpu, Zap } from 'lucide-react'

interface Engine {
  name: string
  max_chars: number
  description: string
}

interface Props {
  engines: Record<string, Engine>
  selected: string
  onSelect: (key: string) => void
}

const ENGINE_ICONS: Record<string, React.ReactNode> = {
  huggingface: <Cpu className="w-4 h-4" />,
  pollinations: <Zap className="w-4 h-4" />,
}

const ENGINE_BADGES: Record<string, string> = {
  huggingface: 'RAW Bytes',
  pollinations: 'Free · No Key',
}

export default function EngineSelector({ engines, selected, onSelect }: Props) {
  return (
    <div className="space-y-2">
      {Object.entries(engines).map(([key, engine]) => {
        const isActive = selected === key
        return (
          <motion.button
            key={key}
            onClick={() => onSelect(key)}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className={`
              w-full text-left p-4 rounded-xl border transition-all duration-200 relative overflow-hidden
              ${isActive
                ? 'border-violet-500/50 bg-violet-950/30'
                : 'border-white/5 bg-white/[0.02] hover:border-white/10 hover:bg-white/[0.04]'
              }
            `}
          >
            {isActive && (
              <motion.div
                layoutId="engine-glow"
                className="absolute inset-0 bg-gradient-to-r from-violet-600/10 to-indigo-600/10 rounded-xl"
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
            )}
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className={isActive ? 'text-violet-400' : 'text-slate-500'}>
                    {ENGINE_ICONS[key]}
                  </span>
                  <span className={`text-sm font-semibold ${isActive ? 'text-white' : 'text-slate-300'}`}>
                    {engine.name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-slate-500 border border-white/5">
                    {ENGINE_BADGES[key]}
                  </span>
                  {isActive && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-2 h-2 rounded-full bg-violet-400 shadow-[0_0_8px_rgba(167,139,250,0.8)]"
                    />
                  )}
                </div>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">{engine.description}</p>
              <div className="mt-2 flex items-center gap-1.5">
                <div className="flex-1 h-1 rounded-full bg-white/5 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-violet-500 to-indigo-500"
                    style={{ width: `${Math.min((engine.max_chars / 10000) * 100, 100)}%` }}
                  />
                </div>
                <span className="text-xs text-slate-600">
                  {engine.max_chars.toLocaleString()} chars
                </span>
              </div>
            </div>
          </motion.button>
        )
      })}
    </div>
  )
}