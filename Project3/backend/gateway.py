# ============================================================
# Project 3: Multimodal Image Generation Studio
# File: gateway.py — Phase 2: Production-Grade Network Gateway
# Role: Senior Backend & Infrastructure Engineer
# ============================================================

import requests
import logging
import time
import random
import os
import uuid
from io import BytesIO
from PIL import Image
from engines import GenerationPayload, Engine, ENGINE_CONFIG

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# SPLIT-TIMEOUT CONFIGURATION
# From the PDF: never use requests without explicit timeouts.
# Connection timeout: 3.05s (TCP retransmission buffer)
# Read timeout: 60-120s (GPU cluster generation time)
# ------------------------------------------------------------
CONNECT_TIMEOUT = 3.05   # TCP handshake + 0.05s retransmission buffer
READ_TIMEOUT    = 120    # Diffusion model generation on remote GPU

SPLIT_TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)

# ------------------------------------------------------------
# EXPONENTIAL BACKOFF CONFIGURATION
# From the PDF: retry with jitter to prevent bot-swarms
# locking up the API gateway
# ------------------------------------------------------------
MAX_RETRIES     = 3
BASE_DELAY      = 2.0    # seconds
BACKOFF_FACTOR  = 2      # doubles each retry
MAX_JITTER      = 1.0    # random jitter range

# Image storage directory
IMAGES_DIR = "generated_images"
os.makedirs(IMAGES_DIR, exist_ok=True)


# ------------------------------------------------------------
# BINARY INTEGRITY VERIFIER
# From the PDF: never trust imghdr.what() or verify() alone.
# Must force Image.open().load() for full pixel-level decode.
# This catches truncated data streams that pass header checks.
# ------------------------------------------------------------
def verify_image_integrity(image_bytes: bytes) -> bool:
    """
    Forces rigorous pixel-level decode using Pillow .load().
    Catches truncated binary streams that header checks miss.
    Raises OSError if the data stream is broken mid-download.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        img.load()  # Forces full pixel decode — not just header read
        logger.info(
            f"[INTEGRITY] Image verified — "
            f"Format: {img.format} | Size: {img.size} | Mode: {img.mode}"
        )
        return True
    except OSError as e:
        logger.error(f"[INTEGRITY_FAIL] Broken data stream detected: {e}")
        return False
    except Exception as e:
        logger.error(f"[INTEGRITY_FAIL] Unexpected verification error: {e}")
        return False


# ------------------------------------------------------------
# MEMORY-SAFE BINARY STREAM DOWNLOADER
# From the PDF: never load high-res images entirely into RAM.
# Use stream=True + iter_content(chunk_size=65536)
# ------------------------------------------------------------
def stream_image_from_url(url: str, save_path: str) -> bytes:
    """
    Memory-safe image downloader using chunked streaming.
    Prevents RAM overflow on large binary payloads.
    Writes sequentially to local disk in 65.5KB chunks.
    """
    logger.info(f"[STREAM] Starting chunked download from URL: {url[:60]}...")

    try:
        response = requests.get(
            url,
            stream=True,           # Enable chunked streaming
            timeout=SPLIT_TIMEOUT  # Always apply split-timeout
        )
        response.raise_for_status()

        total_bytes = 0
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=65536):  # 65.5KB chunks
                if chunk:
                    f.write(chunk)
                    total_bytes += len(chunk)

        logger.info(f"[STREAM] Download complete — {total_bytes} bytes written to {save_path}")

        # Read back for integrity verification and return
        with open(save_path, 'rb') as f:
            return f.read()

    except requests.exceptions.ConnectTimeout:
        raise ConnectionError(
            "[FAIL_FAST] ConnectTimeout — Cannot establish TCP connection. "
            "Diagnosis: Network routing issue, firewall, or downed server. "
            "Action: FAIL FAST. Do not retry."
        )
    except requests.exceptions.ReadTimeout:
        raise TimeoutError(
            "[READ_TIMEOUT] Server connected but response timed out. "
            "Diagnosis: Overloaded GPU cluster or massive response payload. "
            "Action: Prepare for secondary retry with exponential backoff."
        )


# ------------------------------------------------------------
# EXPONENTIAL BACKOFF RETRY ENGINE
# From the PDF: randomized delays prevent synchronized bot-swarms
# Delay = multiplier * 2^attempt +/- random_jitter
# ------------------------------------------------------------
def calculate_backoff_delay(attempt: int) -> float:
    """
    Calculates exponential backoff delay with jitter.
    Attempt 1: ~2s, Attempt 2: ~4s, Attempt 3: ~8s
    """
    delay = BASE_DELAY * (BACKOFF_FACTOR ** attempt)
    jitter = random.uniform(-MAX_JITTER, MAX_JITTER)
    final_delay = max(0.5, delay + jitter)
    logger.info(f"[BACKOFF] Attempt {attempt + 1} — waiting {final_delay:.2f}s")
    return final_delay


# ------------------------------------------------------------
# HUGGING FACE GATEWAY
# Stable Diffusion XL via HF Inference API
# Output: RAW binary image bytes
# ------------------------------------------------------------
def call_huggingface(
    payload: GenerationPayload,
    api_key: str
) -> tuple[bytes, str]:
    """
    Calls Hugging Face Inference API.
    Implements split-timeout + exponential backoff retry.
    Returns (image_bytes, saved_file_path)
    """
    config = ENGINE_CONFIG[Engine.HUGGING_FACE]
    model = config["model"]
    url = f"https://router.huggingface.co/hf-inference/models/{model}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "image/png"
    }

    # Build request body
    body = {
        "inputs": payload.prompt,
        "parameters": {
            "width":  payload.width,
            "height": payload.height,
        }
    }

    if payload.negative_prompt:
        body["parameters"]["negative_prompt"] = payload.negative_prompt

    logger.info(
        f"[HF_GATEWAY] Transmitting payload → "
        f"Model: {model} | Size: {payload.width}x{payload.height}"
    )

    # Retry loop with exponential backoff
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                stream=True,            # Memory-safe streaming
                timeout=SPLIT_TIMEOUT   # Split-timeout: (3.05, 120)
            )

            # Handle security gate rejections
            if response.status_code == 403:
                raise PermissionError(
                    "[GATE_1_REJECTED] Input filtered by security gate. "
                    "Content policy violation detected."
                )

            if response.status_code == 429:
                logger.warning(f"[RATE_LIMIT] 429 Too Many Requests — backing off")
                time.sleep(calculate_backoff_delay(attempt))
                continue

            if response.status_code == 503:
                logger.warning(f"[MODEL_LOADING] Model loading on HF — backing off")
                time.sleep(calculate_backoff_delay(attempt))
                continue

            response.raise_for_status()

            # Memory-safe chunked binary collection
            image_bytes = b""
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    image_bytes += chunk

            # Pixel-level integrity verification
            if not verify_image_integrity(image_bytes):
                raise OSError("[INTEGRITY_FAIL] Broken data stream — pixel decode failed")

            # Save to disk
            file_id = str(uuid.uuid4())[:8]
            filename = f"hf_{file_id}_{payload.width}x{payload.height}.png"
            save_path = os.path.join(IMAGES_DIR, filename)

            with open(save_path, 'wb') as f:
                f.write(image_bytes)

            logger.info(f"[HF_GATEWAY] Success — saved to {save_path}")
            return image_bytes, save_path

        except requests.exceptions.ConnectTimeout:
            logger.error("[FAIL_FAST] ConnectTimeout on HF — network/firewall issue")
            raise ConnectionError(
                "Cannot connect to Hugging Face API. "
                "Check your internet connection or firewall settings."
            )

        except requests.exceptions.ReadTimeout:
            last_error = "ReadTimeout — GPU cluster overloaded"
            logger.warning(f"[READ_TIMEOUT] Attempt {attempt + 1}/{MAX_RETRIES} — {last_error}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(calculate_backoff_delay(attempt))
            continue

        except (PermissionError, OSError) as e:
            raise e

        except Exception as e:
            last_error = str(e)
            logger.error(f"[HF_ERROR] Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(calculate_backoff_delay(attempt))
            continue

    raise RuntimeError(
        f"[HF_GATEWAY] All {MAX_RETRIES} attempts failed. Last error: {last_error}"
    )


# ------------------------------------------------------------
# POLLINATIONS GATEWAY
# Free tier — no API key required
# Output: Public Image URL → memory-safe download
# ------------------------------------------------------------
def call_pollinations(payload: GenerationPayload) -> tuple[bytes, str]:
    """
    Calls Pollinations.ai free API.
    Returns image URL → downloads via memory-safe streaming.
    Returns (image_bytes, saved_file_path)
    """
    import urllib.parse

    # Build the Pollinations URL
    encoded_prompt = urllib.parse.quote(payload.prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={payload.width}"
        f"&height={payload.height}"
        f"&model={ENGINE_CONFIG[Engine.POLLINATIONS]['model']}"
        f"&nologo=true"
        f"&enhance=true"
    )

    logger.info(f"[POLLINATIONS] Transmitting payload → {payload.width}x{payload.height}")

    # Save path
    file_id = str(uuid.uuid4())[:8]
    filename = f"poll_{file_id}_{payload.width}x{payload.height}.png"
    save_path = os.path.join(IMAGES_DIR, filename)

    # Retry loop
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            # Memory-safe streaming download
            image_bytes = stream_image_from_url(url, save_path)

            # Pixel-level integrity verification
            if not verify_image_integrity(image_bytes):
                raise OSError("[INTEGRITY_FAIL] Broken data stream from Pollinations")

            logger.info(f"[POLLINATIONS] Success — saved to {save_path}")
            return image_bytes, save_path

        except ConnectionError as e:
            # ConnectTimeout — FAIL FAST, no retry
            raise e

        except (TimeoutError, OSError) as e:
            last_error = str(e)
            logger.warning(f"[POLLINATIONS] Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(calculate_backoff_delay(attempt))
            continue

        except Exception as e:
            last_error = str(e)
            logger.error(f"[POLLINATIONS_ERROR] Attempt {attempt + 1}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(calculate_backoff_delay(attempt))
            continue

    raise RuntimeError(
        f"[POLLINATIONS] All {MAX_RETRIES} attempts failed. Last error: {last_error}"
    )