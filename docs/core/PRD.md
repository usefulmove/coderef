# coderef PRD

## Problem

Developers need quick, accurate code examples when learning APIs or language features. Existing solutions either:
- Provide verbose documentation that requires reading through pages of text
- Hallucinate outdated or non-existent APIs from stale training data
- Require switching between multiple tabs and sources

A one-shot CLI that returns succinct, working code examples would save significant time and reduce friction in the development workflow.

## Goals

- Provide succinct, accurate code examples via a simple CLI
- Ground responses in up-to-date documentation via Context7 MCP
- Fall back to web search when Context7 lacks coverage
- Optimize for speed using Claude Haiku 4.5
- Require minimal setup (single environment variable)

## Scope

**In scope:**
- Python CLI tool using Click
- Claude Haiku 4.5 as synthesis engine
- Context7 MCP via Anthropic's native MCP connector
- Web search fallback for unsupported libraries
- Markdown output with syntax highlighting via Rich
- Environment variable configuration (`ANTHROPIC_API_KEY`, `CONTEXT7_API_KEY`)

**Out of scope:**
- Config files or persistent settings
- Interactive/conversational modes
- Caching or retry logic
- GUI or web interface
- IDE/editor integration
- Windows/macOS-specific support (Linux-first)

## Requirements

### Functional

**FR1: Query Interface**
- CLI accepts a single positional argument: the query string
- Optional `--tokens` flag to control response length (default: 2000)
- Example: `coderef "modern C++ fold_left"`

**FR2: Documentation Retrieval**
- Use Context7 MCP tools (`resolve-library-id`, `query-docs`) as primary source
- Fall back to web search if Context7 returns no relevant documentation
- Include source attribution when using web search fallback

**FR3: Response Synthesis**
- Claude synthesizes a concise response from documentation
- Response format: code snippet first, one-sentence explanation second
- No preamble, greetings, or filler text

**FR4: Output Formatting**
- Display response as formatted Markdown
- Syntax highlighting for code blocks via Rich

**FR5: Error Handling**
- Clear error message if `ANTHROPIC_API_KEY` not set
- Graceful handling of API errors with actionable messages

### Non-Functional

**NFR1: Performance**
- Response time: typically 2-5 seconds (depends on API latency)
- Use Claude Haiku 4.5 for fastest inference

**NFR2: Usability**
- Single command, no setup wizard required
- Self-explanatory error messages

**NFR3: Reliability**
- Handle API errors without crashing
- Provide fallback path when primary source fails

## Constraints

- Requires Python 3.11+
- Requires `ANTHROPIC_API_KEY` environment variable
- Optional `CONTEXT7_API_KEY` for higher rate limits
- Linux-first (may work on other platforms)
- Dependencies: `anthropic`, `rich`, `click`

## Success Metrics

- Query to response in <5 seconds (typical case)
- Code examples are syntactically correct and runnable
- No hallucinated APIs when Context7 provides documentation
