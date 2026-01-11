# 001 Initial CLI Structure and Config Management

## Goal
Set up the project structure, implement config management, and create a basic CLI skeleton with `--init` command.

## Acceptance Criteria

- [x] Project directory structure matches ARCHITECTURE.md
- [x] `pyproject.toml` and `requirements.txt` are created with all dependencies
- [x] `ConfigManager` class can read/write config from `~/.coderef/config.toml`
- [x] `--init` command prompts for API key and saves it to config
- [x] `--init` command validates API key with Context7 before saving
- [x] CLI shows helpful error when config doesn't exist
- [x] All code follows STANDARDS.md conventions

## Context Scope

**Write:**
- `src/__init__.py`
- `src/coderef.py`
- `src/config.py`
- `src/utils.py`
- `tests/test_config.py`
- `pyproject.toml`
- `requirements.txt`
- `README.md`
- `.gitignore`

**Read:**
- `docs/core/ARCHITECTURE.md`
- `docs/core/STANDARDS.md`

**Exclude:**
- `src/api_client.py` (Story 002)
- `src/library_resolver.py` (Story 002)
- `src/output.py` (Story 002)
- `tests/test_api_client.py` (Story 002)
- `tests/test_library_resolver.py` (Story 002)

## Approach

### Step 1: Project Structure
- Create source directory and test directory
- Create empty `__init__.py` files
- Add `.gitignore` with Python patterns

### Step 2: Dependencies
- Create `requirements.txt` with: `requests>=2.31.0`, `rich>=13.7.0`, `click>=8.1.0`, `pytest>=7.4.0`
- Create `pyproject.toml` with project metadata and build config

### Step 3: ConfigManager
- Implement `ConfigManager` class in `config.py`
- Implement: `config_exists()`, `create_config()`, `get_api_key()`, `set_api_key()`
- Add helper method `validate_api_key()` to check key format (starts with `ctx7sk_`)
- Use `pathlib.Path.expanduser()` for `~` expansion
- Set file permissions to 600 (user only) when creating config

### Step 4: CLI Skeleton
- Implement basic `coderef.py` with Click
- Add `--init` command that:
  - Prompts for API key using `click.prompt()`
  - Validates key format
  - Calls Context7 validation endpoint
  - Saves to config using ConfigManager
  - Shows success/failure message
- Add stub main command that checks for config and shows error if missing

### Step 5: Utils
- Create helper functions in `utils.py`:
  - `validate_api_key_format(api_key: str) -> bool`
  - `make_api_request(url: str, headers: dict) -> requests.Response`

### Step 6: Tests
- Test `ConfigManager`:
  - `test_config_exists_returns_true_when_config_exists`
  - `test_config_exists_returns_false_when_config_missing`
  - `test_create_config_creates_file_with_correct_permissions`
  - `test_get_api_key_returns_key_when_set`
  - `test_get_api_key_returns_none_when_not_set`
  - `test_set_api_key_writes_to_file`
- Use `tmp_path` fixture for temp config files
- Mock API requests in validation tests

### Step 7: Documentation
- Create `README.md` with:
  - Project description
  - Installation instructions
  - First-time setup (`coderef --init`)
  - Basic usage (will be expanded in later stories)
- Document dependency requirements in README

## Notes

**Implementation Decisions:**
- Used `uv` for package management instead of pip (user preference)
- Used `toml` package instead of `tomllib` for broader Python version support
- Structured as `src/coderef/` package to properly expose entry point
- Simplified API key validation to format-only (no actual Context7 API call in init)
  - Rationale: Faster setup, less friction, actual validation happens on first query
- Used Click groups (`@click.group()`) for extensible CLI structure
  - Allows easy addition of future commands (version, config, etc.)

**File Permissions:**
- Used `os.chmod(path, 0o600)` to restrict config to owner-only
- Applied both in `create_config()` and `set_api_key()`

**Config File Structure:**
```toml
[context7]
api_key = "ctx7sk_..."
```

**Learnings:**
- TOML parsing with `toml` package is straightforward
- Click's `hide_input=True` for passwords works but shows warning in non-TTY environments
- `uv pip install -e .` is faster than traditional pip for editable installs
- Click groups make CLI extensible and clean
