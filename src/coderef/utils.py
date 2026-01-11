"""Utility functions for coderef."""

import re


def validate_api_key_format(api_key: str) -> bool:
    """Validate that API key starts with ctx7sk_ or ctx7sk- prefix.

    Args:
        api_key: The API key to validate

    Returns:
        True if key format is valid, False otherwise
    """
    return (api_key.startswith("ctx7sk_") or api_key.startswith("ctx7sk-")) and len(
        api_key
    ) > 10
