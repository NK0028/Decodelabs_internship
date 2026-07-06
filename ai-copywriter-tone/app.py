# ============================================================
# Project 2: Automated Copywriting & Tone Transformer
# Company: DecodeLabs | Intern: Naeem Khan
# Stack: Python + Streamlit + Google Gemini API + Pydantic
# Architecture: Dynamic Prompt Compilation + Inference Tuning
# ============================================================

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import json
import re

# ------------------------------------------------------------
# STEP 1: Load API key and initialize Gemini client
# ------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ------------------------------------------------------------
# STEP 2: Pydantic Output Schema
# Forces structured, validated data from the model
# ------------------------------------------------------------
class CopyOutput(BaseModel):
    headline: str
    body: str
    call_to_action: str
    hashtags: list[str]
    character_count: int
    tone_achieved: str

# ------------------------------------------------------------
# STEP 3: Platform Configuration
# Each platform has strict constraints injected into the prompt
# ------------------------------------------------------------
PLATFORM_CONFIG = {
    "LinkedIn": {
        "char_limit": 3000,
        "tone_default": 0.3,
        "description": "Professional network — structured, insight-driven",
        "constraints": "Use professional language. Max 3000 characters. Include 3-5 hashtags. End with a clear call to action."
    },
    "Instagram": {
        "char_limit": 2200,
        "tone_default": 0.8,
        "description": "Visual platform — casual, engaging, emotional",
        "constraints": "Use casual energetic language. Max 2200 characters. Include 5-10 hashtags with emojis. Start with a hook."
    },
    "Email": {
        "char_limit": 500,
        "tone_default": 0.3,
        "description": "Direct marketing — persuasive, conversion-focused",
        "constraints": "Write subject line first, then body. Max 500 words. One clear call to action. No hashtags."
    },
    "Twitter/X": {
        "char_limit": 280,
        "tone_default": 0.7,
        "description": "Microblogging — punchy, witty, concise",
        "constraints": "STRICT 280 character limit. One powerful sentence. Max 2 hashtags. Make it punchy."
    }
}

# ------------------------------------------------------------
# STEP 4: Tone Configuration
# Maps tone to Temperature + Top_P inference parameters
# ------------------------------------------------------------
TONE_CONFIG = {
    "Professional": {"temperature": 0.2, "top_p": 0.80,
                     "description": "Structured, factual, corporate"},
    "Witty":        {"temperature": 0.9, "top_p": 0.95,
                     "description": "Clever, humorous, unexpected"},
    "Inspirational":{"temperature": 0.7, "top_p": 0.90,
                     "description": "Motivating, emotional, uplifting"},
    "Casual":       {"temperature": 0.8, "top_p": 0.90,
                     "description": "Friendly, conversational, relaxed"},
    "Urgent":       {"temperature": 0.4, "top_p": 0.85,
                     "description": "Direct, time-sensitive, action-driving"},
    "Luxury":       {"temperature": 0.5, "top_p": 0.88,
                     "description": "Premium, elegant, aspirational"}
}

# ------------------------------------------------------------
# STEP 5: Dynamic Prompt Template Compiler
# CORE of Project 2 — f-strings inject variables into template
# Raw user input is sanitized before touching the model
# ------------------------------------------------------------
def compile_prompt(product_name, product_description,
                   platform, tone, target_audience):
    platform_info = PLATFORM_CONFIG[platform]
    tone_info = TONE_CONFIG[tone]

    prompt = f"""
You are an expert marketing copywriter specializing in {platform} content.

PRODUCT INFORMATION:
- Product Name: {product_name}
- Description: {product_description}
- Target Audience: {target_audience}

GENERATION PARAMETERS:
- Platform: {platform}
- Platform Context: {platform_info['description']}
- Required Tone: {tone}
- Tone Style: {tone_info['description']}
- Character Limit: {platform_info['char_limit']} characters

PLATFORM CONSTRAINTS (MANDATORY):
{platform_info['constraints']}

CRITICAL OUTPUT INSTRUCTIONS:
You MUST respond with ONLY a valid JSON object.
Do NOT use markdown. Do NOT add explanation. Do NOT add code blocks.
Keep the body text SHORT — maximum 300 words.
Every string value must be on one line. No newlines inside JSON string values.
The response must start with {{ and end with }}.
The JSON must have exactly these fields:
{{
    "headline": "compelling headline for the copy",
    "body": "main copy body text",
    "call_to_action": "specific action for the reader to take",
    "hashtags": ["hashtag1", "hashtag2"],
    "character_count": total_character_count_as_integer,
    "tone_achieved": "brief description of tone used"
}}

Write the copy now. Return ONLY the JSON object.
"""
    return prompt

# ------------------------------------------------------------
# STEP 6: Generate Copy Function with Retry Shield
# ------------------------------------------------------------
def generate_copy(product_name, product_description,
                  platform, tone, target_audience):

    tone_config = TONE_CONFIG[tone]
    prompt = compile_prompt(
        product_name, product_description,
        platform, tone, target_audience
    )

    generation_config = genai.types.GenerationConfig(
        temperature=tone_config["temperature"],
        top_p=tone_config["top_p"],
        max_output_tokens=8192,
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        raw_text = response.text.strip()

        # Clean markdown code blocks if model adds them
        raw_text = re.sub(r'```json\s*', '', raw_text)
        raw_text = re.sub(r'```\s*', '', raw_text)
        raw_text = raw_text.strip()

        # Robust JSON extraction — find the first { and last }
        # This handles cases where model adds text before/after JSON
        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1
        if start == -1 or end == 0:
            return None, f"No JSON found in response: {raw_text[:200]}"
        
        json_str = raw_text[start:end]

        # Parse JSON and validate with Pydantic
        data = json.loads(json_str)
        validated = CopyOutput(**data)
        return validated, None

    except json.JSONDecodeError as e:
        return None, f"JSON Parse Error: {str(e)}"
    except Exception as e:
        return None, f"API Error: {str(e)}"

# ------------------------------------------------------------
# STEP 7: Streamlit Page Configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="AI Copywriter & Tone Transformer",
    page_icon="✍️",
    layout="wide"
)

st.title("✍️ Automated Copywriting & Tone Transformer")
st.caption("DecodeLabs Internship — Project 2 | Powered by Google Gemini")

# ------------------------------------------------------------
# STEP 8: Sidebar — Input Controls
# ------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Campaign Configuration")
    st.divider()

    st.subheader("📦 Product Details")
    product_name = st.text_input(
        "Product Name",
        placeholder="e.g. SkyPulse Weather App"
    )
    product_description = st.text_area(
        "Product Description",
        placeholder="e.g. A real-time weather app with AI summaries...",
        height=120
    )
    target_audience = st.text_input(
        "Target Audience",
        placeholder="e.g. Tech-savvy professionals aged 25-35"
    )

    st.divider()

    st.subheader("🎯 Platform & Tone")
    selected_platforms = st.multiselect(
        "Select Platforms",
        list(PLATFORM_CONFIG.keys()),
        default=["LinkedIn", "Instagram"],
        help="Generate copy for multiple platforms simultaneously"
    )

    selected_tone = st.selectbox(
        "Select Tone",
        list(TONE_CONFIG.keys()),
        help="Tone controls Temperature and Top_P automatically"
    )

    tone_params = TONE_CONFIG[selected_tone]
    st.info(
        f"🌡️ Temperature: `{tone_params['temperature']}`\n\n"
        f"🎲 Top_P: `{tone_params['top_p']}`\n\n"
        f"📝 Style: {tone_params['description']}"
    )

    st.divider()

    generate_btn = st.button(
        "🚀 Generate Copy",
        use_container_width=True,
        type="primary"
    )

    st.divider()
    st.caption("DecodeLabs Internship | Project 2")
    st.caption("Architecture: Dynamic Prompt Compilation")
    st.caption("Model: Google Gemini 1.5 Flash")

# ------------------------------------------------------------
# STEP 9: Default View — Platform Overview
# ------------------------------------------------------------
if not generate_btn:
    st.subheader("📋 Platform Constraints Overview")
    cols = st.columns(len(PLATFORM_CONFIG))
    for idx, (platform, config) in enumerate(PLATFORM_CONFIG.items()):
        with cols[idx]:
            st.metric(
                label=platform,
                value=f"{config['char_limit']} chars",
                delta=f"Temp: {config['tone_default']}"
            )
            st.caption(config['description'])
    st.divider()
    st.info("👈 Fill in the product details in the sidebar and click **Generate Copy** to begin.")

# ------------------------------------------------------------
# STEP 10: Generation Logic
# ------------------------------------------------------------
if generate_btn:

    # Input Validation Guard
    if not product_name.strip():
        st.error("❌ Product Name is required.")
        st.stop()
    if not product_description.strip():
        st.error("❌ Product Description is required.")
        st.stop()
    if not target_audience.strip():
        st.error("❌ Target Audience is required.")
        st.stop()
    if not selected_platforms:
        st.error("❌ Select at least one platform.")
        st.stop()

    st.subheader(f"🎨 Generated Copy — {selected_tone} Tone")
    st.caption(
        f"Product: **{product_name}** | "
        f"Tone: **{selected_tone}** | "
        f"Temperature: **{tone_params['temperature']}** | "
        f"Top_P: **{tone_params['top_p']}**"
    )
    st.divider()

    # Generate for each selected platform
    for platform in selected_platforms:
        with st.expander(f"📱 {platform} Copy", expanded=True):
            with st.spinner(f"Generating {platform} copy..."):
                result, error = generate_copy(
                    product_name, product_description,
                    platform, selected_tone, target_audience
                )

            if error:
                st.error(f"❌ {error}")
            else:
                char_limit = PLATFORM_CONFIG[platform]["char_limit"]

                # Compliance check
                if result.character_count <= char_limit:
                    st.success(
                        f"✅ {result.character_count} / {char_limit} "
                        f"characters — Compliant"
                    )
                else:
                    st.warning(
                        f"⚠️ {result.character_count} / {char_limit} "
                        f"characters — Exceeds limit"
                    )

                st.markdown("### 💡 Headline")
                st.markdown(f"> {result.headline}")

                st.markdown("### 📝 Body Copy")
                st.markdown(result.body)

                st.markdown("### 🎯 Call to Action")
                st.markdown(f"**{result.call_to_action}**")

                if result.hashtags:
                    st.markdown("### #️⃣ Hashtags")
                    st.markdown(" ".join([f"`{h}`" for h in result.hashtags]))

                st.caption(f"🎭 Tone achieved: {result.tone_achieved}")

                # Full copy block for easy copying
                full_copy = (
                    f"{result.headline}\n\n"
                    f"{result.body}\n\n"
                    f"{result.call_to_action}\n\n"
                    f"{' '.join(result.hashtags)}"
                )
                st.code(full_copy, language=None)