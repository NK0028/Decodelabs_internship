# ============================================================
# Project 3: Multimodal Image Generation Studio
# File: pipeline.py — Phase 3: Architecture Orchestrator
# Role: Full-Stack Solutions Architect
# ============================================================

import base64
import logging
from engines import Engine, EngineAdapterFactory
from gateway import call_huggingface, call_pollinations

logger = logging.getLogger(__name__)


def run_pipeline(
    prompt:          str,
    engine:          str,
    aspect_ratio:    str = "1:1",
    negative_prompt: str = None,
    style_preset:    str = None,
    num_images:      int = 1,
    hf_api_key:      str = None,
) -> dict:
    """
    Main orchestration pipeline.
    Implements the 3-phase architecture from the PDF:
    INPUT → PROCESS → OUTPUT
    """

    logger.info(f"[PIPELINE] Starting — Engine: {engine} | Ratio: {aspect_ratio}")

    # --------------------------------------------------------
    # INPUT PHASE: Serialize and validate the multimodal payload
    # --------------------------------------------------------
    try:
        engine_enum = Engine(engine)
    except ValueError:
        raise ValueError(f"[INPUT_ERROR] Unknown engine: '{engine}'")

    payload = EngineAdapterFactory.build_payload(
        prompt=prompt,
        engine=engine_enum,
        aspect_ratio=aspect_ratio,
        negative_prompt=negative_prompt,
        style_preset=style_preset,
        num_images=num_images,
    )

    logger.info(
        f"[INPUT_PHASE] Payload validated — "
        f"{payload.width}x{payload.height} | {len(payload.prompt)} chars"
    )

    # --------------------------------------------------------
    # PROCESS PHASE: Route to correct engine gateway
    # --------------------------------------------------------
    try:
        if engine_enum == Engine.HUGGING_FACE:
            if not hf_api_key:
                raise ValueError("[PROCESS_ERROR] Hugging Face API key is required.")
            image_bytes, save_path = call_huggingface(payload, hf_api_key)

        elif engine_enum == Engine.POLLINATIONS:
            image_bytes, save_path = call_pollinations(payload)

        else:
            raise ValueError(f"[PROCESS_ERROR] No gateway for engine: {engine}")

    except ConnectionError as e:
        # ConnectTimeout — FAIL FAST
        logger.error(f"[PROCESS_PHASE] FAIL FAST — {e}")
        raise

    except TimeoutError as e:
        # ReadTimeout — already retried in gateway
        logger.error(f"[PROCESS_PHASE] Read timeout after retries — {e}")
        raise

    # --------------------------------------------------------
    # OUTPUT PHASE: Package result for frontend delivery
    # --------------------------------------------------------
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    result = {
        "status":       "success",
        "engine":       engine,
        "aspect_ratio": aspect_ratio,
        "width":        payload.width,
        "height":       payload.height,
        "prompt":       prompt,
        "style_preset": style_preset,
        "save_path":    save_path,
        "image_b64":    image_b64,
        "file_size_kb": round(len(image_bytes) / 1024, 2),
    }

    logger.info(
        f"[OUTPUT_PHASE] Complete — "
        f"File: {save_path} | Size: {result['file_size_kb']}KB"
    )
    return result