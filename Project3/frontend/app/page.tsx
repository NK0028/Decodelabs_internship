'use client'

import { useState, useEffect, useRef } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import axios from 'axios'
import { Settings2, Palette, Layers, X, SlidersHorizontal, Sparkles } from 'lucide-react'

import EngineSelector   from './components/EngineSelector'
import AspectRatioGrid  from './components/AspectRatioGrid'
import PromptWorkspace  from './components/PromptWorkspace'
import GenerationCanvas from './components/GenerationCanvas'
import Toast            from './components/Toast'
import { useKeybinds }  from './hooks/useKeybinds'

const API_BASE = 'http://localhost:8000'

interface Config {
  aspect_ratios: Record<string, { width: number; height: number; label: string }>
  engines: Record<string, { name: string; max_chars: number; description: string }>
  style_presets: string[]
}
interface GeneratedImage {
  image_b64: string; save_path: string; width: number; height: number
  engine: string; aspect_ratio: string; prompt: string; style_preset: string; file_size_kb: number
}
type Phase = 'idle' | 'processing' | 'output' | 'error'
interface ToastState { message: string; type: 'error' | 'success' | 'warning'; autoRetrySeconds?: number }

export default function Home() {
  const [config, setConfig]           = useState<Config | null>(null)
  const [configError, setConfigError] = useState(false)
  const [prompt, setPrompt]           = useState('')
  const [negativePrompt, setNegativePrompt] = useState('')
  const [selectedEngine, setSelectedEngine] = useState('pollinations')
  const [selectedRatio, setSelectedRatio]   = useState('1:1')
  const [selectedStyle, setSelectedStyle]   = useState('None')
  const [phase, setPhase]             = useState<Phase>('idle')
  const [generatedImage, setGeneratedImage] = useState<GeneratedImage | null>(null)
  const [toast, setToast]             = useState<ToastState | null>(null)

  // Mobile drawer states
  const [showConfigDrawer, setShowConfigDrawer] = useState(false)
  const [showPromptDrawer, setShowPromptDrawer] = useState(false)

  const promptRef = useRef<HTMLTextAreaElement>(null)
  const generateBtnRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    axios.get(`${API_BASE}/config`)
      .then(res => setConfig(res.data))
      .catch(() => setConfigError(true))
  }, [])

  const showToast = (message: string, type: ToastState['type'], autoRetrySeconds?: number) => {
    setToast({ message, type, autoRetrySeconds })
    if (type !== 'error') setTimeout(() => setToast(null), 4000)
  }

  const handleGenerate = async () => {
    if (!prompt.trim() || phase === 'processing') return
    setPhase('processing')
    setGeneratedImage(null)
    setToast(null)
    setShowConfigDrawer(false)
    setShowPromptDrawer(false)

    try {
      const res = await axios.post(`${API_BASE}/generate`, {
        prompt,
        engine: selectedEngine,
        aspect_ratio: selectedRatio,
        negative_prompt: negativePrompt || null,
        style_preset: selectedStyle,
        num_images: 1,
      })
      setGeneratedImage(res.data)
      setPhase('output')
      showToast('Image generated and integrity verified ✓', 'success')
      // Keep focus flow — return focus to prompt for next generation
      setTimeout(() => promptRef.current?.focus(), 300)
    } catch (err: any) {
      setPhase('idle') // graceful degradation — parameters intact, canvas returns to ready
      const rawDetail = err?.response?.data?.detail
      const detail = typeof rawDetail === 'string'
        ? rawDetail
        : Array.isArray(rawDetail)
        ? rawDetail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
        : rawDetail?.msg || err.message || 'Unknown error occurred'

      if (detail.includes('ConnectTimeout') || detail.includes('connect')) {
        showToast('Connection failed. Check your network or firewall settings.', 'error')
      } else if (detail.includes('ReadTimeout') || detail.includes('503') || detail.includes('loading')) {
        showToast('GPU clusters are heavily loaded. Retrying automatically...', 'warning', 4)
      } else if (detail.includes('policy') || detail.includes('403')) {
        showToast('Content policy violation detected. Please revise your prompt.', 'warning')
      } else {
        showToast(detail, 'error')
      }
    }
  }

  // --------------------------------------------------------
  // KEYBOARD-FIRST CONTROL
  // Cmd/Ctrl + Enter → Generate
  // Escape → close mobile drawers
  // --------------------------------------------------------
  useKeybinds([
    { key: 'Enter', metaOrCtrl: true, handler: handleGenerate },
    { key: 'Escape', metaOrCtrl: false, handler: () => {
        setShowConfigDrawer(false)
        setShowPromptDrawer(false)
      }
    },
  ])

  const handleDownload = (filename: string) => {
    window.open(`${API_BASE}/download/${filename}`, '_blank')
  }

  const maxChars = config?.engines[selectedEngine]?.max_chars ?? 1000

  if (configError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#09090b] p-6">
        <div className="text-center p-8 rounded-2xl border border-red-900/30 bg-red-950/20 max-w-sm">
          <p className="text-red-400 font-semibold mb-2">Backend Offline</p>
          <p className="text-slate-500 text-sm">Start the FastAPI server on port 8000 first.</p>
          <code className="block mt-3 text-xs text-slate-600 bg-white/5 px-3 py-2 rounded-lg">
            uvicorn main:app --reload --port 8000
          </code>
        </div>
      </div>
    )
  }

  if (!config) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#09090b]">
        <motion.div animate={{ opacity: [0.4, 1, 0.4] }} transition={{ duration: 1.5, repeat: Infinity }}
          className="text-slate-600 text-sm">
          Connecting to generation engine...
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col lg:flex-row overflow-hidden">

      {/* =============================================
          MOBILE TOP BAR (< 1024px only)
      ============================================= */}
      <div className="lg:hidden flex items-center justify-between px-4 py-3 border-b border-white/5 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
            <Palette className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="text-sm font-bold text-white">Image Studio</span>
        </div>
        <button
          onClick={() => setShowConfigDrawer(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-slate-300"
        >
          <SlidersHorizontal className="w-3.5 h-3.5" /> Config
        </button>
      </div>

      {/* =============================================
          LEFT SIDEBAR — DESKTOP (>= 1024px)
      ============================================= */}
      <aside className="hidden lg:flex w-[360px] shrink-0 h-screen overflow-y-auto border-r border-white/[0.05] bg-white/[0.01] backdrop-blur-sm flex-col">
        <SidebarContent
          config={config}
          selectedEngine={selectedEngine} setSelectedEngine={setSelectedEngine}
          selectedRatio={selectedRatio} setSelectedRatio={setSelectedRatio}
          selectedStyle={selectedStyle} setSelectedStyle={setSelectedStyle}
        />
      </aside>

      {/* =============================================
          MOBILE CONFIG DRAWER (bottom sheet)
      ============================================= */}
      <AnimatePresence>
        {showConfigDrawer && (
          <>
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setShowConfigDrawer(false)}
              className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            />
            <motion.div
              initial={{ y: '100%' }} animate={{ y: 0 }} exit={{ y: '100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="lg:hidden fixed bottom-0 inset-x-0 z-50 max-h-[85vh] overflow-y-auto
                         bg-[#0b0f19] border-t border-white/10 rounded-t-3xl backdrop-blur-xl"
            >
              <div className="sticky top-0 bg-[#0b0f19]/95 backdrop-blur-xl flex items-center justify-between px-5 py-4 border-b border-white/5">
                <span className="text-sm font-bold text-white">Configuration</span>
                <button onClick={() => setShowConfigDrawer(false)} className="text-slate-500">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="px-5 py-5">
                <SidebarContent
                  config={config}
                  selectedEngine={selectedEngine} setSelectedEngine={setSelectedEngine}
                  selectedRatio={selectedRatio} setSelectedRatio={setSelectedRatio}
                  selectedStyle={selectedStyle} setSelectedStyle={setSelectedStyle}
                  hideFooter
                />
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* =============================================
          RIGHT WORKSPACE
      ============================================= */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">

        <div className="hidden lg:flex shrink-0 px-8 py-5 border-b border-white/[0.05] items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-white">Generation Canvas</h2>
            <p className="text-xs text-slate-600 mt-0.5">
              {phase === 'processing' ? 'Generating...' : 'Configure parameters and generate'}
            </p>
          </div>
          {phase === 'output' && generatedImage && (
            <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-2 text-xs text-slate-500">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]" />
              {generatedImage.width}×{generatedImage.height} · {generatedImage.file_size_kb} KB
            </motion.div>
          )}
        </div>

        <div className="flex-1 flex overflow-hidden">

          {/* Image Canvas */}
          <div className="flex-1 overflow-y-auto p-4 lg:p-8 pb-24 lg:pb-8">
            <GenerationCanvas
              phase={phase === 'error' ? 'idle' : phase}
              image={generatedImage}
              onDownload={handleDownload}
              onRetry={() => { setPhase('idle'); setGeneratedImage(null) }}
              engine={selectedEngine}
            />
          </div>

          {/* Prompt Panel — DESKTOP */}
          <div className="hidden lg:block w-[340px] shrink-0 border-l border-white/[0.05] p-6 overflow-y-auto">
            <PromptWorkspace
              prompt={prompt} negativePrompt={negativePrompt} maxChars={maxChars}
              onPromptChange={setPrompt} onNegativeChange={setNegativePrompt}
              onGenerate={handleGenerate} isGenerating={phase === 'processing'}
              textareaRef={promptRef}
            />
          </div>

        </div>
      </main>

      {/* =============================================
          MOBILE PROMPT DRAWER + FAB
      ============================================= */}
      <AnimatePresence>
        {showPromptDrawer && (
          <>
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setShowPromptDrawer(false)}
              className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            />
            <motion.div
              initial={{ y: '100%' }} animate={{ y: 0 }} exit={{ y: '100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="lg:hidden fixed bottom-0 inset-x-0 z-50 max-h-[85vh] overflow-y-auto
                         bg-[#0b0f19] border-t border-white/10 rounded-t-3xl"
            >
              <div className="sticky top-0 bg-[#0b0f19]/95 backdrop-blur-xl flex items-center justify-between px-5 py-4 border-b border-white/5">
                <span className="text-sm font-bold text-white">Prompt</span>
                <button onClick={() => setShowPromptDrawer(false)} className="text-slate-500">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="px-5 py-5">
                <PromptWorkspace
                  prompt={prompt} negativePrompt={negativePrompt} maxChars={maxChars}
                  onPromptChange={setPrompt} onNegativeChange={setNegativePrompt}
                  onGenerate={handleGenerate} isGenerating={phase === 'processing'}
                  textareaRef={promptRef}
                />
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Mobile Floating Action Button */}
      {!showPromptDrawer && !showConfigDrawer && (
        <motion.button
          initial={{ scale: 0 }} animate={{ scale: 1 }}
          onClick={() => setShowPromptDrawer(true)}
          disabled={phase === 'processing'}
          className="lg:hidden fixed bottom-5 right-5 z-30 w-14 h-14 rounded-full
                     bg-gradient-to-br from-violet-600 to-indigo-600 shadow-[0_4px_25px_rgba(139,92,246,0.5)]
                     flex items-center justify-center disabled:opacity-50"
        >
          {phase === 'processing' ? (
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              className="w-5 h-5 border-2 border-white/40 border-t-white rounded-full" />
          ) : (
            <Sparkles className="w-6 h-6 text-white" />
          )}
        </motion.button>
      )}

      {/* Toast Notifications */}
      <div className="fixed bottom-6 right-6 z-50 lg:right-6">
        <AnimatePresence>
          {toast && (
            <Toast
              message={toast.message}
              type={toast.type}
              autoRetrySeconds={toast.autoRetrySeconds}
              onClose={() => setToast(null)}
              onRetry={toast.type !== 'success' ? handleGenerate : undefined}
            />
          )}
        </AnimatePresence>
      </div>

    </div>
  )
}

// ------------------------------------------------------------
// SHARED SIDEBAR CONTENT — used by both desktop aside and mobile drawer
// ------------------------------------------------------------
function SidebarContent({
  config, selectedEngine, setSelectedEngine,
  selectedRatio, setSelectedRatio, selectedStyle, setSelectedStyle,
  hideFooter
}: any) {
  return (
    <>
      <div className="hidden lg:block px-6 pt-6 pb-5 border-b border-white/[0.05]">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-[0_0_15px_rgba(139,92,246,0.4)]">
            <Palette className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white">Image Studio</h1>
            <p className="text-[10px] text-slate-600">DecodeLabs · Project 3</p>
          </div>
        </div>
      </div>

      <div className="flex-1 lg:px-5 lg:py-5 space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Settings2 className="w-3.5 h-3.5 text-slate-600" />
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Generation Engine</span>
          </div>
          <EngineSelector engines={config.engines} selected={selectedEngine} onSelect={setSelectedEngine} />
        </div>

        <div>
          <div className="flex items-center gap-2 mb-3">
            <Layers className="w-3.5 h-3.5 text-slate-600" />
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Aspect Ratio</span>
          </div>
          <AspectRatioGrid ratios={config.aspect_ratios} selected={selectedRatio} onSelect={setSelectedRatio} />
          <p className="text-xs text-slate-700 mt-2 pl-1">{config.aspect_ratios[selectedRatio]?.label}</p>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-3">
            <Palette className="w-3.5 h-3.5 text-slate-600" />
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Style Preset</span>
          </div>
          <div className="grid grid-cols-2 gap-1.5">
            {config.style_presets.map((preset: string) => (
              <button
                key={preset}
                onClick={() => setSelectedStyle(preset)}
                className={`px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 text-left
                  ${selectedStyle === preset
                    ? 'bg-violet-950/60 border border-violet-500/40 text-violet-300'
                    : 'bg-white/[0.02] border border-white/5 text-slate-500 hover:border-white/10 hover:text-slate-400'
                  }`}
              >
                {preset}
              </button>
            ))}
          </div>
        </div>
      </div>

      {!hideFooter && (
        <div className="hidden lg:block px-5 py-4 border-t border-white/[0.05]">
          <p className="text-[10px] text-slate-700 text-center">Built by Naeem Khan · FAST NUCES Peshawar</p>
        </div>
      )}
    </>
  )
}