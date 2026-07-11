#!/usr/bin/env python3
"""
Intelligent Code Reviewer & Explainer
DecodeLabs Generative AI Internship — Project 4 (Optional Mastery Phase)

An autonomous, AI-powered gatekeeper: ingests a raw source file, forces a
Gemini model into a strict analytical persona, validates the structured
output, and renders a bug report + refactored code with syntax highlighting.

Usage:
    python main.py path/to/file.py
    python main.py path/to/file.js --save review.md
    python main.py path/to/file.java --model gemini-2.5-pro
"""
import argparse
import sys
from pathlib import Path

from rich.console import Console

from file_handler import ingest_file, FileIngestionError
from reviewer import CodeReviewer, ReviewerAPIError
from validator import MalformedResponseError
from renderer import render_review

console = Console()


def save_report(result, out_path: str) -> None:
    content = (
        f"## BUG_REPORT\n{result.bug_report}\n\n"
        f"## REFACTORED_CODE\n```{result.code_language}\n{result.refactored_code}\n```\n"
    )
    Path(out_path).write_text(content, encoding="utf-8")
    console.print(f"[green]✔ Report saved to {out_path}[/green]")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code-reviewer",
        description="Analyze a source file, identify bugs, and generate an optimized, refactored version.",
    )
    parser.add_argument("filepath", help="Path to a .py, .js, or .java source file")
    parser.add_argument("--save", metavar="OUTPUT.md", help="Save the report as a Markdown file")
    parser.add_argument("--model", help="Override the Gemini model (default: gemini-2.5-flash)")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()

    # --- Phase 1: Input & Payload Capture ---
    try:
        raw_code, language = ingest_file(args.filepath)
    except FileIngestionError as e:
        console.print(f"[bold red]Ingestion Error:[/bold red] {e}")
        return 1

    # --- Phase 2: Context Orchestration ---
    try:
        reviewer = CodeReviewer(model=args.model)
    except ReviewerAPIError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        return 1

    try:
        with console.status("[cyan]Analyzing code with Gemini...[/cyan]", spinner="dots"):
            result = reviewer.review(raw_code, language)
    except ReviewerAPIError as e:
        console.print(f"[bold red]API Error:[/bold red] {e}")
        return 1
    except MalformedResponseError as e:
        console.print(f"[bold red]Validation Error:[/bold red] {e}")
        return 1

    # --- Phase 3: Deterministic Markdown Rendering ---
    render_review(result, Path(args.filepath).name)

    if args.save:
        save_report(result, args.save)

    return 0


if __name__ == "__main__":
    sys.exit(main())
