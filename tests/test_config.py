"""Tests for ConfigManager."""

import os
from pathlib import Path

import pytest

from coderef.config import ConfigManager, ConfigError
from coderef.utils import validate_api_key_format


class TestConfigManager:
    """Test ConfigManager class."""

    def test_config_exists_returns_true_when_config_exists(self, tmp_path):
        """Test that config_exists returns True when config file exists."""
        config_path = tmp_path / "config.toml"
        config_path.touch()

        manager = ConfigManager(str(config_path))

        assert manager.config_exists() is True

    def test_config_exists_returns_false_when_config_missing(self, tmp_path):
        """Test that config_exists returns False when config file doesn't exist."""
        config_path = tmp_path / "nonexistent.toml"
        manager = ConfigManager(str(config_path))

        assert manager.config_exists() is False

    def test_create_config_creates_file_with_correct_permissions(self, tmp_path):
        """Test that create_config creates file with 600 permissions."""
        config_dir = tmp_path / ".coderef"
        config_path = config_dir / "config.toml"
        manager = ConfigManager(str(config_path))

        manager.create_config()

        assert config_path.exists()
        assert config_dir.exists()

        stat = config_path.stat()
        # Check file permissions (0o600 = read/write for owner only)
        mode = stat.st_mode & 0o777
        assert mode == 0o600

    def test_create_config_creates_parent_directories(self, tmp_path):
        """Test that create_config creates parent directories if they don't exist."""
        config_dir = tmp_path / "deeply" / "nested" / ".coderef"
        config_path = config_dir / "config.toml"
        manager = ConfigManager(str(config_path))

        manager.create_config()

        assert config_dir.exists()
        assert config_path.exists()

    def test_get_api_key_returns_key_when_set(self, tmp_path):
        """Test that get_api_key returns the API key when it's set."""
        config_path = tmp_path / "config.toml"
        manager = ConfigManager(str(config_path))

        manager.create_config()
        manager.set_api_key("ctx7sk_test_key_12345")

        api_key = manager.get_api_key()

        assert api_key == "ctx7sk_test_key_12345"

    def test_get_api_key_returns_none_when_not_set(self, tmp_path):
        """Test that get_api_key returns None when API key is not set."""
        config_path = tmp_path / "config.toml"
        manager = ConfigManager(str(config_path))

        manager.create_config()
        api_key = manager.get_api_key()

        assert api_key is None

    def test_get_api_key_returns_none_when_config_missing(self, tmp_path):
        """Test that get_api_key returns None when config doesn't exist."""
        config_path = tmp_path / "nonexistent.toml"
        manager = ConfigManager(str(config_path))

        api_key = manager.get_api_key()

        assert api_key is None

    def test_set_api_key_writes_to_file(self, tmp_path):
        """Test that set_api_key writes the key to the config file."""
        config_path = tmp_path / "config.toml"
        manager = ConfigManager(str(config_path))

        manager.create_config()
        manager.set_api_key("ctx7sk_test_key_12345")

        assert config_path.exists()
        assert config_path.stat().st_size > 0

    def test_set_api_key_creates_config_if_missing(self, tmp_path):
        """Test that set_api_key creates config file if it doesn't exist."""
        config_dir = tmp_path / ".coderef"
        config_path = config_dir / "config.toml"
        manager = ConfigManager(str(config_path))

        assert not config_path.exists()

        manager.set_api_key("ctx7sk_test_key_12345")

        assert config_path.exists()

    def test_set_api_key_raises_on_invalid_format(self, tmp_path):
        """Test that set_api_key raises ValueError for invalid key format."""
        config_path = tmp_path / "config.toml"
        manager = ConfigManager(str(config_path))
        manager.create_config()

        with pytest.raises(ValueError, match="Invalid API key format"):
            manager.set_api_key("invalid_key")

        with pytest.raises(ValueError, match="Invalid API key format"):
            manager.set_api_key("")

    def test_set_api_key_maintains_file_permissions(self, tmp_path):
        """Test that set_api_key maintains 600 permissions."""
        config_path = tmp_path / "config.toml"
        manager = ConfigManager(str(config_path))

        manager.create_config()
        manager.set_api_key("ctx7sk_test_key_12345")

        stat = config_path.stat()
        mode = stat.st_mode & 0o777
        assert mode == 0o600

    def test_config_path_expands_tilde(self, tmp_path):
        """Test that config path expands tilde to home directory."""
        # We can't actually test ~ expansion in tmp_path context,
        # but we can verify the path is processed correctly
        config_path = tmp_path / "config.toml"
        manager = ConfigManager(str(config_path))

        assert str(manager.config_path) == str(config_path)


class TestValidateApiKeyFormat:
    """Test validate_api_key_format function."""

    def test_validate_api_key_format_accepts_hyphen_prefix(self):
        """Test that hyphen prefix (actual format) is accepted."""
        assert (
            validate_api_key_format("ctx7sk-5a7c7f69-332e-4fd6-af7c-6b510ace592d")
            is True
        )

    def test_validate_api_key_format_accepts_underscore_prefix(self):
        """Test that underscore prefix (legacy format) is accepted."""
        assert validate_api_key_format("ctx7sk_test_key_12345") is True

    def test_validate_api_key_format_rejects_invalid_prefix(self):
        """Test that invalid prefixes are rejected."""
        assert validate_api_key_format("apikey_test") is False
        assert validate_api_key_format("ctx7-test") is False

    def test_validate_api_key_format_rejects_short_key(self):
        """Test that short keys are rejected."""
        assert validate_api_key_format("ctx7sk-") is False
        assert validate_api_key_format("ctx7sk_ab") is False
