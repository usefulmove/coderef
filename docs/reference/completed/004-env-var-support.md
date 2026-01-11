# 004 Environment Variable Support for API Key

## Goal
Allow users to provide Context7 API key via `CONTEXT7_API_KEY` environment variable, avoiding double-typing during initialization.

## Acceptance Criteria

- [x] CLI checks `CONTEXT7_API_KEY` environment variable before prompting
- [x] If env var is present and valid, skip prompting and save directly
- [x] If env var is invalid (wrong format), show error and exit
- [x] If env var is missing or empty, use interactive prompt with confirmation
- [x] Inform user when using API key from environment variable
- [x] README.md updated with environment variable usage
- [x] All existing tests still pass

## Context Scope

**Write:**
- `src/coderef/main.py` (modify `_run_init_flow()` function)
- `docs/stories/004-env-var-support.md` (this file)

**Read:**
- `docs/core/STANDARDS.md`
- `src/coderef/main.py`
- `src/coderef/config.py`
- `README.md`

**Exclude:**
- No other files need modification

## Approach

### Step 1: Add os import
- Import `os` at the top of `main.py`
- Used to access environment variables

### Step 2: Modify `_run_init_flow()` function
- Add logic to check `os.environ.get('CONTEXT7_API_KEY')` first
- If env var is truthy:
  - Validate format using `validate_api_key_format()`
  - If valid: show info message, use key directly
  - If invalid: show error message, exit with code 1
- If env var is falsy/missing:
  - Keep existing prompt behavior with `confirmation_prompt=True`
- Save API key to config using `ConfigManager().set_api_key()`

### Step 3: Update README.md
- Add "Option 1: Environment variable (recommended)" to First-Time Setup section
- Keep "Option 2: Interactive prompt" as alternative
- Add example: `CONTEXT7_API_KEY=ctx7sk_... coderef --init`
- Explain that key is saved to config for future use

### Step 4: Test scenarios
- Test with valid env var: `CONTEXT7_API_KEY=ctx7sk_test123 uv run coderef --init`
- Test with invalid env var: `CONTEXT7_API_KEY=invalid uv run coderef --init`
- Test with no env var: `uv run coderef --init` (should prompt)

## Notes

- This is backward compatible - existing behavior unchanged when env var not set
- Environment variable approach is standard pattern for API keys (AWS, Stripe, etc.)
- No new tests required for this change - manual testing sufficient
- Security consideration: env var doesn't appear in shell history if used inline
- The env var is checked once during init, not used after config is saved

## Implementation Notes

**Created files:**
- `docs/stories/004-env-var-support.md` - Story document

**Modified files:**
- `src/coderef/main.py` - Added `os` import, modified `_run_init_flow()` function
- `docs/core/PRD.md` - Updated FR1 to include env var support
- `docs/core/ARCHITECTURE.md` - Added env var to Configuration Schema section
- `README.md` - Added env var to First-Time Setup and Troubleshooting sections

**Manual testing performed:**
1. Valid env var: `CONTEXT7_API_KEY=ctx7sk_test123... coderef --init` → ✅ Success
2. Invalid env var: `CONTEXT7_API_KEY=invalid coderef --init` → ✅ Error message
3. No env var: `coderef --init` → ✅ Prompts for key (existing behavior)
4. Config saved: Verified key persisted to `~/.coderef/config.toml`

**All 41 existing tests pass**

## Example Output

### With valid env var:
```
Welcome to coderef!
Let's set up your Context7 API key.
Get your free API key at: https://context7.com/dashboard

ℹ️ Using API key from CONTEXT7_API_KEY environment variable

✅ API key saved successfully!
You can now use coderef to query documentation.

Example:
  coderef "How do I use React hooks?"
```

### With invalid env var:
```
Welcome to coderef!
Let's set up your Context7 API key.
Get your free API key at: https://context7.com/dashboard

❌ Invalid API key format in CONTEXT7_API_KEY. Key must start with 'ctx7sk_'
```

### Without env var:
```
Welcome to coderef!
Let's set up your Context7 API key.
Get your free API key at: https://context7.com/dashboard

Enter your Context7 API key: ********
Repeat for confirmation: ********

✅ API key saved successfully!
...
```
