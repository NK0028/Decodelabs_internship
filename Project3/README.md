# 🎨 Multimodal Image Generation Studio

> **DecodeLabs Internship — Generative AI | Project 3**

A production-grade full-stack application that translates natural language prompts into high-quality AI-generated images, built with a FastAPI backend and an immersive Next.js frontend.

---

## 🎯 Project Goal

Build a visual generation studio that integrates text-to-image APIs, handles exact pixel-resolution payloads, manages binary/URL image streams safely, and presents results through a world-class SaaS-grade interface.

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| Animation | Framer Motion |
| Icons | Lucide React |
| Image Engines | Hugging Face (FLUX.1-schnell), Pollinations.ai |
| Image Processing | Pillow (PIL) |

---

## 🧠 Core Architecture — 3-Phase Pipeline
INPUT PHASE → PROCESS PHASE → OUTPUT PHASE

**1. Core Engine & Payload Architecture**
- Strict aspect ratio mapper (16:9 → 1344×768, 1:1 → 1024×1024, 9:16 → 768×1344)
- Engine adapter factory (SOLID principles) supporting multiple text-to-image APIs
- Per-engine character limit enforcement with graceful truncation

**2. Production-Grade Network Gateway**
- Split-timeout policy: 3.05s connect / 120s read (accommodates GPU cluster latency)
- Exponential backoff + jitter retry logic for 429/503 responses
- Memory-safe binary streaming (`stream=True` + `iter_content(chunk_size=65536)`)
- Pixel-level integrity verification via forced `Image.open().load()`

**3. Full-Stack Orchestrator**
- FastAPI endpoints: `/generate`, `/config`, `/download/{filename}`, `/gallery`
- Next.js frontend with real 3-phase state management (Idle → Processing → Output)
- Graceful error handling with toast notifications and auto-retry countdowns

---

## ✨ Advanced UX Features

- ⌨️ **Keyboard-first control** — `Cmd/Ctrl + Enter` to generate instantly
- 🎬 **Staged loading sequence** — realistic pipeline status text during generation
- 🔔 **Smart toast system** — context-aware error messages with auto-retry
- 📱 **Fully responsive** — collapses into glassmorphic bottom sheets on mobile with a floating action button
- 🎨 **Style presets** — Cyberpunk, Minimalism, Photorealistic, Anime, Oil Painting, Watercolor
- ⬇️ **Download & gallery** — persistent local storage of all generated assets

---

## 🚀 How to Run Locally

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn requests pillow python-dotenv python-multipart
echo "HF_API_KEY=your_huggingface_token" > .env
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`

---

## 📁 Project Structure
Project3/
├── backend/
│   ├── main.py          # FastAPI endpoints
│   ├── engines.py       # Aspect ratio mapper + engine adapter factory
│   ├── gateway.py       # Split-timeout network gateway + retry logic
│   ├── pipeline.py      # 3-phase orchestrator
│   └── .env             # API keys (not pushed)
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── components/
│   │   │   ├── EngineSelector.tsx
│   │   │   ├── AspectRatioGrid.tsx
│   │   │   ├── PromptWorkspace.tsx
│   │   │   ├── GenerationCanvas.tsx
│   │   │   └── Toast.tsx
│   │   └── hooks/
│   │       └── useKeybinds.ts
└── README.md

---

## �� Engineering Challenges Solved

- Diagnosed and resolved a Hugging Face API migration (deprecated `api-inference.huggingface.co` endpoint → new router-based endpoint)
- Handled a retired model (410 Gone) by migrating to an actively supported model
- Implemented DNS-safe fallback engine (Pollinations.ai) as a redundancy path

---

## 👨‍💻 Author

**Naeem Khan** | FAST NUCES Peshawar | AI Engineering
DecodeLabs Internship Batch 2026
GitHub: github.com/NK0028
