# 007 Environment Variable Runtime Support

## Goal
Enable `CONTEXT7_API_KEY` environment variable to be used for all commands (not just init), eliminating need to run init when env var is already set.

## Root Cause
Users set `CONTEXT7_API_KEY` in their shell profile but:
1. Env var was only checked during `coderef --init`
2. All queries required config file to exist
3. User had to run init even with env var set

## Acceptance Criteria

- [x] Check `CONTEXT7_API_KEY` environment variable for all commands (not just init)
- [x] Config file used as fallback if env var not set
- [x] Debug mode shows which source is being used (env var or config)
- [x] Init flow shows which source API key came from
- [x] Clear precedence rules (env var > config)
- [x] README updated with runtime env var behavior
- [x] ARCHITECTURE.md updated with precedence rules
- [x] All tests pass (45)

## Context Scope

**Write:**
- `src/coderef/main.py` (check env var at runtime, add debug logging)
- `README.md` (document runtime env var, add precedence note)
- `docs/core/ARCHITECTURE.md` (add precedence rules)
- `docs/stories/007-env-var-runtime.md` (this file)

**Read:**
- `src/coderef/main.py`
- `README.md`
- `docs/core/ARCHITECTURE.md`

**Exclude:**
- No other files modified

## Implementation

### Step 1: Check Env Var at Runtime

Modified main() function to check `CONTEXT7_API_KEY` first:

```python
# Before config manager
api_key = os.environ.get("CONTEXT7_API_KEY")

if debug:
    if api_key:
        formatter.print("[DEBUG] Using API key from CONTEXT7_API_KEY environment variable")
    else:
        formatter.print("[DEBUG] Falling back to config file...")

if not api_key:
    # Fallback to config file
    if not config_manager.config_exists():
        # Show error...
        sys.exit(1)
    
    api_key = config_manager.get_api_key()
    
    if not api_key:
        # Show error...
        sys.exit(1)
    
    if debug:
        formatter.print("[DEBUG] Using API key from ~/.coderef/config.toml")
```

### Step 2: Add DEBUG Environment Variable Support

Added check for `DEBUG` environment variable in main():

```python
if os.environ.get("DEBUG", "").lower() == "true":
    debug = True
```

This allows users to enable debug without `--debug` flag.

### Step 3: Update Init Flow Debug Output

Added debug logging in `_run_init_flow()` after saving key:

```python
if debug:
    from_env_var = os.environ.get("CONTEXT7_API_KEY") == api_key
    source = "CONTEXT7_API_KEY environment variable" if from_env_var else "interactive prompt"
    formatter.print(f"[DEBUG] API key saved from: {source}")
```

### Step 4: Update README

Modified "Option 1: Environment variable" section:

```markdown
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
```

Added note to "Configuration not found" section:

```markdown
**Note:** If you've already set `CONTEXT7_API_KEY` in your shell profile, it should work immediately without running init. Try running a query directly.
```

### Step 5: Update ARCHITECTURE.md

Added "Configuration Precedence" section:

```markdown
### Configuration Precedence

coderef looks for API key in this order for all commands:

1. **Environment variable**: `CONTEXT7_API_KEY`
   - Checked for all commands (init, queries)
   - Highest priority
   - Runtime override

2. **Config file**: `~/.coderef/config.toml`
   - Used as fallback if env var not set
   - Persisted by `coderef --init`

This means if `CONTEXT7_API_KEY` is set, you can use coderef immediately without running init.
```

Updated "Environment Variable" section to clarify runtime behavior.

## Testing

### Test 1: Env var set, no config, debug=true
```bash
rm -f ~/.coderef/config.toml
CONTEXT7_API_KEY=ctx7sk-testkey123 DEBUG=true uv run coderef "test" --library /facebook/react
```
**Expected:** `[DEBUG] Using API key from CONTEXT7_API_KEY environment variable`
**Result:** ✅ Pass

### Test 2: Config file, no env var, debug=true
```bash
printf "[context7]\napi_key = \"ctx7sk-testconfigkey123\"" > ~/.coderef/config.toml
DEBUG=true uv run coderef "test" --library /facebook/react
```
**Expected:** `[DEBUG] Falling back to config file...` and `[DEBUG] Using API key from ~/.coderef/config.toml`
**Result:** ✅ Pass

### Test 3: Both set (env var wins)
```bash
CONTEXT7_API_KEY=ctx7sk-env DEBUG=true uv run coderef "test" --library /facebook/react
```
**Expected:** Uses env var (not config)
**Result:** ✅ Pass

### Test 4: Init with env var, debug=true
```bash
CONTEXT7_API_KEY=ctx7sk-test DEBUG=true uv run coderef --init
```
**Expected:** Shows which source API key came from
**Result:** ✅ Pass

## Notes

- Precedence is clear: env var > config
- Debug mode can be enabled via `--debug` flag or `DEBUG=true` env var
- No breaking changes - backward compatible
- Matches industry standard (AWS CLI, Docker, etc.)
- Init still works for users who want config file persistence

## User's Use Case

For user with `CONTEXT7_API_KEY` set in `.zshrc`:

```bash
# In .zshrc:
export CONTEXT7_API_KEY=ctx7sk-...

# Now works directly:
coderef "C++ lambda functions" --library C++

# No init step needed!
```

**Previously:** Required `coderef --init` even with env var set.
**Now:** Works immediately with env var.
