# 003 Output Formatting, CLI Integration, and Polish

## Goal
Implement output formatting with Rich, integrate all components into the main CLI, add explicit flags, and complete error handling.

## Acceptance Criteria

- [x] `OutputFormatter` displays library header with name and version
- [x] `OutputFormatter` formats code blocks with syntax highlighting
- [x] `OutputFormatter` formats explanatory text as markdown
- [x] Main CLI accepts `question` argument and optional `--library`, `--tokens`, `--version` flags
- [x] CLI integrates ConfigManager, LibraryResolver, and API Client
- [x] CLI shows detected library for high/medium confidence
- [x] CLI prompts for library when confidence is low
- [x] All error paths show helpful, actionable messages
- [x] Output is colorful and easy to read
- [x] All code follows STANDARDS.md conventions

## Context Scope

**Write:**
- `src/output.py`
- `src/coderef.py` (complete implementation)
- Update `README.md` with full usage examples

**Read:**
- `docs/core/ARCHITECTURE.md`
- `docs/core/STANDARDS.md`
- `src/config.py`
- `src/api_client.py`
- `src/library_resolver.py`

**Exclude:**
- No exclusions (complete the CLI)

## Approach

### Step 1: OutputFormatter Base
- Create `OutputFormatter` class with:
  - `__init__(theme: str = "default", code_theme: str = "monokai")`
  - Initialize Rich console with theme
- Store themes as instance variables for formatting methods

### Step 2: Library Header
- Implement `format_library_header(library_id: str) -> Panel`
- Parse library_id to extract name and version (if present)
  - Format: `/org/repo/vX.Y.Z` → name: `org/repo`, version: `vX.Y.Z`
  - Format: `/org/repo` → name: `org/repo`, version: `latest`
- Create Rich Panel with:
  - Title: library name and version
  - Border style: rounded
  - Padding: (1, 2)
  - Color: blue/cyan

### Step 3: Code Block Formatting
- Implement `format_code_block(code: str, language: str) -> Syntax`
- Use Rich's `Syntax` class
- Detect language from:
  - Explicit `language` parameter
  - Library name heuristics (e.g., `/python/python` → "python")
  - Default to "text" if unknown
- Apply code theme from instance
- Line numbers: enabled
- Line width: 100 (match STANDARDS.md)

### Step 4: Markdown Formatting
- Implement `format_markdown(text: str) -> Markdown`
- Use Rich's `Markdown` class
- Parse and render:
  - Headers
  - Bullet lists
  - Code blocks (inline)
  - Bold/italic text
- Style with readable colors

### Step 5: Error Formatting
- Implement `format_error(message: str) -> Panel`
- Create red/orange panel
- Use emoji for visual emphasis (❌, ⚠️, ℹ️)
- Add actionable guidance in panel

### Step 6: Main format_response()
- Implement `format_response(context: dict, library_id: str) -> None`
- Call `format_library_header()` and print
- Parse context dict:
  - Extract `context` text (explanation)
  - Extract `examples` array (code examples)
- Print explanation using `format_markdown()`
- For each example:
  - Extract `code` and `language`
  - Print using `format_code_block()`
- Add separator line between examples
- Use Rich `console.print()` for all output

### Step 7: CLI Main Command
- Update `src/coderef.py` with full implementation:
  - Import all components
  - Use Click for CLI interface
- Command structure:
  ```python
  @click.command()
  @click.argument("question", type=str)
  @click.option("--library", "-l", type=str, help="Explicit library ID")
  @click.option("--tokens", "-t", type=int, default=5000, help="Token limit")
  @click.option("--version", "-v", type=str, help="Library version")
  @click.option("--init", is_flag=True, help="Initialize configuration")
  def main(question, library, tokens, version, init):
  ```

### Step 8: Handle --init Flag
- Check `init` flag first
- If set, run initialization flow:
  - Prompt for API key
  - Validate key
  - Save to config
  - Show success message
  - Exit (don't process question)

### Step 9: Load Config
- Create `ConfigManager` instance
- Check if config exists
- If not, show error: `config not found. run coderef --init`
- Load API key from config

### Step 10: Resolve Library
- Create `Context7Client` with API key
- Create `LibraryResolver` with client
- If `--library` flag provided:
  - Use that library ID directly
  - Append version if `--version` provided
- If no explicit library:
  - Call `resolver.resolve_from_question(question)`
  - Check confidence level
  - If high (≥0.8): show "Using library: {id}" and continue
  - If medium (0.5-0.8): show "Using library: {id} (confidence: {score})" and continue
  - If low (<0.5): show error asking for `--library` flag and exit

### Step 11: Fetch Documentation
- Call `api_client.get_context(library_id, question, tokens)`
- Handle errors with OutputFormatter:
  - `AuthError` → "Invalid API key. Run coderef --init"
  - `RateLimitError` → "Rate limit exceeded. Wait before retrying."
  - `NotFoundError` → "Library not found. Check --library flag."
  - `APIError` → "API error: {message}"

### Step 12: Format and Display
- Create `OutputFormatter` instance
- Call `formatter.format_response(context, library_id)`
- Exit with success code (0)

### Step 13: Error Handling Completeness
- Add try/except wrapper around main logic
- Catch all expected exceptions:
  - `ConfigError` → config-related errors
  - `APIError`, `AuthError`, `RateLimitError`, `NotFoundError` → API errors
  - `ValueError` → invalid inputs (tokens range, etc.)
  - `requests.RequestException` → network errors
- Display formatted error message using `OutputFormatter.format_error()`
- Exit with error code (1)

### Step 14: Update README
- Add installation section: `pip install -r requirements.txt`
- Add first-time setup: `coderef --init`
- Add usage examples:
  - Simple: `coderef "How do I use React hooks?"`
  - Explicit library: `coderef "How do I create middleware?" --library /vercel/next.js`
  - With version: `coderef "How do I use app router?" --library /vercel/next.js --version v15.0.0`
  - Token limit: `coderef "Explain useState" --tokens 8000`
- Add troubleshooting section:
  - API key not found
  - Invalid API key
  - Library not found
  - Rate limit
- Add flag reference table

### Step 15: Polish
- Add Rich progress spinner for API calls (optional)
- Add version information: `coderef --version`
- Add help text: `coderef --help`
- Ensure all user-facing messages are friendly
- Add emoji icons for visual clarity
- Test with real API (if API key available)

## Notes

- Rich Panel styles: `border_style="blue"`, `padding=(1, 2)`
- Syntax themes: "monokai", "dracula", "github-dark", "nord"
- Markdown rendering: Use built-in Markdown class from Rich
- Emoji usage: 📚 for docs, ❌ for errors, ⚠️ for warnings, ℹ️ for info
- Confidence display: Use color coding (green=high, yellow=medium, red=low)
- Library ID parsing: Split on `/v` to extract version, rest is name
- For version appending: `library_id` → `library_id + "/" + version` if version provided
- API timeout: 10 seconds (already set in API client)
- Exit codes: 0 for success, 1 for errors
- Consider adding `--verbose` flag for debugging (optional, out of scope?)

## Implementation Notes

**Created files:**
- `src/coderef/output.py` - OutputFormatter class with Rich integration

**Modified files:**
- `src/coderef/main.py` - Complete CLI implementation with all integrations
- `src/coderef/__init__.py` - Added OutputFormatter to exports
- `README.md` - Updated with full usage examples and troubleshooting

**Key implementation details:**
- Made QUESTION argument optional (required=False) so --init works without it
- Added validation: question is required unless --init is used
- Used Rich console for all output with custom error/info/warning panels
- Confidence display: blue for high, yellow for medium, red (error) for low
- All error paths exit with code 1
- Library detection with confidence threshold handling as specified
- Used monokai theme for code highlighting

## Example Output

```
╭────────────────────────────────────────────────────────────╮
│ 📚 /facebook/react (v18.3.1)                               │
╰────────────────────────────────────────────────────────────╯

To use the useState hook for state management in React:

```python
import React, { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

The useState hook returns:
• Current state value (first element)
• Function to update state (second element)

Key points:
- Initial state is passed as the argument
- State updates trigger component re-renders
- State is local to each component instance
- Updates are asynchronous and batched

─────────────────────────────────────────────────────────────
```

## Testing Considerations

- Test output formatting with actual Rich output (captured with console capture)
- Test CLI with click's CliRunner
- Mock API calls for integration tests
- Test error paths with various exception types
- Manual testing with real API recommended
