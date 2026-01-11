"""Main CLI entry point for coderef."""

import os
import sys

import click

from .api_client import (
    APIError,
    AuthError,
    Context7Client,
    NotFoundError,
    RateLimitError,
)
from .config import ConfigError, ConfigManager
from .library_resolver import LibraryResolver
from .output import OutputFormatter
from .utils import validate_api_key_format


@click.command()
@click.argument("question", type=str, required=False)
@click.option(
    "--library",
    "-l",
    type=str,
    help="Explicitly specify library (e.g., /facebook/react)",
)
@click.option(
    "--tokens",
    "-t",
    type=int,
    default=5000,
    show_default=True,
    help="Token limit for context (1000-50000)",
)
@click.option("--version", "-v", type=str, help="Library version (e.g., v18.3.1)")
@click.option("--init", is_flag=True, help="Initialize configuration")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.option("--skip-library-detect", is_flag=True, help="Skip library auto-detection")
def main(
    question: str | None,
    library: str | None,
    tokens: int,
    version: str | None,
    init: bool,
    debug: bool,
    skip_library_detect: bool,
) -> None:
    """Query Context7 for code documentation.

    QUESTION: Your question about the library or framework

    Examples:
        coderef "How do I use React hooks?"
        coderef "How do I create middleware?" --library /vercel/next.js
        coderef "How do I use app router?" --library /vercel/next.js --version v15.0.0
        coderef "C++ lambda functions" --skip-library-detect
    """
    formatter = OutputFormatter()

    if os.environ.get("DEBUG", "").lower() == "true":
        debug = True

    try:
        if init:
            _run_init_flow(formatter, debug)
            return

        if not question:
            formatter.print_error(
                "Please provide a question. Use [bold]--help[/bold] for usage."
            )
            sys.exit(1)

        _validate_tokens(tokens)

        config_manager = ConfigManager()
        api_key = os.environ.get("CONTEXT7_API_KEY")

        if debug:
            if api_key:
                formatter.print(
                    "[DEBUG] Using API key from CONTEXT7_API_KEY environment variable"
                )
            else:
                formatter.print("[DEBUG] Falling back to config file...")

        if not api_key:
            if not config_manager.config_exists():
                formatter.print_error(
                    "Configuration not found. Run [bold]coderef --init[/bold] to set up."
                )
                sys.exit(1)

            api_key = config_manager.get_api_key()

            if not api_key:
                formatter.print_error(
                    "API key not found. Run [bold]coderef --init[/bold] to set up."
                )
                sys.exit(1)

            if debug:
                formatter.print("[DEBUG] Using API key from ~/.coderef/config.toml")

        api_client = Context7Client(api_key)
        resolver = LibraryResolver(api_client)

        library_id = _resolve_library(
            formatter, resolver, question, library, version, skip_library_detect, debug
        )

        # library_id is None if skipped or not found (and we want to try generic query)
        # But _resolve_library raises error if not found and not skipped.
        # So here, library_id is either a string OR None (if skipped).

        context = api_client.get_context(library_id, question, tokens)
        formatter.format_response(context, library_id or "Auto-detected")

    except (ConfigError, APIError, ValueError) as e:
        formatter.print_error(str(e))
        sys.exit(1)
    except AuthError:
        formatter.print_error(
            "Invalid API key. Run [bold]coderef --init[/bold] to update."
        )
        sys.exit(1)
    except RateLimitError:
        formatter.print_error("Rate limit exceeded. Please wait before retrying.")
        sys.exit(1)
    except NotFoundError:
        formatter.print_error(
            "Library not found. Check the [bold]--library[/bold] flag."
        )
        sys.exit(1)
    except Exception as e:
        formatter.print_error(f"An unexpected error occurred: {e}")
        sys.exit(1)


def _run_init_flow(formatter: OutputFormatter, debug: bool = False) -> None:
    """Run the initialization flow.

    Args:
        formatter: OutputFormatter for messages
        debug: Enable debug output
    """
    formatter.print("Welcome to coderef!")
    formatter.print("Let's set up your Context7 API key.")
    formatter.print("Get your free API key at: https://context7.com/dashboard")
    formatter.print()

    if debug:
        formatter.print("[DEBUG] Checking for CONTEXT7_API_KEY environment variable...")

    try:
        api_key = os.environ.get("CONTEXT7_API_KEY")

        if debug:
            if api_key:
                formatter.print(
                    f"[DEBUG] Environment variable found: {api_key[:10]}...{api_key[-4:]}"
                )
            else:
                formatter.print("[DEBUG] Environment variable not found")

        if api_key:
            if validate_api_key_format(api_key):
                formatter.print_info(
                    "Using API key from CONTEXT7_API_KEY environment variable"
                )
            else:
                formatter.print_error(
                    "Invalid API key format in CONTEXT7_API_KEY.\n"
                    "Key must start with 'ctx7sk-' or 'ctx7sk_'.\n\n"
                    "Verify your key: echo $CONTEXT7_API_KEY"
                )
                sys.exit(1)
        else:
            formatter.print_info(
                "Environment variable CONTEXT7_API_KEY not found.\n"
                "You can set it in your shell profile or enter it below."
            )
            api_key = click.prompt(
                "Enter your Context7 API key", hide_input=True, confirmation_prompt=True
            )

            if not validate_api_key_format(api_key):
                formatter.print_error(
                    "Invalid API key format. Key must start with 'ctx7sk-' or 'ctx7sk_'."
                )
                sys.exit(1)

        config_manager = ConfigManager()
        config_manager.set_api_key(api_key)

        if debug:
            from_env_var = os.environ.get("CONTEXT7_API_KEY") == api_key
            source = (
                "CONTEXT7_API_KEY environment variable"
                if from_env_var
                else "interactive prompt"
            )
            formatter.print(f"[DEBUG] API key saved from: {source}")

        formatter.print("✅ API key saved successfully!")
        formatter.print("You can now use coderef to query documentation.")
        formatter.print()
        formatter.print("Example:")
        formatter.print('  coderef "How do I use React hooks?"')

    except click.exceptions.Abort:
        formatter.print_error("Initialization cancelled.")
        sys.exit(1)
    except ConfigError as e:
        formatter.print_error(f"Configuration error: {e}")
        sys.exit(1)


def _validate_tokens(tokens: int) -> None:
    """Validate token limit.

    Args:
        tokens: Token limit to validate

    Raises:
        ValueError: If tokens outside valid range
    """
    if not 1000 <= tokens <= 50000:
        raise ValueError("Tokens must be between 1000 and 50000")


def _resolve_library(
    formatter: OutputFormatter,
    resolver: LibraryResolver,
    question: str,
    library: str | None,
    version: str | None,
    skip_detect: bool = False,
    debug: bool = False,
) -> str | None:
    """Resolve library ID from input or auto-detect.

    Args:
        formatter: OutputFormatter for messages
        resolver: LibraryResolver for detection
        question: User's question
        library: Explicit library ID (if provided)
        version: Library version (if provided)
        skip_detect: Skip library auto-detection
        debug: Enable debug output

    Returns:
        Context7 library ID, or None if skipping/not found but skipped

    Raises:
        ValueError: If library cannot be resolved and not skipped
    """
    if library:
        library_id = library

        if version:
            library_id = f"{library_id}/{version}"

        formatter.print_info(f"Using library: {library_id}")
        return library_id

    if skip_detect:
        if debug:
            formatter.print("[DEBUG] Skipping library detection per flag")
        return None

    library_id, confidence = resolver.resolve_from_question(question)

    if not library_id:
        if not skip_detect:
            formatter.print_error(
                "Could not detect library. Use [bold]--library[/bold] to specify."
            )
            formatter.print_info(
                "Tip: Use [bold]--skip-library-detect[/bold] to let Context7 handle library resolution for generic queries."
            )
            raise ValueError("Library detection failed")
        return None

    if confidence >= 0.8:
        formatter.print_info(f"Using library: {library_id}")
    elif confidence >= 0.5:
        formatter.print_warning(
            f"Using library: {library_id} (confidence: {confidence:.2f})"
        )
    else:
        # Low confidence
        if not skip_detect:
            formatter.print_error(
                f"Low confidence library match: {library_id} (confidence: {confidence:.2f}). "
                "Use [bold]--library[/bold] to specify explicitly."
            )
            formatter.print_info(
                "Tip: Use [bold]--skip-library-detect[/bold] to let Context7 handle library resolution."
            )
            raise ValueError("Low confidence library match")
        return None

    return library_id


if __name__ == "__main__":
    main()
