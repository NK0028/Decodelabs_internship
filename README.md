# 🤖 AI Chatbot with Memory

> **DecodeLabs Internship — Generative AI | Project 1**

A production-grade conversational AI chatbot built with **Stateful Architecture** — transforming a stateless LLM into a fully contextual chat system through session state management.

---

##  Project Goal

Build a web app that remembers previous user messages during a live session by maintaining an active in-memory conversation history array.

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Web UI | Streamlit |
| AI Model | Google Gemini 2.5 Flash |
| SDK | google-genai |
| Secret Management | python-dotenv |

---

##  Core Architecture: Stateful Memory Loop
- **Mt** — Current user message at turn t
- **Ht-1** — Full historical array of all messages up to turn t-1
- **Rt** — Generated context-aware model response

---

## ✅ Key Features

- 🔁 **Stateful Memory Loop** — full conversation history sent with every API call
- 🛡️ **Input Validation Guard** — blocks empty inputs before they reach the API
- 📉 **Sliding Window (FIFO)** — prunes oldest messages to prevent token exhaustion
- 🧠 **Memory Inspector** — live sidebar showing memory usage (x/20 messages)
- 🗑️ **Clear Conversation** — reset session state instantly

---

##  Memory Exam (Passed ✅)

| Phase | Input | Expected Output | Result |
|---|---|---|---|
| State Initialization | "My name is Naeem" | Acknowledgment | ✅ |
| Context Distraction | Long AI poem request | Large generation | ✅ |
| State Extraction | "What is my name?" | "Your name is Naeem" | ✅ |

---

##  How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/NK00028/ai-chatbot-memory.git
cd ai-chatbot-memory
```

**2. Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install google-genai streamlit python-dotenv
```

**4. Add your API key**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env
```

**5. Run the app**
```bash
streamlit run app.py
```

---

##  Project Structure
'''
ai-chatbot-memory/

├── app.py          # Main application — stateful memory loop

├── .env            # API key (not pushed to GitHub)

├── .gitignore      # Protects secrets from being committed

└── README.md       # Project documentation
'''

---

##  Author

**Naeem Khan** 
DecodeLabs Internship Batch 2026
