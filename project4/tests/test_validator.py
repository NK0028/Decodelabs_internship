"""
Unit tests for validator.py — pure logic, no API key or network required.
Run with: pytest tests/
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from validator import validate_and_parse, MalformedResponseError


VALID_RESPONSE = """## BUG_REPORT
- `find_user` uses an off-by-one range causing an IndexError.
- `calculate_average` divides by zero when `numbers` is empty.

## REFACTORED_CODE
```python
def find_user(users, target_id):
    for user in users:
        if user["id"] == target_id:
            return user
    return None
```
"""


def test_valid_response_parses_correctly():
    result = validate_and_parse(VALID_RESPONSE, fallback_language="python")
    assert "off-by-one" in result.bug_report
    assert "def find_user" in result.refactored_code
    assert result.code_language == "python"


def test_missing_bug_report_header_raises():
    bad = "## REFACTORED_CODE\n```python\nprint('hi')\n```"
    with pytest.raises(MalformedResponseError):
        validate_and_parse(bad, fallback_language="python")


def test_missing_refactored_code_header_raises():
    bad = "## BUG_REPORT\n- something is wrong"
    with pytest.raises(MalformedResponseError):
        validate_and_parse(bad, fallback_language="python")


def test_sections_out_of_order_raises():
    bad = (
        "## REFACTORED_CODE\n```python\nprint('hi')\n```\n\n"
        "## BUG_REPORT\n- issue here"
    )
    with pytest.raises(MalformedResponseError):
        validate_and_parse(bad, fallback_language="python")


def test_missing_code_fence_raises():
    bad = "## BUG_REPORT\n- issue here\n\n## REFACTORED_CODE\nno fenced block here"
    with pytest.raises(MalformedResponseError):
        validate_and_parse(bad, fallback_language="python")


def test_empty_bug_report_raises():
    bad = "## BUG_REPORT\n\n## REFACTORED_CODE\n```python\nprint(1)\n```"
    with pytest.raises(MalformedResponseError):
        validate_and_parse(bad, fallback_language="python")


def test_falls_back_to_source_language_when_untagged():
    resp = "## BUG_REPORT\n- none\n\n## REFACTORED_CODE\n```\nprint(1)\n```"
    result = validate_and_parse(resp, fallback_language="python")
    assert result.code_language == "python"
