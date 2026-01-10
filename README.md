# coderef

Succinct code example agent powered by Claude and Context7.

Get accurate, working code examples with minimal explanation—fast.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd coderef

# Install with uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e .

# Or with pip
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Setup

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Optionally, set a Context7 API key for higher rate limits:

```bash
export CONTEXT7_API_KEY=ctx7sk-...
```

Get your API keys:
- Anthropic: [console.anthropic.com](https://console.anthropic.com)
- Context7 (optional): [context7.com/dashboard](https://context7.com/dashboard)

## Usage

```bash
# Get a code example
coderef "modern C++ fold_left"

# Rust iterators
coderef "Rust iterators filter map collect"

# Python async
coderef "Python asyncio gather example"

# React hooks
coderef "React useEffect cleanup"

# Limit response length
coderef "Go channels select" --tokens 1000
```

### Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--tokens` | `-t` | Max response tokens | 2000 |

### Output

coderef returns:
1. A minimal, working code snippet
2. A one-sentence explanation

No preamble. No filler. Just code.

## How It Works

```
Your query
    │
    ▼
Claude Haiku 4.5 + Context7 MCP
    │
    ├── Tries Context7 docs first (accurate, up-to-date)
    │
    ├── Falls back to web search if needed
    │
    ▼
Concise code example
```

1. You ask about any programming concept
2. Claude uses Context7 MCP to find accurate documentation
3. If Context7 doesn't have it, Claude searches the web
4. Claude synthesizes a minimal, working example
5. Output: code + one-line explanation

## Examples

**Query:**
```bash
coderef "Python dataclass frozen"
```

**Output:**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
# p.x = 3  # Raises FrozenInstanceError
```
A frozen dataclass is immutable after creation.

---

**Query:**
```bash
coderef "Rust Result map_err"
```

**Output:**
```rust
fn parse_number(s: &str) -> Result<i32, String> {
    s.parse::<i32>()
        .map_err(|e| format!("Parse error: {}", e))
}
```
`map_err` transforms the error type while preserving the success value.

## Development

```bash
# Run tests
uv run pytest tests/ -v

# Install dev dependencies
uv pip install -e ".[dev]"
```

## Requirements

- Python 3.11+
- `ANTHROPIC_API_KEY` environment variable

## Architecture

- **Claude Haiku 4.5**: Fast inference for quick responses
- **Context7 MCP**: Accurate, up-to-date documentation
- **Web Search**: Fallback for libraries not in Context7
- **Rich**: Markdown rendering with syntax highlighting

See [docs/core/ARCHITECTURE.md](docs/core/ARCHITECTURE.md) for details.

## License

MIT
