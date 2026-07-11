# ============================================================
# Project 3: Multimodal Image Generation Studio
# File: engines.py — Phase 1: Core Engine & Payload Architecture
# Company: DecodeLabs | Intern: Naeem Khan
# Role: Principal Staff Engineer — Adapter Factory
# ============================================================

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# ASPECT RATIO MAPPER
# Translates standard aspect ratio intents into exact pixel
# payloads. Throws explicit validation error for unsupported
# dimensions — critical architecture rule from the PDF.
# ------------------------------------------------------------
ASPECT_RATIO_MAP = {
    "16:9": {"width": 1344, "height": 768,  "label": "Landscape — Web banners, presentations"},
    "1:1":  {"width": 1024, "height": 1024, "label": "Square — Avatars, product grids"},
    "9:16": {"width": 768,  "height": 1344, "label": "Vertical — Mobile reels, wallpapers"},
}

def resolve_aspect_ratio(ratio: str) -> dict:
    """
    Strict Aspect Ratio Mapper.
    Translates ratio intent to exact pixel payload.
    Raises ValueError immediately for unsupported dimensions.
    """
    if ratio not in ASPECT_RATIO_MAP:
        supported = list(ASPECT_RATIO_MAP.keys())
        raise ValueError(
            f"[PAYLOAD_ERROR] Unsupported aspect ratio '{ratio}'. "
            f"Supported ratios: {supported}. "
            f"Passing unsupported dimensions causes immediate API handshake failure."
        )
    payload = ASPECT_RATIO_MAP[ratio]
    logger.info(f"[ASPECT_RATIO] Resolved '{ratio}' → {payload['width']}x{payload['height']}")
    return payload


# ------------------------------------------------------------
# ENGINE ENUM
# Defines the three supported generation engines
# ------------------------------------------------------------
class Engine(str, Enum):
    HUGGING_FACE    = "huggingface"     # Stability AI SDXL via HF — RAW binary bytes
    POLLINATIONS    = "pollinations"    # Pollinations.ai — Public Image URL


# ------------------------------------------------------------
# ENGINE CONFIGURATION MATRIX
# From the PDF: each engine has strict character limits
# and different output formats
# ------------------------------------------------------------
ENGINE_CONFIG = {
    Engine.HUGGING_FACE: {
    "name":           "Hugging Face — FLUX.1 Schnell",
    "max_chars":      10000,   # Stable Image Core limit
    "output_format":  "raw_bytes",
    "model":          "black-forest-labs/FLUX.1-schnell",
    "description":    "High quality binary stream output — RAW Image Bytes",
    "supports_negative_prompt": True,
},
    Engine.POLLINATIONS: {
        "name":           "Pollinations.ai — Free Tier",
        "max_chars":      1000,    # URL-based engine limit
        "output_format":  "public_url",
        "model":          "flux",
        "description":    "Public Image URL output — no API key required",
        "supports_negative_prompt": False,
    },
}


# ------------------------------------------------------------
# PROMPT VALIDATOR & CHARACTER LIMIT ENFORCER
# Gracefully truncates or rejects prompts exceeding engine limits
# before hitting the network — saves API costs and prevents errors
# ------------------------------------------------------------
def enforce_character_limit(
    prompt: str,
    engine: Engine,
    truncate: bool = True
) -> str:
    """
    Enforces per-engine character limits.
    If truncate=True: silently truncates with warning.
    If truncate=False: raises ValueError immediately.
    """
    config = ENGINE_CONFIG[engine]
    max_chars = config["max_chars"]

    if len(prompt) <= max_chars:
        return prompt

    if truncate:
        truncated = prompt[:max_chars]
        logger.warning(
            f"[CHAR_LIMIT] Prompt truncated from {len(prompt)} to "
            f"{max_chars} chars for engine '{engine.value}'"
        )
        return truncated
    else:
        raise ValueError(
            f"[CHAR_LIMIT_ERROR] Prompt length {len(prompt)} exceeds "
            f"engine limit of {max_chars} for '{config['name']}'. "
            f"Please shorten your prompt."
        )


# ------------------------------------------------------------
# PAYLOAD DATACLASS
# Structured payload passed to the network gateway
# ------------------------------------------------------------
@dataclass
class GenerationPayload:
    prompt:          str
    engine:          Engine
    width:           int
    height:          int
    aspect_ratio:    str
    negative_prompt: Optional[str] = None
    style_preset:    Optional[str] = None
    num_images:      int = 1

    def validate(self):
        """Full payload validation before network transmission."""
        if not self.prompt or not self.prompt.strip():
            raise ValueError("[PAYLOAD_ERROR] Prompt cannot be empty.")
        if self.num_images < 1 or self.num_images > 4:
            raise ValueError("[PAYLOAD_ERROR] num_images must be between 1 and 4.")
        return True


# ------------------------------------------------------------
# STYLE PRESETS
# From the PDF conclusion — adds style preset parameters
# to the payload for creative variance
# ------------------------------------------------------------
STYLE_PRESETS = {
    "None":          "",
    "Cyberpunk":     "cyberpunk aesthetic, neon lights, dark city, rain-soaked streets, high contrast",
    "Minimalism":    "minimalist design, clean lines, white space, simple geometric forms",
    "Photorealistic":"photorealistic, 8K resolution, DSLR quality, natural lighting, hyperdetailed",
    "Anime":         "anime style, Studio Ghibli inspired, vibrant colors, cel shading",
    "Oil Painting":  "oil painting style, textured brushstrokes, classical art, museum quality",
    "Watercolor":    "watercolor painting, soft edges, translucent layers, artistic",
}


# ------------------------------------------------------------
# ENGINE ADAPTER FACTORY
# Main factory class — abstracts payload structure per engine
# SOLID principle: Open/Closed — add new engines without
# modifying existing code
# ------------------------------------------------------------
class EngineAdapterFactory:
    """
    Adapter factory that builds engine-specific request payloads.
    Each engine has different API formats, limits, and output types.
    """

    @staticmethod
    def build_payload(
        prompt:          str,
        engine:          Engine,
        aspect_ratio:    str = "1:1",
        negative_prompt: Optional[str] = None,
        style_preset:    Optional[str] = None,
        num_images:      int = 1,
    ) -> GenerationPayload:
        """
        Main factory method.
        1. Resolves aspect ratio to exact pixel dimensions
        2. Enforces character limits
        3. Appends style preset to prompt
        4. Returns validated GenerationPayload
        """
        # Step 1: Resolve aspect ratio → exact pixel dimensions
        dimensions = resolve_aspect_ratio(aspect_ratio)

        # Step 2: Append style preset to prompt if selected
        style_suffix = ""
        if style_preset and style_preset != "None":
            style_suffix = STYLE_PRESETS.get(style_preset, "")
            if style_suffix:
                prompt = f"{prompt}, {style_suffix}"
                logger.info(f"[STYLE] Applied preset '{style_preset}' to prompt")

        # Step 3: Enforce character limit for target engine
        prompt = enforce_character_limit(prompt, engine, truncate=True)

        # Step 4: Build and validate the payload
        payload = GenerationPayload(
            prompt=prompt,
            engine=engine,
            width=dimensions["width"],
            height=dimensions["height"],
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
            style_preset=style_preset,
            num_images=num_images,
        )
        payload.validate()

        logger.info(
            f"[FACTORY] Payload built — Engine: {engine.value} | "
            f"Size: {payload.width}x{payload.height} | "
            f"Prompt chars: {len(prompt)}"
        )
        return payload