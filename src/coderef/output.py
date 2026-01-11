"""Output formatting with Rich for coderef."""

from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax


class OutputFormatter:
    """Format coderef output using Rich for terminal display."""

    def __init__(self, theme: str = "default", code_theme: str = "monokai") -> None:
        """Initialize the OutputFormatter.

        Args:
            theme: Terminal color theme (default, dark, light)
            code_theme: Syntax highlighting theme (monokai, dracula, github-dark, nord)
        """
        self.theme = theme
        self.code_theme = code_theme
        self.console = Console()

    def format_library_header(self, library_id: str) -> Panel:
        """Format library ID as a header panel.

        Args:
            library_id: Context7 library ID (e.g., /facebook/react/v18.3.1)

        Returns:
            Rich Panel with library name and version
        """
        name, version = self._parse_library_id(library_id)
        title = f"📚 {name} ({version})"

        return Panel(
            title,
            border_style="blue",
            padding=(1, 2),
            title_align="left",
        )

    def format_code_block(self, code: str, language: str | None = None) -> Syntax:
        """Format code block with syntax highlighting.

        Args:
            code: The code to format
            language: Programming language (auto-detected if None)

        Returns:
            Rich Syntax object
        """
        if not language:
            language = "text"

        return Syntax(
            code,
            language,
            theme=self.code_theme,
            line_numbers=True,
        )

    def format_markdown(self, text: str) -> Markdown:
        """Format text as Markdown.

        Args:
            text: Markdown text to format

        Returns:
            Rich Markdown object
        """
        return Markdown(text)

    def format_error(self, message: str, emoji: str = "❌") -> Panel:
        """Format error message as a panel.

        Args:
            message: Error message to display
            emoji: Emoji for visual emphasis

        Returns:
            Rich Panel with error message
        """
        return Panel(
            f"{emoji} {message}",
            border_style="red",
            padding=(1, 2),
        )

    def format_info(self, message: str, emoji: str = "ℹ️") -> Panel:
        """Format info message as a panel.

        Args:
            message: Info message to display
            emoji: Emoji for visual emphasis

        Returns:
            Rich Panel with info message
        """
        return Panel(
            f"{emoji} {message}",
            border_style="cyan",
            padding=(1, 2),
        )

    def format_warning(self, message: str, emoji: str = "⚠️") -> Panel:
        """Format warning message as a panel.

        Args:
            message: Warning message to display
            emoji: Emoji for visual emphasis

        Returns:
            Rich Panel with warning message
        """
        return Panel(
            f"{emoji} {message}",
            border_style="yellow",
            padding=(1, 2),
        )

    def format_response(self, context: dict, library_id: str) -> None:
        """Format and display full API response.

        Args:
            context: API response dict with 'context' and 'examples' keys
            library_id: Context7 library ID for header
        """
        header = self.format_library_header(library_id)
        self.console.print(header)
        self.console.print()

        explanation = context.get("context", "")
        if explanation:
            markdown = self.format_markdown(explanation)
            self.console.print(markdown)
            self.console.print()

        examples = context.get("examples", [])
        for i, example in enumerate(examples):
            if i > 0:
                self.console.print("─" * self.console.width, style="dim")
                self.console.print()

            code = example.get("code", "")
            language = example.get("language", "text")

            if code:
                syntax = self.format_code_block(code, language)
                self.console.print(syntax)
                self.console.print()

    def print(self, *args, **kwargs) -> None:
        """Print using the Rich console.

        Args:
            *args: Arguments to pass to console.print
            **kwargs: Keyword arguments to pass to console.print
        """
        self.console.print(*args, **kwargs)

    def print_error(self, message: str) -> None:
        """Print formatted error message.

        Args:
            message: Error message to display
        """
        panel = self.format_error(message)
        self.console.print(panel)

    def print_info(self, message: str) -> None:
        """Print formatted info message.

        Args:
            message: Info message to display
        """
        panel = self.format_info(message)
        self.console.print(panel)

    def print_warning(self, message: str) -> None:
        """Print formatted warning message.

        Args:
            message: Warning message to display
        """
        panel = self.format_warning(message)
        self.console.print(panel)

    def _parse_library_id(self, library_id: str) -> tuple[str, str]:
        """Parse library ID into name and version.

        Args:
            library_id: Context7 library ID (e.g., /facebook/react/v18.3.1)

        Returns:
            Tuple of (name, version)
        """
        if "/v" in library_id:
            name_part, version = library_id.split("/v", 1)
            version = f"v{version}"
        else:
            name_part = library_id
            version = "latest"

        name = name_part.lstrip("/")
        return name, version
