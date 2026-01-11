"""Context7 API client for fetching documentation."""

import requests

BASE_URL = "https://context7.com/api/v2"
TIMEOUT = 10


class APIError(Exception):
    """Base API error."""

    pass


class AuthError(APIError):
    """Authentication error (401/403)."""

    pass


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""

    pass


class NotFoundError(APIError):
    """Library not found (404)."""

    pass


class Context7Client:
    """Client for Context7 API."""

    def __init__(self, api_key: str):
        """Initialize Context7 client.

        Args:
            api_key: Context7 API key
        """
        self.api_key = api_key
        self.base_url = BASE_URL
        self.timeout = TIMEOUT

    def _make_request(
        self, method: str, endpoint: str, params: dict | None = None
    ) -> dict | str:
        """Make HTTP request to API.

        Args:
            method: HTTP method ('GET' or 'POST')
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dict, or text content if not JSON

        Raises:
            AuthError: If authentication fails
            RateLimitError: If rate limit exceeded
            NotFoundError: If resource not found
            APIError: For other API errors
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(
                method, url, headers=headers, params=params, timeout=self.timeout
            )
            response.raise_for_status()

            if "application/json" in response.headers.get("Content-Type", ""):
                return response.json()
            return response.text

        except requests.HTTPError as e:
            status_code = getattr(e.response, "status_code", None)

            if status_code in (401, 403):
                raise AuthError(
                    "Invalid API key. Get a key at https://context7.com/dashboard"
                ) from e
            if status_code == 404:
                raise NotFoundError(
                    "Library not found. Check the --library flag or try a different query."
                ) from e
            if status_code == 429:
                headers = getattr(e.response, "headers", {})
                retry_after = headers.get("Retry-After", "unknown")
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds."
                ) from e
            if status_code is not None and status_code >= 500:
                raise APIError(
                    f"API server error ({status_code}). Please try again later."
                ) from e

            raise APIError(f"HTTP error {status_code or 'unknown'}: {e}") from e
        except requests.RequestException as e:
            raise APIError(f"Network error: {e}") from e

    def validate_api_key(self) -> bool:
        """Validate API key by making a simple request.

        Returns:
            True if key is valid, False otherwise
        """
        try:
            self._make_request(
                "GET", "libs/search", {"libraryName": "react", "query": "test"}
            )
            return True
        except AuthError:
            return False
        except APIError:
            return True

    def search_library(self, library_name: str, query: str) -> list[dict]:
        """Search for a library in Context7.

        Args:
            library_name: Name of library to search for
            query: Query for relevance ranking

        Returns:
            List of matching libraries with metadata

        Raises:
            AuthError: If authentication fails
            RateLimitError: If rate limit exceeded
            APIError: For other errors
        """
        params = {"libraryName": library_name, "query": query}
        response = self._make_request("GET", "libs/search", params)

        if isinstance(response, str):
            raise APIError("Unexpected text response from search API")

        return response.get("results", [])

    def get_context(
        self, library_id: str | None = None, query: str = "", tokens: int = 5000
    ) -> dict:
        """Fetch documentation context for a library.

        Args:
            library_id: Context7 library ID (e.g., /facebook/react). Optional.
            query: The question or task to get docs for
            tokens: Maximum tokens to return (1000-50000)

        Returns:
            Dictionary containing formatted documentation

        Raises:
            ValueError: If tokens outside valid range
            AuthError: If authentication fails
            RateLimitError: If rate limit exceeded
            NotFoundError: If library not found
            APIError: For other errors
        """
        if not 1000 <= tokens <= 50000:
            raise ValueError("Tokens must be between 1000 and 50000")

        params = {"query": query, "tokens": tokens}
        if library_id:
            params["libraryId"] = library_id

        response = self._make_request("GET", "context", params)

        if isinstance(response, str):
            return {"context": response, "examples": []}

        return response
