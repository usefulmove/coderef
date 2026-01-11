"""Tests for LibraryResolver."""

from unittest.mock import Mock, patch

import pytest

from coderef.api_client import Context7Client
from coderef.library_resolver import LibraryResolver


class TestLibraryResolver:
    """Test LibraryResolver class."""

    def test_init_creates_keyword_map(self):
        """Test that init creates keyword mapping."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        assert "python" in resolver.all_keywords
        assert "react" in resolver.all_keywords
        assert "numpy" in resolver.all_keywords
        assert len(resolver.all_keywords) > 20

    def test_extract_keywords_finds_language_names(self):
        """Test that extract_keywords finds language names."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        keywords = resolver.extract_keywords(
            "How do I use Python and JavaScript together?"
        )

        assert "python" in keywords
        assert "javascript" in keywords

    def test_extract_keywords_finds_framework_names(self):
        """Test that extract_keywords finds framework names."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        keywords = resolver.extract_keywords("How do I use React hooks in Next.js?")

        assert "react" in keywords
        assert "next.js" in keywords

    def test_extract_keywords_finds_library_names(self):
        """Test that extract_keywords finds library names."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        keywords = resolver.extract_keywords("How do I use NumPy and Pandas?")

        assert "numpy" in keywords
        assert "pandas" in keywords

    def test_extract_keywords_returns_empty_list_no_matches(self):
        """Test that extract_keywords returns empty list for no matches."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        keywords = resolver.extract_keywords("How do I loop through arrays?")

        assert keywords == []

    def test_extract_keywords_is_case_insensitive(self):
        """Test that extract_keywords is case insensitive."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        keywords = resolver.extract_keywords("How do I use REACT and PYTHON?")

        assert "react" in keywords
        assert "python" in keywords

    def test_extract_keywords_limits_to_3_results(self):
        """Test that extract_keywords limits results to 3."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        question = "python javascript typescript go rust swift"
        keywords = resolver.extract_keywords(question)

        assert len(keywords) == 3

    def test_extract_keywords_uses_word_boundaries(self):
        """Test that extract_keywords uses word boundaries."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        keywords = resolver.extract_keywords("How do I use numpy?")

        assert "numpy" in keywords
        assert "num" not in keywords

    def test_calculate_confidence_scores_name_match_highly(self):
        """Test that calculate_confidence scores name match highly."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        match = {
            "name": "react",
            "description": "A JavaScript library for building UIs",
            "popularity": 90.0,
        }
        score = resolver.calculate_confidence(match, ["react"])

        assert score >= 0.5
        assert score <= 1.0

    def test_calculate_confidence_scores_description_match_moderately(self):
        """Test that calculate_confidence scores description match moderately."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        match = {
            "name": "some-lib",
            "description": "A Python library for data analysis",
            "popularity": 10.0,
        }
        score = resolver.calculate_confidence(match, ["python"])

        assert score >= 0.3
        assert score < 0.5

    def test_calculate_confidence_cap_at_1_0(self):
        """Test that calculate_confidence caps score at 1.0."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        match = {
            "name": "react",
            "description": "React React React React React React",
            "popularity": 100.0,
        }
        score = resolver.calculate_confidence(match, ["react"])

        assert score <= 1.0

    def test_get_confidence_level_high(self):
        """Test that get_confidence_level returns 'high' for high scores."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        assert resolver.get_confidence_level(0.9) == "high"
        assert resolver.get_confidence_level(0.8) == "high"

    def test_get_confidence_level_medium(self):
        """Test that get_confidence_level returns 'medium' for medium scores."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        assert resolver.get_confidence_level(0.7) == "medium"
        assert resolver.get_confidence_level(0.5) == "medium"

    def test_get_confidence_level_low(self):
        """Test that get_confidence_level returns 'low' for low scores."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        assert resolver.get_confidence_level(0.4) == "low"
        assert resolver.get_confidence_level(0.0) == "low"

    def test_resolve_from_question_returns_high_confidence_match(self):
        """Test that resolve_from_question returns library for high confidence."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        mock_client.search_library.return_value = [
            {
                "id": "/facebook/react",
                "name": "react",
                "description": "React JavaScript library",
                "popularity": 95.0,
            }
        ]

        library_id, confidence = resolver.resolve_from_question(
            "How do I use React hooks?"
        )

        assert library_id == "/facebook/react"
        assert confidence >= 0.8

    def test_resolve_from_question_returns_match_for_low_confidence(self):
        """Test that resolve_from_question returns library even for low confidence."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        # "python" is a keyword, so it will search
        # But the result "unknown" matches nothing, so score will be low (just popularity)
        mock_client.search_library.return_value = [
            {
                "id": "/some/unknown",
                "name": "unknown",
                "description": "Unknown library",
                "popularity": 10.0,
            }
        ]

        library_id, confidence = resolver.resolve_from_question("How do I use python?")

        assert library_id == "/some/unknown"
        assert confidence < 0.5

    def test_resolve_from_question_returns_none_no_keywords(self):
        """Test that resolve_from_question returns None when no keywords found."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        library_id, confidence = resolver.resolve_from_question(
            "How do I write a function?"
        )

        assert library_id is None
        assert confidence == 0.0
        mock_client.search_library.assert_not_called()

    def test_resolve_from_question_handles_api_errors_gracefully(self):
        """Test that resolve_from_question handles API errors gracefully."""
        mock_client = Mock(spec=Context7Client)
        resolver = LibraryResolver(mock_client)

        mock_client.search_library.side_effect = Exception("API error")

        library_id, confidence = resolver.resolve_from_question("How do I use React?")

        assert library_id is None
        assert confidence == 0.0
