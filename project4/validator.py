"""
Structured Output Validation.

Enforces the IPO contract from the "Structured Output Validation" slide:
if the model fails to return both explicit section headers in the right
order with a valid fenced code block, the response is rejected outright
so a malformed report never reaches the terminal or a CI pipeline.
"""
import re
from dataclasses import dataclass

from config import BUG_REPORT_HEADER, REFACTORED_CODE_HEADER


class MalformedResponseError(Exception):
    """Raised when the model's response breaks the structured output contract."""


@dataclass
class ReviewResult:
    bug_report: str
    refactored_code: str
    code_language: str
    raw_response: str


CODE_BLOCK_PATTERN = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)


def validate_and_parse(response_text: str, fallback_language: str) -> ReviewResult:
    """Parse and strictly validate a model response against the IPO contract."""
    if BUG_REPORT_HEADER not in response_text or REFACTORED_CODE_HEADER not in response_text:
        raise MalformedResponseError(
            "Model response is missing one or both required section headers "
            f"('{BUG_REPORT_HEADER}', '{REFACTORED_CODE_HEADER}'). Rejecting to protect the pipeline."
        )

    bug_idx = response_text.index(BUG_REPORT_HEADER)
    code_idx = response_text.index(REFACTORED_CODE_HEADER)

    if code_idx < bug_idx:
        raise MalformedResponseError(
            "Sections are out of order (REFACTORED_CODE appeared before BUG_REPORT)."
        )

    bug_section = response_text[bug_idx + len(BUG_REPORT_HEADER):code_idx].strip()
    code_section = response_text[code_idx + len(REFACTORED_CODE_HEADER):].strip()

    match = CODE_BLOCK_PATTERN.search(code_section)
    if not match:
        raise MalformedResponseError(
            "REFACTORED_CODE section does not contain a valid fenced code block."
        )

    language = match.group(1) or fallback_language
    code = match.group(2).strip()

    if not bug_section:
        raise MalformedResponseError("BUG_REPORT section is empty.")

    if not code:
        raise MalformedResponseError("REFACTORED_CODE block is empty.")

    return ReviewResult(
        bug_report=bug_section,
        refactored_code=code,
        code_language=language,
        raw_response=response_text,
    )
