'use client'
import { motion } from 'framer-motion'
import { Sparkles, Minus } from 'lucide-react'
import { RefObject } from 'react'

interface Props {
  prompt: string
  negativePrompt: string
  maxChars: number
  onPromptChange: (val: string) => void
  onNegativeChange: (val: string) => void
  onGenerate: () => void
  isGenerating: boolean
  textareaRef?: RefObject<HTMLTextAreaElement>
}

export default function PromptWorkspace({
  prompt, negativePrompt, maxChars,
  onPromptChange, onNegativeChange,
  onGenerate, isGenerating, textareaRef
}: Props) {
  const charCount = prompt.length
  const isOverLimit = charCount > maxChars
  const charPct = Math.min((charCount / maxChars) * 100, 100)

  return (
    <div className="space-y-3">
      <div className={`
        relative rounded-xl border transition-all duration-300
        ${isOverLimit
          ? 'border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.1)]'
          : 'border-white/5 focus-within:border-violet-500/40 focus-within:shadow-[0_0_20px_rgba(139,92,246,0.1)]'
        }
        bg-white/[0.02]
      `}>
        <div className="flex items-start gap-2 px-4 pt-4 pb-1">
          <Sparkles className="w-4 h-4 text-violet-400 mt-0.5 shrink-0" />
          <span className="text-xs font-semibold text-violet-400 uppercase tracking-wider">Prompt</span>
          <span className="ml-auto text-[10px] text-slate-700 hidden lg:inline">⌘ Enter to generate</span>
        </div>
        <textarea
          ref={textareaRef}
          value={prompt}
          onChange={e => onPromptChange(e.target.value)}
          placeholder="Describe your vision in rich detail — lighting, mood, style, composition..."
          rows={5}
          className="w-full bg-transparent px-4 pb-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none resize-none leading-relaxed"
        />
        <div className="flex items-center justify-between px-4 pb-3 border-t border-white/5 pt-2">
          <div className="flex items-center gap-2 flex-1 mr-4">
            <div className="flex-1 h-1 rounded-full bg-white/5 overflow-hidden">
              <motion.div
                className={`h-full rounded-full transition-colors duration-300 ${
                  isOverLimit ? 'bg-red-500' : charPct > 80 ? 'bg-amber-500' : 'bg-violet-500'
                }`}
                animate={{ width: `${charPct}%` }} transition={{ duration: 0.3 }}
              />
            </div>
          </div>
          <span className={`text-xs font-mono tabular-nums ${isOverLimit ? 'text-red-400' : 'text-slate-600'}`}>
            {charCount.toLocaleString()} / {maxChars.toLocaleString()}
          </span>
        </div>
      </div>

      <div className="relative rounded-xl border border-white/5 bg-white/[0.02] focus-within:border-red-500/20 transition-all duration-300">
        <div className="flex items-center gap-2 px-4 pt-3 pb-1">
          <Minus className="w-4 h-4 text-red-400/70 shrink-0" />
          <span className="text-xs font-semibold text-red-400/70 uppercase tracking-wider">Negative Prompt</span>
          <span className="text-xs text-slate-700">(optional · HF only)</span>
        </div>
        <textarea
          value={negativePrompt}
          onChange={e => onNegativeChange(e.target.value)}
          placeholder="blur, low quality, watermark, text, artifacts..."
          rows={2}
          className="w-full bg-transparent px-4 pb-3 text-sm text-slate-400 placeholder-slate-700 focus:outline-none resize-none leading-relaxed"
        />
      </div>

      <motion.button
        onClick={onGenerate}
        disabled={isGenerating || !prompt.trim() || isOverLimit}
        whileHover={!isGenerating && prompt.trim() ? { scale: 1.01, y: -1 } : {}}
        whileTap={!isGenerating ? { scale: 0.99 } : {}}
        className={`
          w-full py-4 rounded-xl font-bold text-base relative overflow-hidden transition-all duration-300
          ${isGenerating || !prompt.trim() || isOverLimit
            ? 'bg-white/5 text-slate-600 cursor-not-allowed border border-white/5'
            : 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-[0_4px_20px_rgba(139,92,246,0.35)] hover:shadow-[0_4px_30px_rgba(139,92,246,0.5)]'
          }
        `}
      >
        {isGenerating ? (
          <span className="flex items-center justify-center gap-3">
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              className="w-4 h-4 border-2 border-slate-500 border-t-slate-300 rounded-full" />
            <span>Generating...</span>
          </span>
        ) : (
          <span className="flex items-center justify-center gap-2">
            <Sparkles className="w-5 h-5" /> Generate Image
          </span>
        )}
      </motion.button>
    </div>
  )
}