'use client'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import { Download, Share2, RefreshCw, ImageIcon } from 'lucide-react'

interface GeneratedImage {
  image_b64: string
  save_path: string
  width: number
  height: number
  engine: string
  aspect_ratio: string
  prompt: string
  style_preset: string
  file_size_kb: number
}

interface Props {
  phase: 'idle' | 'processing' | 'output' | 'error'
  image: GeneratedImage | null
  onDownload: (filename: string) => void
  onRetry: () => void
  engine: string
}

// ------------------------------------------------------------
// STAGED LOADING SEQUENCE
// Cycles through realistic pipeline status text for perceived speed
// ------------------------------------------------------------
const STAGE_SEQUENCES: Record<string, string[]> = {
  huggingface: [
    'Initializing GPU cluster...',
    'Encoding semantic prompt vector...',
    'Establishing split-timeout connection...',
    'Running reverse-Markov denoising matrix...',
    'Upscaling generated asset...',
    'Verifying binary stream integrity...',
  ],
  pollinations: [
    'Serializing multimodal payload...',
    'Routing to Pollinations generation engine...',
    'Rendering diffusion output...',
    'Streaming image asset...',
    'Verifying binary integrity...',
  ],
}

function useStagedLoading(active: boolean, engine: string) {
  const [stageIndex, setStageIndex] = useState(0)
  const stages = STAGE_SEQUENCES[engine] || STAGE_SEQUENCES.pollinations

  useEffect(() => {
    if (!active) {
      setStageIndex(0)
      return
    }
    const interval = setInterval(() => {
      setStageIndex(prev => Math.min(prev + 1, stages.length - 1))
    }, 1600)
    return () => clearInterval(interval)
  }, [active, stages.length])

  return stages[stageIndex]
}

function DenoiseAnimation({ engine }: { engine: string }) {
  const statusText = useStagedLoading(true, engine)

  return (
    <div className="relative w-full aspect-square max-w-sm mx-auto">
      {[...Array(5)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute inset-0 rounded-2xl"
          style={{
            background: `radial-gradient(circle at ${20 + i * 15}% ${30 + i * 10}%, 
              rgba(139,92,246,${0.15 - i * 0.02}) 0%, 
              rgba(99,102,241,${0.1 - i * 0.015}) 40%, 
              transparent 70%)`
          }}
          animate={{ opacity: [0.4, 1, 0.4], scale: [0.98, 1.02, 0.98] }}
          transition={{ duration: 2 + i * 0.5, repeat: Infinity, delay: i * 0.3, ease: 'easeInOut' }}
        />
      ))}

      <div
        className="absolute inset-0 rounded-2xl opacity-10"
        style={{
          backgroundImage: `
            linear-gradient(rgba(139,92,246,0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(139,92,246,0.3) 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px',
        }}
      />

      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-violet-400"
          style={{ left: `${10 + (i * 7) % 80}%`, top: `${15 + (i * 11) % 70}%` }}
          animate={{ opacity: [0, 1, 0], scale: [0, 1.5, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
        />
      ))}

      {/* Staged status text — the key upgrade */}
      <div className="absolute inset-0 flex flex-col items-center justify-center px-6">
        <div className="text-violet-400 text-4xl mb-4">
          <motion.span
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            className="inline-block"
          >
            ◈
          </motion.span>
        </div>
        <AnimatePresence mode="wait">
          <motion.p
            key={statusText}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.35 }}
            className="text-xs text-slate-400 font-mono text-center leading-relaxed"
          >
            {statusText}
          </motion.p>
        </AnimatePresence>
      </div>
    </div>
  )
}

export default function GenerationCanvas({
  phase, image, onDownload, onRetry, engine
}: Props) {
  const getFilename = (path: string) => path.split('/').pop() || path

  return (
    <div className="w-full h-full flex flex-col">
      <AnimatePresence mode="wait">

        {phase === 'idle' && (
          <motion.div
            key="idle"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="flex-1 flex flex-col items-center justify-center text-center p-12"
          >
            <motion.div
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
              className="w-20 h-20 rounded-2xl bg-white/[0.03] border border-white/5 flex items-center justify-center mb-6"
            >
              <ImageIcon className="w-8 h-8 text-slate-700" />
            </motion.div>
            <h3 className="text-lg font-semibold text-slate-600 mb-2">Canvas Ready</h3>
            <p className="text-sm text-slate-700 max-w-xs leading-relaxed">
              Configure your parameters, write a detailed prompt, and press{' '}
              <kbd className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-slate-500 text-xs">⌘ Enter</kbd>{' '}
              to generate.
            </p>
          </motion.div>
        )}

        {phase === 'processing' && (
          <motion.div
            key="processing"
            initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.98 }}
            className="flex-1 flex flex-col items-center justify-center p-8"
          >
            <DenoiseAnimation engine={engine} />
            <p className="text-xs text-slate-700 mt-6 font-mono">
              timeout: 3.05s connect / 120s read
            </p>
          </motion.div>
        )}

        {phase === 'output' && image && (
          <motion.div
            key="output"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}
            className="flex-1 flex flex-col"
          >
            <div className="relative group rounded-2xl overflow-hidden bg-black/20 border border-white/5">
              <motion.img
                initial={{ opacity: 0, scale: 1.02 }} animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
                src={`data:image/png;base64,${image.image_b64}`}
                alt={image.prompt}
                className="w-full object-contain"
              />
              <motion.div
                initial={{ opacity: 0, y: 10 }} whileHover={{ opacity: 1, y: 0 }}
                className="absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-black/80 via-black/40 to-transparent
                           opacity-0 group-hover:opacity-100 transition-opacity duration-300"
              >
                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => onDownload(getFilename(image.save_path))}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 backdrop-blur-sm border border-white/10 text-white text-xs font-medium hover:bg-white/20 transition-all"
                  >
                    <Download className="w-3.5 h-3.5" /> Download Raw Asset
                  </button>
                  <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 backdrop-blur-sm border border-white/10 text-white text-xs font-medium hover:bg-white/20 transition-all">
                    <Share2 className="w-3.5 h-3.5" /> Share
                  </button>
                </div>
              </motion.div>
              <div className="absolute top-3 right-3">
                <span className="text-xs px-2 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/30 text-emerald-400 backdrop-blur-sm font-medium">
                  ✓ Verified
                </span>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-2 mt-4">
              {[
                ['Engine', image.engine],
                ['Resolution', `${image.width}×${image.height}`],
                ['Ratio', image.aspect_ratio],
                ['Size', `${image.file_size_kb} KB`],
              ].map(([label, value]) => (
                <div key={label} className="rounded-xl bg-white/[0.02] border border-white/5 p-3 text-center">
                  <p className="text-xs text-slate-600 mb-1">{label}</p>
                  <p className="text-xs font-semibold text-slate-300 truncate">{value}</p>
                </div>
              ))}
            </div>

            <div className="mt-3 rounded-xl bg-white/[0.02] border border-white/5 p-4">
              <p className="text-xs text-slate-600 mb-1 uppercase tracking-wider font-medium">Prompt</p>
              <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">{image.prompt}</p>
            </div>

            <button
              onClick={onRetry}
              className="mt-3 flex items-center justify-center gap-2 w-full py-3 rounded-xl border border-white/5 text-slate-500 hover:text-slate-300 hover:border-white/10 text-sm transition-all"
            >
              <RefreshCw className="w-4 h-4" /> Generate Another
            </button>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  )
}