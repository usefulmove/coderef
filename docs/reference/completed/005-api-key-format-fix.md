# 005 Fix API Key Format Validation

## Goal
Fix API key format validation to accept both `ctx7sk-` (actual format) and `ctx7sk_` (legacy assumed format), resolving issue where user's valid key was being rejected.

## Root Cause
The `validate_api_key_format()` function only accepted `ctx7sk_` (underscore), but actual Context7 API keys use `ctx7sk-` (hyphen). The underscore format was an assumption made during Story 001 and never verified against Context7 documentation.

## Acceptance Criteria

- [x] Update `validate_api_key_format()` to accept both `ctx7sk-` and `ctx7sk_` prefixes
- [x] Update docstring to document both formats
- [x] Add tests for hyphen prefix format (actual)
- [x] Add tests for underscore prefix format (legacy)
- [x] Add tests for invalid prefixes
- [x] Update README.md to document both accepted formats
- [x] Verify user's actual key format works
- [x] All tests pass (45 total)

## Context Scope

**Write:**
- `src/coderef/utils.py` (update validation function)
- `tests/test_config.py` (add new test class)
- `README.md` (document both formats)
- `docs/stories/005-api-key-format-fix.md` (this file)

**Read:**
- `src/coderef/utils.py`
- `tests/test_config.py`
- `README.md`
- `docs/core/STANDARDS.md`

**Exclude:**
- No other files modified (per user request to keep error messages simple)

## Implementation

### 1. Update `src/coderef/utils.py`

**Line 7 (docstring):**
```python
# Changed from:
"""Validate that API key starts with ctx7sk_ prefix."""

# To:
"""Validate that API key starts with ctx7sk_ or ctx7sk- prefix."""
```

**Line 15 (validation logic):**
```python
# Changed from:
return api_key.startswith("ctx7sk_") and len(api_key) > 10

# To:
return (api_key.startswith("ctx7sk_") or api_key.startswith("ctx7sk-")) and len(api_key) > 10
```

### 2. Add Tests to `tests/test_config.py`

**Import added:**
```python
from coderef.utils import validate_api_key_format
```

**New test class `TestValidateApiKeyFormat` with 4 test methods:**

1. `test_validate_api_key_format_accepts_hyphen_prefix` - Tests `ctx7sk-...` format
2. `test_validate_api_key_format_accepts_underscore_prefix` - Tests `ctx7sk_...` format
3. `test_validate_api_key_format_rejects_invalid_prefix` - Tests rejection of bad prefixes
4. `test_validate_api_key_format_rejects_short_key` - Tests rejection of short keys

### 3. Update `README.md`

**First-Time Setup section, Option 1:**

Added note about accepted formats:
```markdown
This is the fastest method. Accepted formats:
- `ctx7sk-...` (current format with hyphen)
- `ctx7sk_...` (legacy format with underscore)
```

## Manual Testing

### Test 1: Hyphen format (actual)
```bash
CONTEXT7_API_KEY=ctx7sk-5a7c7f69-332e-4fd6-af7c-6b510ace592d coderef --init
```
**Result:** ✅ Saved successfully

### Test 2: Underscore format (legacy)
```bash
CONTEXT7_API_KEY=ctx7sk_test_underscore_format coderef --init
```
**Result:** ✅ Saved successfully

### Test 3: Invalid format
```bash
CONTEXT7_API_KEY=invalid_format coderef --init
```
**Result:** ✅ Error: "Invalid API key format in CONTEXT7_API_KEY. Key must start with 'ctx7sk_'"

## Test Results

All 45 tests pass:
- 11 API client tests
- 16 config tests (12 + 4 new)
- 18 library resolver tests

## Notes

- Error messages were NOT updated (per user request) to keep them simple
- Backward compatibility maintained for legacy `ctx7sk_` format
- Primary format is `ctx7sk-...` (hyphen)
- No changes to API client or main.py error handling
- User's original issue (API key rejection) is now resolved
