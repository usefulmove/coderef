"""CLI entry point for coderef."""

import os
import sys

import anthropic
import click
from rich.console import Console
from rich.markdown import Markdown

from .agent import query

console = Console()


@click.command()
@click.argument("question", type=str)
@click.option("--tokens", "-t", type=int, default=2000, help="Max response tokens")
def main(question: str, tokens: int) -> None:
    """Get succinct code examples for programming queries.

    Examples:
        coderef "modern C++ fold_left"
        coderef "Rust iterators filter map"
        coderef "Python asyncio gather"
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]Error:[/red] Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    try:
        result = query(question, max_tokens=tokens)
        console.print(Markdown(result))
    except anthropic.APIError as e:
        console.print(f"[red]API Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
