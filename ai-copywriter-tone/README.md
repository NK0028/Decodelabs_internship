# ✍️ Automated Copywriting & Tone Transformer

> **DecodeLabs Internship — Generative AI | Project 2**

A production-grade AI copywriting engine that takes a raw product description and automatically generates professional marketing copy tailored to different platforms — with full inference parameter control.

---

## 🎯 Project Goal

Build an application that compiles dynamic prompt templates using user-defined variables (Product_Name, Platform, Tone) and precisely adjusts hyperparameters (Temperature, Top_P) to control creative variance across multiple marketing platforms simultaneously.

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Web UI | Streamlit |
| AI Model | Google Gemini 2.5 Flash |
| SDK | google-generativeai |
| Output Validation | Pydantic |
| Secret Management | python-dotenv |

---

## 🧠 Core Architecture: Dynamic Prompt Compilation
Input (Product + Platform + Tone) → Prompt Compiler (f-strings) → Inference Engine (Temp + Top_P) → Validated Output (Pydantic)

---

## 🎛️ Inference Parameter Tuning

| Tone | Temperature | Top_P | Use Case |
|---|---|---|---|
| Professional | 0.2 | 0.80 | LinkedIn, Email |
| Witty | 0.9 | 0.95 | Social media, Twitter |
| Inspirational | 0.7 | 0.90 | Campaigns, Instagram |
| Casual | 0.8 | 0.90 | Instagram, community |
| Urgent | 0.4 | 0.85 | Limited offers, CTAs |
| Luxury | 0.5 | 0.88 | Premium products |

---

## 📱 Platform Constraints

| Platform | Char Limit | Default Temp | Format |
|---|---|---|---|
| LinkedIn | 3,000 | 0.3 | Professional + 3-5 hashtags |
| Instagram | 2,200 | 0.8 | Hook + emojis + 5-10 hashtags |
| Email | 500 words | 0.3 | Subject line + body |
| Twitter/X | 280 | 0.7 | Punchy + max 2 hashtags |

---

## ✅ Key Features

- 🧩 **Dynamic Prompt Template Compiler** — f-strings inject Product, Platform, Tone into a Master Instruction Template
- 🎛️ **Inference Parameter Control** — Temperature and Top_P auto-set per tone selection
- 🛡️ **Platform Constraint Enforcement** — Character limits injected directly into prompt payload
- ✅ **Pydantic Output Validation** — Structured schema enforces headline, body, CTA, hashtags
- 🔍 **Input Validation Guard** — All fields sanitized before reaching the API
- 📊 **Compliance Indicator** — Live character count vs platform limit check
- 📋 **Copy Export Block** — Full formatted copy ready to paste anywhere
- 🔄 **Multi-Platform Generation** — Generate for all 4 platforms simultaneously

---

## 🚀 How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/NK0028/Decodelabs_internship.git
cd Decodelabs_internship/ai-copywriter-tone
```

**2. Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install google-generativeai streamlit python-dotenv pydantic
```

**4. Add your API key**
```bash
echo "GEMINI_API_KEY=your_key_here" > .env
```

**5. Run the app**
```bash
venv/bin/python -m streamlit run app.py
```

---

## 📁 Project Structure
ai-copywriter-tone/
├── app.py          # Main application — prompt compiler + inference engine
├── .env            # API key (not pushed to GitHub)
├── .gitignore      # Protects secrets
└── README.md       # Project documentation

---

## 🧪 What This Project Proves

By completing this project you demonstrate:
- Dynamic string template compilation using f-strings
- Inference parameter tuning (Temperature + Top_P)
- Platform-specific constraint injection into prompts
- Structured output validation with Pydantic
- Production-grade input sanitization pipeline

---

## 👨‍💻 Author

**Naeem Khan** | FAST NUCES Peshawar | AI Engineering
DecodeLabs Internship Batch 2026
GitHub: github.com/NK0028
