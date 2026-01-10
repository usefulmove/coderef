# 009 Agent Rewrite

## Goal

Transform coderef from a Context7 REST API client into a succinct code example agent powered by Claude + Context7 MCP. This enables higher-quality, synthesized responses rather than raw documentation dumps.

## Status: Complete

## Acceptance Criteria

- [x] Replace REST API client with Anthropic Messages API + MCP connector
- [x] Use Claude Haiku 4.5 for fast inference
- [x] Include web search fallback for libraries not in Context7
- [x] Simplify CLI to single query interface
- [x] Update all documentation (PRD, Architecture)
- [x] Write new tests for agent module
- [x] Update README with new usage
- [x] Clean terminal output formatting (filter preamble text, proper code block rendering)

## Context Scope

**Write:**
- src/coderef/agent.py (new)
- src/coderef/main.py (rewrite)
- src/coderef/output.py (simplify)
- src/coderef/__init__.py (update)
- docs/core/PRD.md
- docs/core/ARCHITECTURE.md
- tests/test_agent.py (new)
- README.md
- pyproject.toml

**Delete:**
- src/coderef/api_client.py
- src/coderef/library_resolver.py
- src/coderef/config.py
- src/coderef/utils.py
- tests/test_config.py
- tests/test_api_client.py
- tests/test_library_resolver.py

## Approach

1. Update dependencies: replace `requests`, `toml` with `anthropic`
2. Create new `agent.py` with Claude + MCP integration
3. Simplify `main.py` to minimal CLI
4. Remove obsolete modules
5. Update documentation
6. Write new tests

## Notes

### Key Technical Decisions

- **Beta API required**: Must use `client.beta.messages.create()` not `client.messages.create()`
- **Native MCP connector**: Anthropic's API supports MCP servers directly via `mcp_servers` parameter
- **Beta features**: Passed via `betas=["mcp-client-2025-11-20", "web-search-2025-03-05"]` parameter
- **Model choice**: `claude-haiku-4-5` for speed
- **Web search as fallback**: `web_search_20250305` (not `web_search_tool_20250305`)
- **Auth token**: Use `authorization_token` field in MCP server config (not `headers`)

### Correct API Structure

```python
client.beta.messages.create(
    model="claude-haiku-4-5",
    mcp_servers=[{
        "type": "url",
        "url": "https://mcp.context7.com/mcp",
        "name": "context7",
        "authorization_token": "..."  # Optional
    }],
    tools=[
        {"type": "mcp_toolset", "mcp_server_name": "context7"},
        {"type": "web_search_20250305", "name": "web_search", "max_uses": 3}
    ],
    betas=["mcp-client-2025-11-20", "web-search-2025-03-05"]
)
```

### Response Block Types

When processing responses, these block types may appear:
- `mcp_tool_use` - Claude calling Context7 MCP tool
- `mcp_tool_result` - Result from Context7 MCP
- `server_tool_use` - Claude calling web search
- `web_search_tool_result` - Result from web search
- `text` - Text content (may appear multiple times)

**Important**: Text blocks before/between tool calls contain "thinking out loud" preamble. Only text blocks AFTER the last tool result contain the final synthesized response.

### Breaking Changes from v0.1.0

- Removed `--init` flag (no config file needed)
- Removed `--library` flag (agent resolves automatically)
- Removed `--version` flag (Context7 handles versioning)
- Removed `--skip-library-detect` flag (not applicable)
- Output format changed from structured panels to plain markdown

## Implementation Complete

All acceptance criteria met. The following was implemented:

1. **Filter pre-tool text blocks**: Added `_extract_final_text()` function that only includes text blocks after the last tool result (`mcp_tool_result` or `web_search_tool_result`)
2. **Strengthened system prompt**: Added explicit instructions to not narrate tool usage
3. **Added tests**: 6 new tests for filtering behavior with mock responses containing multiple block types
4. **Total tests**: 20 passing
