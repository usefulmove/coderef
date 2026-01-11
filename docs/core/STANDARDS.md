# coderef Coding Standards

## Python Style Guide

Follow PEP 8 guidelines with these clarifications:

### Line Length
- Maximum 100 characters (stricter than PEP 8's 79)
- Use implicit line joining for strings (parentheses)

### Imports
- Group imports: standard library, third-party, local
- Sort alphabetically within groups
- Use `from module import Class` for single imports
- Avoid wildcard imports (`from module import *`)

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Classes | PascalCase | `Context7Client` |
| Functions | snake_case | `search_library` |
| Variables | snake_case | `api_key` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_TOKENS` |
| Private members | Leading underscore | `_internal_method` |

### Type Hints
- All function parameters must have type hints
- Return types must be explicit
- Use `|` union syntax (Python 3.10+)
- Use `Optional[T]` for nullable values

```python
def search_library(self, library_name: str, query: str) -> list[dict]:
    """Search for a library in Context7."""
    pass

def get_api_key(self) -> str | None:
    """Get API key from config or None if not set."""
    pass
```

### Docstrings
- Use triple double quotes (`"""`)
- One-line summary for simple functions
- Multi-line for complex functions with Args/Returns/Raises sections

```python
def get_context(self, library_id: str, query: str, tokens: int = 5000) -> dict:
    """Fetch documentation context for a library.

    Args:
        library_id: Context7 library ID (e.g., /vercel/next.js)
        query: The question or task to get docs for
        tokens: Maximum tokens to return (1000-50000)

    Returns:
        Dictionary containing formatted documentation

    Raises:
        ValueError: If tokens outside valid range
        requests.HTTPError: If API request fails
    """
    pass
```

### Comments
- Use inline comments for complex logic only
- Explain "why", not "what"
- Keep comments concise

```python
# Validate token limits (API constraint)
if not 1000 <= tokens <= 50000:
    raise ValueError("Tokens must be between 1000 and 50000")
```

## File Organization

### Module Structure
- Imports first
- Constants second
- Classes third
- Functions last
- `if __name__ == "__main__":` at the end

### Class Structure
- `__init__` first
- Public methods second
- Private methods third
- Properties fourth

```python
class Example:
    """Example class following structure."""

    def __init__(self, value: str):
        """Initialize the example."""
        self._value = value

    def public_method(self) -> str:
        """Public method."""
        return self._value.upper()

    def _private_method(self) -> str:
        """Private method."""
        return self._value.lower()
```

## Error Handling

### Exception Handling
- Use specific exceptions, not bare `except:`
- Handle expected errors locally
- Re-raise unexpected errors with context

```python
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
except requests.HTTPError as e:
    raise APIError(f"Failed to fetch data: {e}") from e
```

### Custom Exceptions
- Define custom exceptions in a central location
- Inherit from `Exception` or appropriate base
- Provide helpful error messages

```python
class ConfigError(Exception):
    """Configuration-related errors."""
    pass

class APIError(Exception):
    """API-related errors."""
    pass
```

## Testing Standards

### Test Structure
- Use pytest as test framework
- Test files named `test_<module>.py`
- One test class per module being tested
- One test method per behavior

### Test Naming
- Use descriptive test names: `test_<what>_<expected>`

```python
class TestConfigManager:
    """Test ConfigManager class."""

    def test_get_api_key_returns_key_when_set(self):
        """Test that get_api_key returns the key when set."""
        pass

    def test_get_api_key_returns_none_when_not_set(self):
        """Test that get_api_key returns None when not set."""
        pass
```

### Test Organization
- Arrange-Act-Assert (AAA) pattern
- Use fixtures for common setup
- Mock external dependencies (API, filesystem)

```python
def test_search_library_calls_api(self, mock_requests):
    """Test that search_library makes correct API call."""
    # Arrange
    client = Context7Client("test_key")
    mock_requests.get.return_value.json.return_value = {"results": []}

    # Act
    client.search_library("react", "hooks")

    # Assert
    mock_requests.get.assert_called_once_with(
        "https://context7.com/api/v2/libs/search",
        params={"libraryName": "react", "query": "hooks"},
        headers={"Authorization": "Bearer test_key"}
    )
```

## CLI Standards

### Command Structure
- Use Click decorators for commands
- Provide help text for all options
- Use descriptive option names

```python
@click.command()
@click.argument("question", type=str)
@click.option(
    "--library", "-l",
    type=str,
    help="Explicitly specify library (e.g., /facebook/react)"
)
@click.option(
    "--tokens", "-t",
    type=int,
    default=5000,
    show_default=True,
    help="Token limit for context (1000-50000)"
)
def main(question: str, library: str, tokens: int):
    """Query Context7 for code documentation."""
    pass
```

### User Messages
- Use friendly, actionable messages
- Provide guidance for next steps
- Colorize important information

```python
console.print(
    "❌ API key not found. Run [bold]coderef --init[/bold] to set up.",
    style="red"
)
```

## Dependency Management

### Requirements
- Pin exact versions in requirements.txt
- Use semantic versioning for version ranges in pyproject.toml
- Update requirements regularly for security patches

### Virtual Environment
- Use venv for development
- Document environment setup in README.md

## Git Standards

### Commit Messages
- Use conventional commits format
- Keep first line under 50 characters
- Add body for complex changes if needed

```
feat: add library resolution with confidence scoring

Implement keyword extraction from questions and confidence-based
library selection. Uses Context7 search API and scores results based
on name match, description relevance, and popularity.

Fixes #123
```

### Branch Naming
- `feature/<name>` for new features
- `fix/<name>` for bug fixes
- `refactor/<name>` for refactoring

## Documentation Standards

### README.md
- Include installation instructions
- Provide usage examples
- Document all CLI flags
- Add troubleshooting section

### Docstrings
- Document all public APIs
- Use Google-style or NumPy-style formatting
- Include examples for complex functions

### Code Comments
- Comment complex algorithms
- Explain non-obvious decisions
- Mark TODO items with issue references

## Security Standards

### API Keys
- Never hardcode API keys in code
- Never log API keys
- Validate API key format before use

### Input Validation
- Validate all user inputs
- Sanitize file paths
- Escape shell arguments

### Dependencies
- Review dependencies for vulnerabilities
- Update dependencies regularly
- Use `pip-audit` for security checks
