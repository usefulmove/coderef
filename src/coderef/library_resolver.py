"""Library resolver for detecting relevant libraries from questions."""

import re
from typing import TypedDict

from .api_client import Context7Client


class LibraryMatch(TypedDict):
    """A library match from search results."""

    id: str
    name: str
    description: str
    popularity: float
    confidence: float


class LibraryResolver:
    """Resolves libraries from questions using Context7 API."""

    def __init__(self, api_client: Context7Client):
        """Initialize library resolver.

        Args:
            api_client: Context7 API client
        """
        self.api_client = api_client

        self.keyword_map = {
            "languages": [
                "python",
                "javascript",
                "typescript",
                "c++",
                "java",
                "go",
                "rust",
                "swift",
                "kotlin",
                "ruby",
                "php",
                "csharp",
            ],
            "frameworks": [
                "react",
                "vue",
                "angular",
                "svelte",
                "next.js",
                "nuxt",
                "django",
                "flask",
                "fastapi",
                "express",
                "spring",
                "rails",
                "laravel",
            ],
            "libraries": [
                "numpy",
                "pandas",
                "scikit-learn",
                "tensorflow",
                "pytorch",
                "lodash",
                "moment",
                "axios",
                "requests",
                "httpx",
                "jinja2",
                "jinja",
            ],
        }

        self.all_keywords = (
            self.keyword_map["languages"]
            + self.keyword_map["frameworks"]
            + self.keyword_map["libraries"]
        )

    def extract_keywords(self, question: str) -> list[str]:
        """Extract library/framework/language keywords from question.

        Args:
            question: User's question

        Returns:
            List of found keywords (max 3)
        """
        question_lower = question.lower()
        found = []

        for keyword in self.all_keywords:
            escaped = re.escape(keyword)

            # Start boundary
            if keyword[0].isalnum() or keyword[0] == "_":
                pattern = r"\b" + escaped
            else:
                pattern = r"(?<!\w)" + escaped

            # End boundary
            if keyword[-1].isalnum() or keyword[-1] == "_":
                pattern += r"\b"
            else:
                pattern += r"(?!\w)"

            if re.search(pattern, question_lower):
                found.append(keyword)

        return found[:3]

    def calculate_confidence(self, match: dict, keywords: list[str]) -> float:
        """Calculate confidence score for a library match.

        Args:
            match: Library match from API
            keywords: Keywords found in question

        Returns:
            Confidence score (0.0-1.0)
        """
        name = match.get("name", match.get("title", "")).lower()
        description = match.get("description", "").lower()
        popularity = match.get("popularity", 0.0)

        score = 0.0

        for keyword in keywords:
            if keyword in name:
                score += 0.5
            if keyword in description:
                score += 0.3

        if len(keywords) > 0:
            avg_popularity = min(popularity / 100.0, 0.2)
            score += avg_popularity

        return min(score, 1.0)

    def get_confidence_level(self, score: float) -> str:
        """Get confidence level label.

        Args:
            score: Confidence score

        Returns:
            "high", "medium", or "low"
        """
        if score >= 0.8:
            return "high"
        if score >= 0.5:
            return "medium"
        return "low"

    def resolve_from_question(self, question: str) -> tuple[str | None, float]:
        """Resolve library from question.

        Args:
            question: User's question

        Returns:
            Tuple of (library_id, confidence_score)
            Returns (None, 0.0) if no confident match found
        """
        keywords = self.extract_keywords(question)

        if not keywords:
            return None, 0.0

        all_results = []
        for keyword in keywords:
            try:
                results = self.api_client.search_library(keyword, question)
                for result in results:
                    result["confidence"] = self.calculate_confidence(result, keywords)
                    all_results.append(result)
            except Exception:
                continue

        if not all_results:
            return None, 0.0

        best_match = max(all_results, key=lambda x: x.get("confidence", 0.0))
        confidence = best_match.get("confidence", 0.0)
        library_id = best_match.get("id")

        return library_id, confidence
