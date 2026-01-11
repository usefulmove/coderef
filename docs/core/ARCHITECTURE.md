# coderef Architecture

## Overview
coderef is a Python CLI tool that queries the Context7 REST API to provide up-to-date code documentation. It consists of a command-line interface, API client, library resolver, output formatter, and config manager.

## Components

| Component | Responsibility | File |
|-----------|----------------|------|
| CLI Entry Point | Argument parsing, command routing, main orchestration | `src/coderef/main.py` |
| API Client | HTTP requests to Context7 API, error handling | `src/coderef/api_client.py` |
| Library Resolver | Extract keywords from questions, search for libraries, confidence scoring | `src/coderef/library_resolver.py` |
| Output Formatter | Rich terminal formatting, syntax highlighting, markdown rendering | `src/coderef/output.py` |
| Config Manager | Read/write config file, API key validation | `src/coderef/config.py` |
| Utilities | API key validation helpers | `src/coderef/utils.py` |

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Use Click for CLI | Better than argparse for complex argument handling, well-maintained |
| Use Rich for output | Best-in-class terminal formatting, built-in syntax highlighting |
| Use TOML for config | Human-readable, Python 3.11+ has built-in support |
| Confidence-based library detection | Balances automation with user control |
| Direct REST API calls | Simpler than MCP integration, no local server required |

## Tech Stack

**Language:** Python 3.11+

**Dependencies:**
- `requests>=2.31.0` - HTTP client
- `rich>=13.7.0` - Terminal formatting
- `click>=8.1.0` - CLI framework
- `toml` (built-in Python 3.11+) - Config parsing

**API:** Context7 REST API v2

## Integration Points

### Context7 API
- **Endpoint 1:** `GET /api/v2/libs/search?libraryName={name}&query={query}`
  - Used for library resolution
  - Returns list of matching libraries with confidence scores

- **Endpoint 2:** `GET /api/v2/context?libraryId={id}&query={query}&tokens={count}`
  - Used for fetching documentation
  - Returns formatted documentation with code examples

- **Authentication:** Bearer token in Authorization header

### Config File
- **Location:** `~/.coderef/config.toml`
- **Format:** TOML
- **Contents:** API key, display preferences

## Data Flow

```
User runs: coderef "question about X"
    ↓
CLI parses arguments
    ↓
ConfigManager loads API key from ~/.coderef/config.toml or environment variable
    ↓
LibraryResolver extracts keywords from question
    ↓
APIClient.search_library() → Context7 API
    ↓
LibraryResolver calculates confidence score
    ↓
If confidence ≥ 0.8: Continue automatically
If confidence < 0.8: Check --skip-library-detect flag
    ↓ If not skipped: Prompt user to specify library
    ↓
If --skip-library-detect: Skip detection, let Context7 handle library resolution
    ↓
APIClient.get_context() → Context7 API (with or without libraryId)
    ↓
OutputFormatter.format_response()
    ↓
Display to terminal with Rich
```
User runs: coderef "question about X"
    ↓
CLI parses arguments
    ↓
ConfigManager loads API key from ~/.coderef/config.toml
    ↓
LibraryResolver extracts keywords from question
    ↓
APIClient.search_library() → Context7 API
    ↓
LibraryResolver calculates confidence score
    ↓
If confidence ≥ 0.8: Continue automatically
If confidence < 0.8: Prompt user to specify library
    ↓
APIClient.get_context() → Context7 API
    ↓
OutputFormatter.format_response()
    ↓
Display to terminal with Rich
```

## Module Interfaces

### Context7Client
```python
class Context7Client:
    def __init__(self, api_key: str)
    def search_library(self, library_name: str, query: str) -> List[dict]
    def get_context(self, library_id: str, query: str, tokens: int = 5000) -> dict
    def validate_api_key(self) -> bool
```

### LibraryResolver
```python
class LibraryResolver:
    def __init__(self, api_client: Context7Client)
    def resolve_from_question(self, question: str) -> tuple[str, float]
    def extract_keywords(self, question: str) -> List[str]
    def calculate_confidence(self, match: dict, keywords: List[str]) -> float
    def get_confidence_level(self, score: float) -> str  # "high", "medium", "low"
```

### OutputFormatter
```python
class OutputFormatter:
    def __init__(self, theme: str = "default", code_theme: str = "monokai")
    def format_response(self, context: dict, library_id: str) -> None
    def format_library_header(self, library_id: str) -> Panel
    def format_code_block(self, code: str, language: str) -> Syntax
    def format_markdown(self, text: str) -> Markdown
    def format_error(self, message: str) -> Panel
```

### ConfigManager
```python
class ConfigManager:
    def __init__(self, config_path: str = "~/.coderef/config.toml")
    def get_api_key(self) -> str | None
    def set_api_key(self, api_key: str) -> None
    def config_exists(self) -> bool
    def create_config(self) -> None
    def get_display_theme(self) -> str
    def get_code_theme(self) -> str
```

## Error Handling Strategy

| Error Type | Source | Handling |
|------------|--------|----------|
| Config not found | ConfigManager | Show first-time setup message |
| Invalid API key | APIClient (401/403) | Prompt to re-run --init |
| Rate limit exceeded | APIClient (429) | Show error with retry message |
| Library not found | APIClient (404) | Prompt to use --library flag |
| Low confidence | LibraryResolver | Prompt to specify library |
| Network error | requests | Show connection error |
| Invalid input | CLI/Click | Show usage message |

## Configuration Schema

```toml
# ~/.coderef/config.toml
[context7]
api_key = "ctx7sk_..."
```

**Environment Variable:** `CONTEXT7_API_KEY`

During initialization (`coderef --init`), the tool first checks the `CONTEXT7_API_KEY` environment variable. If present and valid, it uses the key directly. If not, it falls back to interactive prompting.

### Configuration Precedence

coderef looks for API key in this order for all commands:

1. **Environment variable**: `CONTEXT7_API_KEY`
   - Checked for all commands (init, queries)
   - Highest priority
   - Runtime override

2. **Config file**: `~/.coderef/config.toml`
   - Used as fallback if env var not set
   - Persisted by `coderef --init`

This means if `CONTEXT7_API_KEY` is set, you can use coderef immediately without running init.

**Note:** Display themes are hardcoded in `OutputFormatter` (default theme, monokai code theme) but can be extended to support configurable themes in the future.

## File Structure

```
coderef/
├── docs/
│   ├── core/
│   │   ├── PRD.md
│   │   ├── ARCHITECTURE.md
│   │   └── STANDARDS.md
│   ├── stories/                    # Active work
│   ├── reference/
│   │   └── completed/              # Completed stories
│   │       ├── 001-initial-cli.md
│   │       ├── 002-api-client.md
│   │       └── 003-cli-integration.md
│   ├── skills/
│   └── logs/                       # Session summaries
├── src/
│   └── coderef/
│       ├── __init__.py             # Package exports
│       ├── main.py                 # CLI entry point
│       ├── config.py               # ConfigManager
│       ├── api_client.py           # Context7Client
│       ├── library_resolver.py     # LibraryResolver
│       ├── output.py               # OutputFormatter
│       └── utils.py                # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_config.py              # 12 tests
│   ├── test_api_client.py          # 11 tests
│   └── test_library_resolver.py    # 18 tests
├── pyproject.toml                  # Python project config
├── requirements.txt                # Dependencies
├── README.md
└── .gitignore
```

## Security Considerations

- API key stored in user home directory (not in project)
- Config file permissions restricted to user only (600)
- API key never logged or displayed in output
- HTTPS used for all API calls
- Input validation before API calls

## Performance Considerations

- Config operations are synchronous and fast (<100ms)
- API calls have 10-second timeout
- No caching (out of scope)
- Output formatting is synchronous (terminal is blocking)

## Extensibility

- Easy to add new config options (extend TOML schema)
- Easy to add new CLI flags (Click decorators)
- Easy to add new API endpoints (Context7Client methods)
- Easy to add new output themes (Rich themes)
- Easy to add new confidence strategies (LibraryResolver methods)
