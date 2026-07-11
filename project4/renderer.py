"""
Phase 3: Deterministic Markdown Rendering (The Rendering Engine).

Takes the validated ReviewResult and renders it with IDE-quality,
color-mapped syntax highlighting directly in the terminal — solving
the "Plain Text Problem" from raw API output.
"""
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

from validator import ReviewResult

console = Console()


def render_review(result: ReviewResult, source_filename: str) -> None:
    console.rule(f"[bold cyan]Code Review Report — {source_filename}[/bold cyan]")
    console.print()

    console.print(Panel.fit("[bold white]BUG REPORT[/bold white]", style="red"))
    console.print(Markdown(result.bug_report))
    console.print()

    console.print(Panel.fit("[bold white]REFACTORED CODE[/bold white]", style="green"))
    syntax = Syntax(
        result.refactored_code,
        result.code_language,
        theme="monokai",
        line_numbers=True,
        word_wrap=True,
    )
    console.print(syntax)
    console.print()
    console.rule()
