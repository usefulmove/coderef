# 002 API Client and Library Resolution

## Goal
Implement the Context7 API client and library resolver to fetch documentation and detect libraries from questions.

## Acceptance Criteria

- [x] `Context7Client` class can make authenticated requests to Context7 API
- [x] `search_library()` method calls `/api/v2/libs/search` and returns results
- [x] `get_context()` method calls `/api/v2/context` and returns documentation
- [x] Proper error handling for 401, 403, 404, 429, 500 status codes
- [x] `LibraryResolver` can extract keywords from questions
- [x] `LibraryResolver` can search for libraries and calculate confidence scores
- [x] `LibraryResolver` returns best match if confidence ≥ 0.8, None otherwise
- [x] All code follows STANDARDS.md conventions

## Context Scope

**Write:**
- `src/api_client.py`
- `src/library_resolver.py`
- `tests/test_api_client.py`
- `tests/test_library_resolver.py`

**Read:**
- `docs/core/ARCHITECTURE.md`
- `docs/core/STANDARDS.md`
- `src/config.py` (for API key access)

**Exclude:**
- `src/output.py` (Story 003)
- Integration with main CLI (Story 003)

## Approach

### Step 1: Context7Client Base
- Create `Context7Client` class with:
  - `__init__(api_key: str)` - store API key, set base URL
  - `_make_request(method: str, endpoint: str, params: dict) -> dict` - private helper
  - `validate_api_key() -> bool` - test key with API call
- Implement base URL: `https://context7.com/api/v2`
- Set request timeout to 10 seconds
- Add custom exceptions: `APIError`, `AuthError`, `RateLimitError`, `NotFoundError`

### Step 2: search_library()
- Implement `search_library(library_name: str, query: str) -> list[dict]`
- Call `/api/v2/libs/search` with query params
- Return `results` array from response
- Handle errors:
  - 401/403 → raise `AuthError`
  - 429 → raise `RateLimitError`
  - 500+ → raise `APIError`

### Step 3: get_context()
- Implement `get_context(library_id: str, query: str, tokens: int = 5000) -> dict`
- Validate tokens range (1000-50000)
- Call `/api/v2/context` with query params
- Return full response dict
- Handle errors same as search_library()
- Add 404 handling → raise `NotFoundError`

### Step 4: LibraryResolver Keyword Extraction
- Create `LibraryResolver` class with:
  - `__init__(api_client: Context7Client)`
  - `extract_keywords(question: str) -> list[str]`
- Build keyword mapping in `__init__`:
  - Languages: python, javascript, typescript, c++, java, go, rust, swift, kotlin, ruby, php, csharp
  - Frameworks: react, vue, angular, svelte, next.js, nuxt, django, flask, fastapi, express, spring, rails, laravel
  - Libraries: numpy, pandas, scikit-learn, tensorflow, pytorch, lodash, moment, axios, requests, httpx, jinja2, jinja
- Extract keywords by scanning question for known terms (case-insensitive)
- Return list of found keywords (max 3, prioritized by order in question)

### Step 5: Library Resolution Logic
- Implement `resolve_from_question(question: str) -> tuple[str, float]`
  1. Extract keywords using `extract_keywords()`
  2. For each keyword, call `api_client.search_library()`
  3. Calculate confidence score for each result
  4. Return best match with highest score
- Implement `calculate_confidence(match: dict, keywords: list[str]) -> float`
  - Name match: 0.5 if keyword appears in library name, 0 if not
  - Description relevance: 0.3 if keyword appears in description
  - Popularity score: 0.2 normalized from popularity metric
  - Return sum (0.0-1.0)
- Implement `get_confidence_level(score: float) -> str`:
  - ≥0.8: "high"
  - ≥0.5: "medium"
  - <0.5: "low"

### Step 6: Main Resolution Method
- Refine `resolve_from_question()`:
  - If no keywords found, return (None, 0.0)
  - If multiple keywords, use first match
  - If best score < 0.8, return (None, score) to indicate uncertainty
  - If best score ≥ 0.8, return (library_id, score)

### Step 7: Tests for API Client
- Test `Context7Client`:
  - `test_init_stores_api_key`
  - `test_make_request_adds_auth_header`
  - `test_search_library_calls_correct_endpoint`
  - `test_search_library_returns_results`
  - `test_search_library_handles_401_raises_auth_error`
  - `test_search_library_handles_429_raises_rate_limit_error`
  - `test_get_context_validates_token_range`
  - `test_get_context_calls_correct_endpoint`
  - `test_get_context_handles_404_raises_not_found_error`
  - `test_validate_api_key_returns_true_for_valid_key`
  - `test_validate_api_key_returns_false_for_invalid_key`
  - `test_network_error_raises_api_error`
- Mock `requests.get()` and `requests.post()` with `pytest-mock`

### Step 8: Tests for Library Resolver
- Test `LibraryResolver`:
  - `test_init_creates_keyword_map`
  - `test_extract_keywords_finds_language_names`
  - `test_extract_keywords_finds_framework_names`
  - `test_extract_keywords_finds_library_names`
  - `test_extract_keywords_returns_empty_list_no_matches`
  - `test_extract_keywords_is_case_insensitive`
  - `test_extract_keywords_limits_to_3_results`
  - `test_extract_keywords_uses_word_boundaries`
  - `test_calculate_confidence_scores_name_match_highly`
  - `test_calculate_confidence_scores_description_match_moderately`
  - `test_calculate_confidence_cap_at_1_0`
  - `test_get_confidence_level_high`
  - `test_get_confidence_level_medium`
  - `test_get_confidence_level_low`
  - `test_resolve_from_question_returns_high_confidence_match`
  - `test_resolve_from_question_returns_none_for_low_confidence`
  - `test_resolve_from_question_returns_none_no_keywords`
  - `test_resolve_from_question_handles_api_errors_gracefully`
- Mock `Context7Client.search_library()` with test data

### Step 9: Error Handling Refinement
- Ensure all API errors have clear messages
- Add HTTP status codes to error messages
- Include retry-after header in rate limit error if present

## Notes

**Implementation Decisions:**
- Used `requests.exceptions.HTTPError` with `response` attribute for proper error handling
- Used `getattr()` to safely access `e.response` to handle edge cases
- Keyword map includes 11 languages, 13 frameworks, 12 libraries
- Confidence scoring: name match (0.5) + description match (0.3) + popularity (max 0.2)
- Popularity is normalized: min(popularity / 100.0, 0.2)
- Used word boundaries (`\bkeyword\b`) for precise keyword matching
- Keywords are case-insensitive for better matching
- Limited to 3 keywords to avoid excessive API calls

**API Integration:**
- Base URL: `https://context7.com/api/v2`
- Auth header: `Authorization: Bearer {api_key}`
- Timeout: 10 seconds
- Token limit range: 1000-50000 (Context7 constraint)

**Error Handling:**
- Custom exceptions for different error types
- Clear, actionable error messages
- HTTP status codes included in messages
- Retry-after header captured for rate limits

**Test Results:**
- API client: 11 tests passing
- Library resolver: 18 tests passing
- Total: 29 tests passing

**File Structure:**
- `src/coderef/api_client.py` - API client with error handling
- `src/coderef/library_resolver.py` - Library detection and confidence scoring

**Learnings:**
- Mocking HTTPError requires setting `response` attribute
- Word boundary regex prevents partial matches (e.g., "num" matching "numpy")
- Confidence scoring needs careful tuning to balance precision/recall
- Popularity normalization prevents bias toward popular libraries only
