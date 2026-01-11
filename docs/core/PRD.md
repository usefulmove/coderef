# coderef PRD

## Problem
Developers need up-to-date, accurate documentation when working with programming languages and frameworks. LLMs often hallucinate APIs or provide outdated code because their training data is stale. Context7 solves this by providing fresh documentation, but currently requires an MCP-enabled IDE or manual API calls.

## Goals
- Provide a simple CLI tool for querying code documentation ✅
- Automatically detect the relevant library from natural language questions ✅
- Display code examples with clear syntax highlighting ✅
- Require minimal configuration (just API key) ✅
- Work seamlessly on Linux without external dependencies ✅

**Status:** All goals achieved as of Story 003 completion. Story 004 complete (environment variable support).

## Scope

**In scope:**
- Python CLI tool with argparse/Click
- Integration with Context7 REST API (search + context endpoints)
- Automatic library detection with confidence scoring
- Rich terminal output with syntax highlighting
- Config file for API key storage
- Basic error handling for common failures
- Linux-only support

**Out of scope:**
- Caching or retry logic
- GUI or web interface
- Integration with editors/IDEs
- Windows/macOS support
- Advanced configuration options
- Test suite beyond basic unit tests
- CI/CD pipeline

## Requirements

### Functional

**FR1: Initial Setup**
- CLI must provide `--init` flag to set up configuration
- Must accept Context7 API key via `CONTEXT7_API_KEY` environment variable (recommended)
- Must fall back to interactive prompt if environment variable not set
- Must validate API key before saving
- Must store key in `~/.coderef/config.toml`

**FR2: Library Detection**
- Must extract language/framework keywords from questions
- Must search Context7 API for matching libraries
- Must calculate confidence score for matches (0.0-1.0)
- Must use high-confidence matches (≥0.8) automatically
- Must prompt user for medium/low-confidence matches

**FR3: Documentation Query**
- Must send question to Context7 `/api/v2/context` endpoint
- Must allow explicit library specification via `--library` flag
- Must allow token limit specification via `--tokens` flag (1000-50000)
- Must allow version specification via `--version` flag

**FR4: Output Formatting**
- Must display library name and version
- Must format code blocks with syntax highlighting (Rich)
- Must format explanatory text as markdown
- Must use colored output for readability

**FR5: Error Handling**
- Must handle missing config with helpful message
- Must handle invalid API key (401/403) with setup prompt
- Must handle rate limiting (429) with clear message
- Must handle library not found (404) with specification prompt
- Must handle network errors with helpful message

### Non-Functional

**NFR1: Performance**
- CLI must complete requests within 5 seconds for typical queries
- Config file operations must complete in <100ms

**NFR2: Usability**
- CLI must be intuitive for developers familiar with CLI tools
- Error messages must be actionable
- First-time setup must be self-explanatory

**NFR3: Reliability**
- Must handle API errors gracefully without crashing
- Must validate inputs before making API calls

**NFR4: Maintainability**
- Code must follow PEP 8 style guidelines
- Functions must have clear docstrings
- Project structure must be modular and extensible

## Constraints

- Must run on Linux with Python 3.11+
- Must use only standard library + requests + rich + click
- Must not require MCP server to run locally
- Must use Context7 REST API (not MCP protocol)
- Config file must be stored in `~/.coderef/`
