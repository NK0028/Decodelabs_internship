"""
Phase 1: Input & Payload Capture.

Streams a raw source code file into memory as an untrusted string payload,
exactly as the "Input Ingestion Triage" diagram specifies: FileNotFoundError,
PermissionError, and UnicodeDecodeError are all handled explicitly so the
pipeline never crashes on a bad path or a binary/mis-encoded file.
"""
from pathlib import Path
from typing import Tuple

from config import SUPPORTED_EXTENSIONS


class FileIngestionError(Exception):
    """Raised for any failure during file ingestion. Always human-readable."""


def ingest_file(filepath: str) -> Tuple[str, str]:
    """
    Read a source code file into memory as a raw string payload.

    Returns:
        (raw_code, language) — language is the tag used later for
        syntax highlighting and for the model's language-specific analysis.

    Raises:
        FileIngestionError with a clear, user-facing explanation.
    """
    path = Path(filepath)

    if not path.exists():
        raise FileIngestionError(
            f"File not found: '{filepath}'. Double-check the path and try again."
        )

    if path.is_dir():
        raise FileIngestionError(f"'{filepath}' is a directory, not a file.")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS.keys()))
        raise FileIngestionError(
            f"Unsupported file type '{ext or '(none)'}'. Supported types: {supported}"
        )

    try:
        raw_code = path.read_text(encoding="utf-8")
    except PermissionError:
        raise FileIngestionError(f"Permission denied while reading '{filepath}'.")
    except UnicodeDecodeError:
        # Fallback codec before giving up — protects against non-UTF-8 source files
        try:
            raw_code = path.read_text(encoding="latin-1")
        except Exception:
            raise FileIngestionError(
                f"'{filepath}' contains unsupported encoding or binary data and cannot be read as text."
            )

    if not raw_code.strip():
        raise FileIngestionError(f"'{filepath}' is empty — nothing to review.")

    return raw_code, SUPPORTED_EXTENSIONS[ext]
