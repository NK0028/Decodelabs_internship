# ============================================================
# Project 1: Custom AI Chatbot with Memory
# Company: DecodeLabs | Intern: Naeem Khan
# Stack: Python + Streamlit + Google Gemini API
# Architecture: Stateful Memory Loop with Sliding Window
# ============================================================

import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# ------------------------------------------------------------
# STEP 1: Load API key from .env file
# ------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ------------------------------------------------------------
# STEP 2: Initialize the new Gemini client
# ------------------------------------------------------------
client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})
MODEL = "models/gemini-2.5-flash"

# ------------------------------------------------------------
# STEP 3: Streamlit Page Configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="AI Chatbot with Memory",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Chatbot with Memory")
st.caption("Built with Google Gemini | DecodeLabs Internship — Project 1")

# ------------------------------------------------------------
# STEP 4: Initialize the in-memory conversation history array
# This is the CORE of stateful architecture.
# Each item: {"role": "user"/"model", "parts": ["text"]}
# ------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------------------------------------------
# STEP 5: Sliding Window Configuration (FIFO pruning)
# ------------------------------------------------------------
MAX_HISTORY = 20

# ------------------------------------------------------------
# STEP 6: Display full conversation history on screen
# ------------------------------------------------------------
for message in st.session_state.history:
    role = message["role"]
    text = message["parts"][0]

    if role == "user":
        with st.chat_message("user"):
            st.markdown(text)
    else:
        with st.chat_message("assistant"):
            st.markdown(text)

# ------------------------------------------------------------
# STEP 7: Capture user input
# ------------------------------------------------------------
user_input = st.chat_input("Type your message here...")

if user_input:

    # --------------------------------------------------------
    # STEP 8: INPUT VALIDATION GUARD
    # Blocks empty/whitespace inputs → prevents API 400 errors
    # --------------------------------------------------------
    if not user_input.strip():
        st.warning("⚠️ Please type a message before sending.")
        st.stop()

    # --------------------------------------------------------
    # STEP 9: Display user message in UI
    # --------------------------------------------------------
    with st.chat_message("user"):
        st.markdown(user_input)

    # --------------------------------------------------------
    # STEP 10: APPEND user message to history array
    # --------------------------------------------------------
    st.session_state.history.append({
        "role": "user",
        "parts": [user_input]
    })

    # --------------------------------------------------------
    # STEP 11: SLIDING WINDOW — FIFO Pruning
    # Drop oldest messages when limit exceeded
    # --------------------------------------------------------
    while len(st.session_state.history) > MAX_HISTORY:
        st.session_state.history.pop(0)

    # --------------------------------------------------------
    # STEP 12: Build contents payload for new SDK format
    # Convert our history array into proper Content objects
    # --------------------------------------------------------
    contents = []
    for msg in st.session_state.history:
        contents.append(
            types.Content(
                role=msg["role"],
                parts=[types.Part(text=msg["parts"][0])]
            )
        )

    # --------------------------------------------------------
    # STEP 13: TRANSMIT — Send full history to Gemini API
    # --------------------------------------------------------
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents
        )
        bot_reply = response.text

    except Exception as e:
        bot_reply = f"❌ API Error: {str(e)}"

    # --------------------------------------------------------
    # STEP 14: RECORD — Append model response to history
    # Completes the memory loop for this turn
    # --------------------------------------------------------
    st.session_state.history.append({
        "role": "model",
        "parts": [bot_reply]
    })

    # --------------------------------------------------------
    # STEP 15: Display bot response in UI
    # --------------------------------------------------------
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

# ------------------------------------------------------------
# STEP 16: Sidebar — Memory Inspector & Controls
# ------------------------------------------------------------
with st.sidebar:
    st.header("🧠 Memory Inspector")
    st.write(f"**Messages in memory:** {len(st.session_state.history)} / {MAX_HISTORY}")

    st.progress(min(len(st.session_state.history) / MAX_HISTORY, 1.0))

    if len(st.session_state.history) == MAX_HISTORY:
        st.warning("⚠️ Sliding window active — oldest messages being pruned.")

    st.divider()

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.divider()
    st.caption("DecodeLabs Internship | Project 1")
    st.caption("Architecture: Stateful Memory Loop")
    st.caption("Model: Google Gemini 2.0 Flash")