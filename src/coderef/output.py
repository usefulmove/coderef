"""Output formatting with Rich for coderef."""

from rich.console import Console
from rich.markdown import Markdown

# Shared console instance
console = Console()


def print_markdown(text: str) -> None:
    """Print text as formatted Markdown.

    Args:
        text: Markdown text to format and print
    """
    console.print(Markdown(text))


def print_error(message: str) -> None:
    """Print an error message.

    Args:
        message: Error message to display
    """
    console.print(f"[red]Error:[/red] {message}")


def print_info(message: str) -> None:
    """Print an info message.

    Args:
        message: Info message to display
    """
    console.print(f"[cyan]Info:[/cyan] {message}")
