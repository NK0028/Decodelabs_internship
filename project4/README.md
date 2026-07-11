# Intelligent Code Reviewer & Explainer

**DecodeLabs Generative AI Internship — Project 4 (Optional Mastery Phase)**

An autonomous, AI-powered code gatekeeper. It ingests a raw `.py`, `.js`, or `.java`
file, locks a Gemini model into a strict analytical persona, and returns a
severity-ordered bug report plus a fully refactored, drop-in replacement —
rendered with IDE-quality syntax highlighting directly in your terminal.

```
$ python main.py examples/sample_buggy.py

─────────────── Code Review Report — sample_buggy.py ───────────────
╭ BUG REPORT ╮
 • find_user() iterates range(len(users) + 1), causing an
   IndexError on the last loop iteration.
 • calculate_average() divides by zero when `numbers` is empty.
 • Cache.get() raises a raw KeyError instead of a controlled miss.
 ...
╭ REFACTORED CODE ╮
  1  def process_data(data):
  2      result = []
  3      for item in data:
  ...
```

## Why this exists

Human code review doesn't scale: reviewers rush through large PRs, apply
inconsistent standards, and take hours to respond. This tool applies the
same rigor to every commit, in milliseconds, every time.

## Architecture — the IPO Pipeline

The system follows a strict **Input → Processing → Output** pipeline, exactly
as scoped for this project:

```
1. Local System        2. API Client              3. Validation            4. Terminal
   file_handler.py  →     reviewer.py            →   validator.py        →   renderer.py
   Reads the raw          Merges the payload with     Rejects any response     Renders color-coded
   source file into a     the locked persona/         missing the required     Markdown + syntax-
   string buffer, with    system instruction and       ## BUG_REPORT /          highlighted code via
   explicit handling of   calls the Gemini API.        ## REFACTORED_CODE       rich.
   FileNotFoundError,                                  contract.
   PermissionError, and
   UnicodeDecodeError.
```

| File | Responsibility |
|---|---|
| `config.py` | Constants, supported extensions, and the locked **system instruction** (persona) |
| `file_handler.py` | **Phase 1** — safe file ingestion, all I/O failure modes handled |
| `reviewer.py` | **Phase 2** — Gemini API client, retries automatically on malformed output |
| `validator.py` | **Phase 3a** — strict structured-output contract enforcement |
| `renderer.py` | **Phase 3b** — `rich`-powered terminal rendering with syntax highlighting |
| `main.py` | CLI entry point wiring all four phases together |

### The core design decision: taming a conversational model

By default, an LLM chats — it greets you, hedges, and wraps code in prose.
None of that survives contact with a script that needs to parse the output.
`config.py` locks the model into an **Analytical Gatekeeper** persona via a
`system_instruction`, and `validator.py` treats that contract as non-negotiable:
if the model ever returns `## BUG_REPORT`/`## REFACTORED_CODE` out of order,
missing, or without a valid fenced code block, the response is rejected and
retried rather than silently passed downstream.

## Setup

```bash
git clone <your-repo-url>
cd code_reviewer
pip install -r requirements.txt
cp .env.example .env   # then add your GEMINI_API_KEY
```

Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

## Usage

```bash
# Review a file, print to terminal
python main.py examples/sample_buggy.py

# Also save the report as Markdown
python main.py examples/sample_buggy.js --save review.md

# Use a specific Gemini model
python main.py examples/sample_buggy.java --model gemini-2.5-pro
```

Three intentionally-buggy sample files are included under `examples/` for a
quick demo — one each for Python, JavaScript, and Java.

## Testing

The structured-output validator is fully unit-tested and requires **no API
key or network access** to run:

```bash
pytest tests/ -v
```

```
7 passed in 0.02s
```

## Key skills demonstrated

- **Code-as-context management** — treating raw source as an untrusted string
  payload with strict I/O error handling.
- **Structured output enforcement** — a hard contract between the model and
  the pipeline, with automatic retry on violation.
- **Prompt engineering / persona locking** — overriding a model's default
  conversational behavior with a `system_instruction`.
- **Deterministic rendering** — turning raw Markdown into IDE-quality,
  color-mapped terminal output.

## Roadmap ideas

- [ ] Batch mode: review an entire directory / PR diff at once
- [ ] GitHub Action that comments the bug report directly on a pull request
- [ ] Support for additional languages (Go, TypeScript, C++)
- [ ] JSON output mode for CI pipeline integration

---

Built by **Naeem Khan** as part of the DecodeLabs Generative AI Internship (Batch 2026).
