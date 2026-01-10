# coderef Architecture

## Overview

coderef is a Python CLI tool that provides succinct code examples by combining Claude Haiku 4.5 with Context7 MCP for documentation grounding. The architecture is intentionally minimal: a CLI entry point, an agent module, and output formatting.

## Components

| Component | Responsibility | File |
|-----------|----------------|------|
| CLI Entry Point | Argument parsing, error handling, output display | `src/coderef/main.py` |
| Agent | Claude API calls, MCP configuration, tool orchestration | `src/coderef/agent.py` |
| Output | Rich markdown rendering | `src/coderef/output.py` |

## Data Flow

```
User: coderef "modern C++ fold_left"
         │
         ▼
    ┌─────────────┐
    │  Click CLI  │  Parse args, validate env vars
    └─────────────┘
         │
         ▼
    ┌─────────────────────────────────────────────┐
    │         Anthropic Messages API              │
    │  ┌───────────────────────────────────────┐  │
    │  │ Model: claude-haiku-4-5               │  │
    │  │ System: Succinct code example prompt  │  │
    │  │ MCP: https://mcp.context7.com/mcp     │  │
    │  │ Tools: [mcp_toolset, web_search]      │  │
    │  │ Beta: mcp-client, web-search          │  │
    │  └───────────────────────────────────────┘  │
    └─────────────────────────────────────────────┘
         │
         │  Claude orchestrates tools:
         │  1. resolve-library-id (Context7)
         │  2. query-docs (Context7)
         │  3. web_search (fallback)
         │
         ▼
    ┌─────────────┐
    │  Response   │  Code snippet + one-sentence explanation
    └─────────────┘
         │
         ▼
    ┌─────────────┐
    │ Rich Output │  Markdown with syntax highlighting
    └─────────────┘
```

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Claude Haiku 4.5 | Fastest Claude model, optimized for speed |
| Native MCP connector | No subprocess management, simpler than MCP SDK |
| Web search fallback | Covers libraries not in Context7's index |
| Environment variables only | Simplest configuration, no file management |
| Rich for output | Best terminal markdown/syntax highlighting |

## Tech Stack

**Language:** Python 3.11+

**Dependencies:**
- `anthropic>=0.40.0` - Claude API client with MCP support
- `rich>=13.7.0` - Terminal formatting
- `click>=8.1.0` - CLI framework

**External Services:**
- Anthropic Messages API (Claude Haiku 4.5)
- Context7 MCP Server (`https://mcp.context7.com/mcp`)

## API Integration

### Anthropic Messages API

```python
client.beta.messages.create(
    model="claude-haiku-4-5",
    max_tokens=2000,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": question}],
    mcp_servers=[{
        "type": "url",
        "url": "https://mcp.context7.com/mcp",
        "name": "context7",
        "authorization_token": "..."  # Optional, for higher rate limits
    }],
    tools=[
        {"type": "mcp_toolset", "mcp_server_name": "context7"},
        {"type": "web_search_20250305", "name": "web_search", "max_uses": 3}
    ],
    betas=["mcp-client-2025-11-20", "web-search-2025-03-05"]
)
```

### Context7 MCP Tools

| Tool | Purpose |
|------|---------|
| `resolve-library-id` | Find Context7 library ID from query |
| `query-docs` | Fetch documentation for a library |

### Beta Features Used

| Feature | Header | Purpose |
|---------|--------|---------|
| MCP Connector | `mcp-client-2025-11-20` | Native MCP server connection |
| Web Search | `web-search-2025-03-05` | Fallback documentation source |

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API authentication |
| `CONTEXT7_API_KEY` | No | Context7 higher rate limits |

### System Prompt

The agent uses a carefully crafted system prompt that instructs Claude to:
1. Use Context7 tools first for documentation
2. Fall back to web search if Context7 fails
3. Return only: code snippet + one-sentence explanation
4. No preamble, greetings, or filler

## File Structure

```
coderef/
├── src/
│   └── coderef/
│       ├── __init__.py    # Package exports
│       ├── agent.py       # Claude + MCP integration
│       ├── main.py        # CLI entry point
│       └── output.py      # Rich markdown output
├── tests/
│   └── test_agent.py      # Agent unit tests
├── docs/
│   └── core/
│       ├── PRD.md
│       └── ARCHITECTURE.md
├── pyproject.toml
└── README.md
```

## Error Handling

| Error | Source | Handling |
|-------|--------|----------|
| Missing API key | Environment | Exit with clear message |
| API error | Anthropic | Display error, exit 1 |
| No response | Claude | Return fallback message |

## Performance Characteristics

- **Latency:** 2-5 seconds typical (API-bound)
- **Token usage:** ~500-2000 output tokens per query
- **Cost:** ~$0.001-0.005 per query (Haiku pricing)

## Extensibility

The architecture supports future enhancements:
- Add `--model` flag for model selection
- Add `--verbose` flag for debug output
- Add caching layer for repeated queries
- Add streaming output for long responses
