'use client'
import { motion } from 'framer-motion'

interface RatioInfo {
  width: number
  height: number
  label: string
}

interface Props {
  ratios: Record<string, RatioInfo>
  selected: string
  onSelect: (ratio: string) => void
}

const RATIO_SHAPES: Record<string, { w: number; h: number; icon: string }> = {
  '16:9': { w: 48, h: 27, icon: '⬛' },
  '1:1':  { w: 36, h: 36, icon: '⬜' },
  '9:16': { w: 27, h: 48, icon: '▮'  },
}

export default function AspectRatioGrid({ ratios, selected, onSelect }: Props) {
  return (
    <div className="grid grid-cols-3 gap-2">
      {Object.entries(ratios).map(([ratio, info]) => {
        const shape = RATIO_SHAPES[ratio]
        const isSelected = selected === ratio

        return (
          <motion.button
            key={ratio}
            onClick={() => onSelect(ratio)}
            whileHover={{ scale: 1.04, y: -2 }}
            whileTap={{ scale: 0.97 }}
            transition={{ type: 'spring', stiffness: 400, damping: 25 }}
            className={`
              relative flex flex-col items-center justify-center gap-2 p-3 rounded-xl border
              transition-all duration-200 aspect-square
              ${isSelected
                ? 'border-violet-500/60 bg-violet-950/40 shadow-[0_0_20px_rgba(139,92,246,0.15)]'
                : 'border-white/5 bg-white/[0.02] hover:border-white/10 hover:bg-white/[0.04]'
              }
            `}
          >
            {/* Visual shape representation */}
            <div className="flex items-center justify-center flex-1">
              <motion.div
                animate={isSelected ? { borderColor: 'rgba(167,139,250,0.7)' } : {}}
                style={{
                  width:  shape ? `${shape.w * 0.7}px` : '28px',
                  height: shape ? `${shape.h * 0.7}px` : '28px',
                  minWidth: '14px',
                  minHeight: '14px',
                }}
                className={`
                  rounded-sm border-2 transition-all duration-200
                  ${isSelected
                    ? 'border-violet-400 bg-violet-500/20'
                    : 'border-slate-600 bg-white/[0.03]'
                  }
                `}
              />
            </div>

            {/* Ratio label */}
            <div className="text-center">
              <p className={`text-xs font-bold ${isSelected ? 'text-violet-300' : 'text-slate-400'}`}>
                {ratio}
              </p>
              <p className="text-[10px] text-slate-600 mt-0.5">
                {info.width}×{info.height}
              </p>
            </div>

            {isSelected && (
              <motion.div
                layoutId="ratio-indicator"
                className="absolute inset-0 rounded-xl ring-1 ring-violet-500/40"
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
            )}
          </motion.button>
        )
      })}
    </div>
  )
}