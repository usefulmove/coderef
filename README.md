# coderef

CLI tool for querying up-to-date code documentation using the Context7 API.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd coderef

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

Alternatively, use `uv` for faster package management:

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
uv pip install -e .
```

## First-Time Setup

Before using coderef, you need to set up your Context7 API key.

1. Get a free API key at [context7.com/dashboard](https://context7.com/dashboard)
2. Run the initialization command:

**Option 1: Environment variable (recommended)**

```bash
# Set in shell profile (.zshrc, .bashrc, etc.)
export CONTEXT7_API_KEY=ctx7sk-...

# Then use directly (no init required)
coderef "How do I use React hooks?"

# Or run init to save to config file
CONTEXT7_API_KEY=ctx7sk-... coderef --init
```

This is the fastest method. Accepted formats:
- `ctx7sk-...` (current format with hyphen)
- `ctx7sk_...` (legacy format with underscore)

**How it works:**
- Environment variable is checked for every command (highest priority)
- Config file is used as fallback
- If env var is set, no init step required

**Option 2: Interactive prompt**

```bash
coderef --init
```

You'll be prompted to enter and confirm your API key. This provides extra security but requires typing the key twice.

## Usage

Ask questions about code documentation in natural language:

```bash
# Simple question (auto-detect library)
coderef "How do I use React hooks?"

# Explicit library
coderef "How do I create middleware?" --library /vercel/next.js

# With version
coderef "How do I use app router?" --library /vercel/next.js --version v15.0.0

# Token limit
coderef "Explain useState" --tokens 8000
```

### Flags

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--library` | `-l` | Explicitly specify library ID (e.g., /facebook/react) | Auto-detect |
| `--tokens` | `-t` | Token limit for context (1000-50000) | 5000 |
| `--version` | `-v` | Library version (e.g., v18.3.1) | Latest |
| `--init` | | Initialize configuration with API key | |
| `--debug` | | Enable debug output for troubleshooting | False |

### Command Reference

```bash
# Show help
coderef --help

# Initialize configuration
coderef --init

# Initialize with debug output
DEBUG=true coderef --init
coderef --init --debug

# Query documentation
coderef "How do I use useEffect in React?"
coderef "How do I create a FastAPI endpoint?" --library /tiangolo/fastapi
coderef "What's new in Next.js 15?" --library /vercel/next.js --version v15.0.0
```

## How It Works

1. You ask a question about a programming language or framework
2. coderef automatically detects the relevant library from your question
3. It queries the Context7 API for up-to-date documentation
4. Code examples are displayed with syntax highlighting
5. Explanations are formatted in readable markdown

## Library Auto-Detection

coderef uses intelligent library detection based on keywords in your question:

- **Languages:** python, javascript, typescript, java, go, rust, c#, ruby, php, swift, kotlin
- **Frameworks:** react, vue, angular, next.js, express, fastapi, django, flask, spring, rails, laravel, nestjs, gin
- **Libraries:** pandas, numpy, matplotlib, requests, tensorflow, pytorch, tensorflow, scikit-learn, pytest, jest, lodash, moment

If the tool detects the library with high confidence (≥0.8), it uses that library automatically. For medium confidence (0.5-0.8), it shows a warning. For low confidence (<0.5), it prompts you to specify the library explicitly with the `--library` flag.

## Troubleshooting

### Configuration not found

```
❌ Configuration not found.
Run [bold]coderef --init[/bold] to set up.
```

Run `coderef --init` to set up your configuration. You can either:

```bash
# Fast: Use environment variable (paste once)
CONTEXT7_API_KEY=ctx7sk-... coderef --init

# Secure: Interactive prompt (type twice)
coderef --init
```

**Note:** If you've already set `CONTEXT7_API_KEY` in your shell profile, it should work immediately without running init. Try running a query directly.

### Environment variable not detected

If you set `CONTEXT7_API_KEY` in `.zshrc` but coderef doesn't detect it:

1. **Reload your shell profile:**
   ```bash
   source ~/.zshrc
   ```

2. **Or restart your terminal** to apply changes

3. **Verify env var is set:**
   ```bash
   echo $CONTEXT7_API_KEY
   ```
   This should show your API key.

4. **Check your shell profile:**
   ```bash
   cat ~/.zshrc | grep CONTEXT7_API_KEY
   ```
   Ensure line starts with `export`:
   ```bash
   export CONTEXT7_API_KEY=ctx7sk-...
   ```

5. **Test with DEBUG mode:**
   ```bash
   DEBUG=true coderef --init
   ```
   This will show detailed information about env var detection.

```bash
# Fast: Use environment variable (paste once)
CONTEXT7_API_KEY=ctx7sk_... coderef --init

# Secure: Interactive prompt (type twice)
coderef --init
```

### Invalid API key

```
❌ Invalid API key format. Key must start with 'ctx7sk_'
```

Make sure you're using a Context7 API key from the dashboard.

If using the environment variable:
```bash
CONTEXT7_API_KEY=ctx7sk-... coderef --init
```

Ensure the key is valid and starts with `ctx7sk-` (current format) or `ctx7sk_` (legacy format).

### Library not found

```
❌ Library not found. Check the [bold]--library[/bold] flag.
```

Try using the `--library` flag to explicitly specify the library ID, or rephrase your question to be more specific.

### Low confidence library match

```
⚠️ Using library: /org/repo (confidence: 0.42)
```

The tool is unsure about the library. Use the `--library` flag to specify explicitly.

### Rate limit exceeded

```
❌ Rate limit exceeded. Please wait before retrying.
```

You've reached the API rate limit. Wait a bit before making more requests, or get a paid plan at [context7.com](https://context7.com).

## Development

```bash
# Run tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_config.py -v

# Run with coverage
uv run pytest tests/ --cov=coderef
```

## Requirements

- Python 3.11 or higher
- Linux (currently only Linux is supported)

## License

MIT
