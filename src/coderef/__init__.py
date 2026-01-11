"""coderef - CLI tool for querying Context7 documentation API."""

__version__ = "0.1.0"

from .api_client import (
    APIError,
    AuthError,
    Context7Client,
    NotFoundError,
    RateLimitError,
)
from .config import ConfigManager, ConfigError
from .library_resolver import LibraryResolver
from .main import main
from .output import OutputFormatter

__all__ = [
    "ConfigManager",
    "ConfigError",
    "Context7Client",
    "LibraryResolver",
    "OutputFormatter",
    "APIError",
    "AuthError",
    "NotFoundError",
    "RateLimitError",
    "main",
]
