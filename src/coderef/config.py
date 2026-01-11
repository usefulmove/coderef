"""Configuration management for coderef."""

import os
from pathlib import Path

import toml

from .utils import validate_api_key_format


class ConfigError(Exception):
    """Configuration-related errors."""

    pass


class ConfigManager:
    """Manages coderef configuration file."""

    def __init__(self, config_path: str = "~/.coderef/config.toml"):
        """Initialize ConfigManager with config file path.

        Args:
            config_path: Path to config file (supports ~ expansion)
        """
        self.config_path = Path(config_path).expanduser()
        self.config_dir = self.config_path.parent

    def config_exists(self) -> bool:
        """Check if config file exists.

        Returns:
            True if config file exists, False otherwise
        """
        return self.config_path.exists()

    def create_config(self) -> None:
        """Create config file and directory if needed.

        Raises:
            ConfigError: If unable to create config directory or file
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path.touch(exist_ok=True)
            os.chmod(self.config_path, 0o600)
        except OSError as e:
            raise ConfigError(f"Failed to create config file: {e}") from e

    def get_api_key(self) -> str | None:
        """Get API key from config.

        Returns:
            API key string if found, None otherwise

        Raises:
            ConfigError: If config file is invalid
        """
        if not self.config_exists():
            return None

        try:
            config = toml.load(self.config_path)
            return config.get("context7", {}).get("api_key")
        except Exception as e:
            raise ConfigError(f"Failed to read config file: {e}") from e

    def set_api_key(self, api_key: str) -> None:
        """Set API key in config file.

        Args:
            api_key: The API key to store

        Raises:
            ConfigError: If config file doesn't exist or is invalid
            ValueError: If API key format is invalid
        """
        if not validate_api_key_format(api_key):
            raise ValueError("Invalid API key format. Key must start with 'ctx7sk_'")

        if not self.config_exists():
            self.create_config()

        try:
            if self.config_path.stat().st_size > 0:
                config = toml.load(self.config_path)
            else:
                config = {}

            if "context7" not in config:
                config["context7"] = {}

            config["context7"]["api_key"] = api_key

            with open(self.config_path, "w") as f:
                toml.dump(config, f)

            os.chmod(self.config_path, 0o600)
        except Exception as e:
            raise ConfigError(f"Failed to write config file: {e}") from e
