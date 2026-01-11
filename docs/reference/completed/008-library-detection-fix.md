# 008 Allow Queries Without Explicit Library

## Goal
Enable natural language queries without requiring explicit `--library` flag by calling Context7 API without `libraryId` parameter, letting Context7 handle library resolution internally.

## Root Cause

**Problem:**
- CLI requires explicit `libraryId` parameter for `/api/v2/context` endpoint
- Context7 API and Context7 Chat can handle natural language queries without library specification
- Users get error "Could not detect library. Use --library to specify." when asking generic questions
- Example: `"C++ lambda functions"` returns `C++` which isn't a valid library ID

**Test Results:**
- Option C tested: Calling `/api/v2/context?query=...` (without libraryId) returns proper API response
- When libraryId=`C++` (from auto-detection), returns 400 Bad Request
- Context7 API accepts queries without libraryId and handles library resolution internally

## Acceptance Criteria

- [ ] Modify `_resolve_library()` to support skipping library detection
- [ ] Update `Context7Client.get_context()` to handle None library_id
- [ ] Update `main()` to call API without libraryId when library_id is None
- [ ] Add `--skip-library-detect` flag to bypass auto-detection
- [ ] Test with natural language queries (e.g., "C++ lambda functions")
- [ ] Test with explicit library (e.g., "react hooks" --library /facebook/react)
- [ ] All existing tests pass

## Context Scope

**Write:**
- `src/coderef/main.py` (modify `_resolve_library`, `main`, add flag)
- `src/coderef/api_client.py` (update `get_context` to handle None library_id)
- `README.md` (document new flag and behavior)
- `docs/stories/008-skip-library-flag.md` (this file)

**Read:**
- `src/coderef/main.py`
- `src/coderef/api_client.py`
- `README.md`
- `docs/core/ARCHITECTURE.md`

**Exclude:**
- No other files modified

## Implementation

### Step 1: Add `--skip-library-detect` flag

Add to CLI command:
```python
@click.option("--skip-library-detect", is_flag=True, help="Skip library auto-detection")
def main(
    question: str | None,
    library: str | None,
    tokens: int,
    version: str | None,
    init: bool,
    debug: bool,
    skip_library_detect: bool,
) -> None:
```

### Step 2: Modify `_resolve_library()`

Add parameter and logic to skip detection:
```python
def _resolve_library(
    formatter: OutputFormatter,
    resolver: LibraryResolver,
    question: str,
    library: str | None,
    version: str | None,
    skip_detect: bool = False,
) -> str | None:
    """Resolve library ID from input or auto-detect.

    Args:
        formatter: OutputFormatter for messages
        resolver: LibraryResolver for detection
        question: User's question
        library: Explicit library ID (if provided)
        version: Library version (if provided)
        skip_detect: Skip library auto-detection

    Returns:
        Library ID string, or None if skipping
    """
    if skip_detect:
        return None
    
    # ... rest of existing logic
```

### Step 3: Update `Context7Client.get_context()`

Make library_id optional:
```python
def get_context(
    self, 
    library_id: str | None = None,
    query: str, 
    tokens: int = 5000
) -> dict:
    """Fetch documentation context for a library.

    Args:
        library_id: Context7 library ID (e.g., /facebook/react). Optional.
        query: The question or task to get docs for
        tokens: Maximum tokens to return (1000-50000)

    Returns:
        Dictionary containing formatted documentation
    """
    if not 1000 <= tokens <= 50000:
        raise ValueError("Tokens must be between 1000 and 50000")

    params = {"query": query, "tokens": tokens}
    if library_id:
        params["libraryId"] = library_id

    return self._make_request("GET", "context", params)
```

### Step 4: Update `main()` to Handle None library_id

Conditional API call:
```python
library_id = _resolve_library(formatter, resolver, question, library, version, skip_library_detect)

if library_id:
    context = api_client.get_context(library_id, question, tokens)
else:
    # Call without libraryId, let Context7 handle library resolution
    context = api_client.get_context(None, question, tokens)

formatter.format_response(context, library_id or "Auto-detected")
```

### Step 5: Update README

Add documentation for new flag and behavior:

```markdown
**Option: Skip library detection**

```bash
# Let Context7 handle library resolution internally
coderef "How do I use React hooks?" --skip-library-detect

# With library (overrides flag)
coderef "React hooks" --skip-library-detect --library /facebook/react
```

### Step 6: Update ARCHITECTURE.md

Add note about new behavior:

```markdown
### Library Detection

coderef supports two modes:

1. **Explicit library mode** (default): Specify `--library` flag
   - Requires library ID in format `/org/repo`
   - Auto-detection skipped when flag provided
   - Uses `/api/v2/context?libraryId=...` endpoint

2. **Auto-detection mode** (removed): Attempts to detect library from question
   - If fails, CLI requires explicit `--library` flag
   - This mode is DEPRECATED due to Context7 capabilities

3. **Skip detection mode** (new): Let Context7 handle library resolution
   - Use `--skip-library-detect` flag
   - Calls `/api/v2/context` without `libraryId` parameter
   - Context7 resolves library internally using natural language processing
   - Recommended for generic questions like "C++ lambda functions"
```

## Testing

### Test 1: Natural language query with skip flag
```bash
coderef "C++ lambda functions" --skip-library-detect
```
Expected: Calls API without libraryId, Context7 resolves to AWS Lambda docs

### Test 2: Explicit library still works
```bash
coderef "React hooks" --skip-library-detect --library /facebook/react
```
Expected: Uses explicit library, ignores skip flag

### Test 3: Explicit library without skip (default behavior)
```bash
coderef "React hooks" --library /facebook/react
```
Expected: Works as before

### Test 4: Query without library flag fails without skip
```bash
coderef "unknown framework query"
```
Expected: Shows "Could not detect library" error

## Notes

- Context7 API accepts queries without libraryId parameter
- Context7 Chat/MCP server handles library resolution using natural language
- Auto-detection mode is effectively removed (still in code but bypassed by skip flag)
- Backward compatible: existing `--library` flag still works
- Error messages updated to guide users to use `--skip-library-detect` for generic queries
