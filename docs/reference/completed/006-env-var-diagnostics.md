# 006 Improve Environment Variable Detection and Error Messaging

## Goal
Improve environment variable detection for API key and add better error messaging to help users diagnose configuration issues.

## Root Cause
Users experiencing issues where:
1. Environment variable is set in shell profile but not detected by coderef
2. Error messages don't help identify if env var is set but invalid vs. not set at all
3. No guidance on how to verify env var is loaded

## Acceptance Criteria

- [x] Add debug logging to show when env var is being checked
- [x] Improve error message to distinguish between "not set" and "invalid format"
- [x] Add env var verification guidance to error messages
- [x] Add troubleshooting section to README for env var issues
- [x] Test with env var in different states (set, not set, invalid)

## Context Scope

**Write:**
- `src/coderef/main.py` (add debug logging and improve error messages)
- `README.md` (add env var troubleshooting section)
- `docs/stories/006-env-var-diagnostics.md` (this file)

**Read:**
- `src/coderef/main.py`
- `src/coderef/utils.py`
- `README.md`

**Exclude:**
- No other files modified

## Implementation

### Step 1: Add Debug Logging in `_run_init_flow()`

Add verbose flag or environment variable to enable debug output:

```python
# At top of _run_init_flow()
debug = os.environ.get('DEBUG', '').lower() == 'true'

if debug:
    formatter.print(f"[DEBUG] Checking environment variable CONTEXT7_API_KEY...")
    formatter.print(f"[DEBUG] Env var present: {api_key is not None}")
    if api_key:
        formatter.print(f"[DEBUG] Env var value: {api_key[:10]}...{api_key[-4:]}")
```

### Step 2: Improve Error Messages in `_run_init_flow()`

When env var is invalid:
```python
# Current:
formatter.print_error("Invalid API key format in CONTEXT7_API_KEY. Key must start with 'ctx7sk_'")

# Improved:
formatter.print_error(
    "Invalid API key format in CONTEXT7_API_KEY.\n"
    "Key must start with 'ctx7sk-' or 'ctx7sk_'.\n\n"
    "Verify your key with: echo $CONTEXT7_API_KEY"
)
```

When env var is not set (fallback to prompt):
```python
# Add before prompt:
formatter.print_info(
    "Environment variable CONTEXT7_API_KEY not found.\n"
    "You can set it in your shell profile or enter it below."
)
```

### Step 3: Update README Troubleshooting Section

Add new subsection:

```markdown
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
```

### Step 4: Add DEBUG flag support

Add `--debug` flag to CLI:

```python
@click.option("--debug", is_flag=True, help="Enable debug output")
def main(question: str | None, library: str | None, tokens: int, version: str | None, init: bool, debug: bool):
```

Pass debug flag to functions that need it.

## Testing

### Test 1: Env var set and valid
```bash
CONTEXT7_API_KEY=ctx7sk-test123 DEBUG=true coderef --init
```
Expected: Shows debug logs, uses env var

### Test 2: Env var set and invalid
```bash
CONTEXT7_API_KEY=invalid DEBUG=true coderef --init
```
Expected: Shows debug logs, helpful error message

### Test 3: Env var not set
```bash
DEBUG=true coderef --init
```
Expected: Shows debug logs, prompts for key

### Test 4: After init without env var
```bash
coderef "test query"
```
Expected: Shows "Configuration not found" error with guidance

## Notes

- Debug mode only activated with `--debug` flag or `DEBUG=true` env var
- Error messages are more actionable with specific verification steps
- Troubleshooting guide covers common shell configuration issues
- No breaking changes to existing behavior

## Implementation Notes

**Modified files:**
- `src/coderef/main.py` - Added `--debug` flag, updated `_run_init_flow()` with debug logging and improved error messages
- `README.md` - Added troubleshooting section for env var issues, updated flags table and command reference

**Changes to main.py:**
1. Added `--debug` flag to CLI command (line 40)
2. Updated `_run_init_flow()` signature to accept `debug` parameter (line 118)
3. Added debug logging before env var check (lines 127-129)
4. Added debug logging for env var state (lines 131-135)
5. Improved error message for missing env var with guidance (lines 138-141)
6. Improved error message for invalid env var with verification steps (lines 144-149)
7. Updated error messages to mention both `ctx7sk-` and `ctx7sk_` formats (lines 148, 156)

**Changes to README.md:**
1. Added "Environment variable not detected" subsection to Troubleshooting with 5 detailed steps
2. Updated "Invalid API key" section to mention both formats
3. Added `--debug` to flags table
4. Added debug examples to command reference

**Manual Testing:**
1. Env var not set, DEBUG=true: ✅ Shows "[DEBUG] Checking for CONTEXT7_API_KEY environment variable..." and "[DEBUG] Environment variable not found"
2. Env var not set, --debug flag: ✅ Works the same as DEBUG=true
3. Env var set and valid, DEBUG=true: ✅ Shows "[DEBUG] Environment variable found: ctx7sk-test...456" and uses it
4. Env var set and invalid, DEBUG=true: ✅ Shows improved error message with verification steps

**All 45 tests pass** - No regressions introduced
