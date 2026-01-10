"""coderef - Succinct code example agent powered by Claude and Context7."""

__version__ = "0.2.0"

from .agent import query, SYSTEM_PROMPT
from .main import main
from .output import print_markdown, print_error, print_info

__all__ = [
    "query",
    "SYSTEM_PROMPT",
    "main",
    "print_markdown",
    "print_error",
    "print_info",
]
