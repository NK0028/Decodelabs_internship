# ============================================================
# Project 3: Multimodal Image Generation Studio
# File: main.py — FastAPI Backend
# Role: Full-Stack Solutions Architect
# ============================================================

import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from pipeline import run_pipeline
from engines import ASPECT_RATIO_MAP, ENGINE_CONFIG, STYLE_PRESETS, Engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

app = FastAPI(
    title="Multimodal Image Generation Studio",
    description="DecodeLabs Internship — Project 3",
    version="1.0.0"
)

# Allow Next.js frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# REQUEST SCHEMA
# ------------------------------------------------------------
class GenerateRequest(BaseModel):
    prompt:          str
    engine:          str = "pollinations"
    aspect_ratio:    str = "1:1"
    negative_prompt: str = None
    style_preset:    str = "None"
    num_images:      int = 1


# ------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "online",
        "project": "Multimodal Image Generation Studio",
        "intern": "Naeem Khan",
        "company": "DecodeLabs"
    }


@app.get("/config")
def get_config():
    """Returns all frontend configuration data."""
    return {
        "aspect_ratios": {
            k: {"width": v["width"], "height": v["height"], "label": v["label"]}
            for k, v in ASPECT_RATIO_MAP.items()
        },
        "engines": {
            k.value: {
                "name": v["name"],
                "max_chars": v["max_chars"],
                "output_format": v["output_format"],
                "description": v["description"],
            }
            for k, v in ENGINE_CONFIG.items()
        },
        "style_presets": list(STYLE_PRESETS.keys()),
    }


@app.post("/generate")
async def generate_image(request: GenerateRequest):
    """
    Main generation endpoint.
    Orchestrates the full INPUT → PROCESS → OUTPUT pipeline.
    """
    logger.info(f"[API] /generate called — engine: {request.engine}")

    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        result = run_pipeline(
            prompt=request.prompt,
            engine=request.engine,
            aspect_ratio=request.aspect_ratio,
            negative_prompt=request.negative_prompt,
            style_preset=request.style_preset,
            num_images=request.num_images,
            hf_api_key=HF_API_KEY,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))

    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    except Exception as e:
        logger.error(f"[API_ERROR] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
def download_image(filename: str):
    """
    Serves generated images for download.
    Validates filename to prevent path traversal attacks.
    """
    # Security: strip any path components
    safe_filename = os.path.basename(filename)
    file_path = os.path.join("generated_images", safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found.")

    return FileResponse(
        path=file_path,
        media_type="image/png",
        filename=safe_filename,
        headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
    )


@app.get("/gallery")
def get_gallery():
    """Returns list of all generated images."""
    images_dir = "generated_images"
    if not os.path.exists(images_dir):
        return {"images": []}

    files = [
        f for f in os.listdir(images_dir)
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ]
    return {"images": sorted(files, reverse=True)}