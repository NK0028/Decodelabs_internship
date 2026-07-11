"""
Phase 2: Context Orchestration.

Wraps the Google GenAI client, locks in the persona via system_instruction,
and retries automatically if the model ever breaks the structured output
contract (rare, but LLMs are non-deterministic by nature — this is the
"Conversational vs. Analytical Modalities" trade-off made robust).
"""
import time

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_INSTRUCTION
from validator import validate_and_parse, MalformedResponseError, ReviewResult


class ReviewerAPIError(Exception):
    """Raised for API-level failures: missing/invalid key, network, quota, etc."""


class CodeReviewer:
    """A locked-down, single-purpose Gemini client for code auditing."""

    def __init__(self, api_key: str = None, model: str = None):
        key = api_key or GEMINI_API_KEY
        if not key:
            raise ReviewerAPIError(
                "No API key found. Set GEMINI_API_KEY in your environment or a .env file."
            )
        self.client = genai.Client(api_key=key)
        self.model = model or GEMINI_MODEL

    def review(self, raw_code: str, language: str, max_retries: int = 2) -> ReviewResult:
        """
        Send the raw code payload to the model and return a validated,
        structured ReviewResult. Retries on malformed (non-contract-compliant)
        output before finally raising.
        """
        prompt = (
            f"Analyze the following {language} source file.\n\n"
            f"```{language}\n{raw_code}\n```"
        )

        last_error: Exception = None
        for attempt in range(1, max_retries + 2):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.2,
                    ),
                )
            except Exception as e:
                raise ReviewerAPIError(f"Gemini API call failed: {e}") from e

            text = (response.text or "").strip()

            try:
                return validate_and_parse(text, fallback_language=language)
            except MalformedResponseError as e:
                last_error = e
                if attempt <= max_retries:
                    time.sleep(1)
                    continue
                raise

        raise last_error
