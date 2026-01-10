"""Tests for the coderef agent."""

from unittest.mock import MagicMock, patch

import pytest


class TestQuery:
    """Tests for the query function."""

    def test_query_returns_text_content(self):
        """Should extract text from response content blocks."""
        mock_response = MagicMock()
        mock_block = MagicMock()
        mock_block.text = "```python\nprint('hello')\n```\nPrints hello."
        mock_response.content = [mock_block]

        with patch("coderef.agent.anthropic.Anthropic") as mock_client:
            mock_client.return_value.beta.messages.create.return_value = mock_response

            from coderef.agent import query

            result = query("Python print hello")

        assert "print('hello')" in result

    def test_query_concatenates_multiple_text_blocks(self):
        """Should concatenate all text blocks from response."""
        mock_response = MagicMock()
        mock_tool_block = MagicMock(spec=[])  # No text attr
        mock_text_block1 = MagicMock()
        mock_text_block1.text = "Part 1. "
        mock_text_block2 = MagicMock()
        mock_text_block2.text = "Part 2."
        mock_response.content = [mock_tool_block, mock_text_block1, mock_text_block2]

        with patch("coderef.agent.anthropic.Anthropic") as mock_client:
            mock_client.return_value.beta.messages.create.return_value = mock_response

            from coderef.agent import query

            result = query("test query")

        assert result == "Part 1. Part 2."

    def test_query_uses_correct_model(self):
        """Should use claude-haiku-4-5 model."""
        with patch("coderef.agent.anthropic.Anthropic") as mock_client:
            mock_create = mock_client.return_value.beta.messages.create
            mock_create.return_value.content = []

            from coderef.agent import query

            query("test query")

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["model"] == "claude-haiku-4-5"

    def test_query_includes_mcp_server(self):
        """Should include Context7 MCP server configuration."""
        with patch("coderef.agent.anthropic.Anthropic") as mock_client:
            mock_create = mock_client.return_value.beta.messages.create
            mock_create.return_value.content = []

            from coderef.agent import query

            query("test query")

            call_kwargs = mock_create.call_args.kwargs
            assert "mcp_servers" in call_kwargs
            assert (
                call_kwargs["mcp_servers"][0]["url"] == "https://mcp.context7.com/mcp"
            )
            assert call_kwargs["mcp_servers"][0]["name"] == "context7"

    def test_query_includes_tools(self):
        """Should include mcp_toolset and web_search tools."""
        with patch("coderef.agent.anthropic.Anthropic") as mock_client:
            mock_create = mock_client.return_value.beta.messages.create
            mock_create.return_value.content = []

            from coderef.agent import query

            query("test query")

            call_kwargs = mock_create.call_args.kwargs
            tool_types = [t["type"] for t in call_kwargs["tools"]]
            assert "mcp_toolset" in tool_types
            assert "web_search_20250305" in tool_types

    def test_query_includes_betas(self):
        """Should include required beta features."""
        with patch("coderef.agent.anthropic.Anthropic") as mock_client:
            mock_create = mock_client.return_value.beta.messages.create
            mock_create.return_value.content = []

            from coderef.agent import query

            query("test query")

            call_kwargs = mock_create.call_args.kwargs
            betas = call_kwargs["betas"]
            assert "mcp-client-2025-11-20" in betas
            assert "web-search-2025-03-05" in betas

    def test_query_adds_context7_api_key_when_set(self):
        """Should add Context7 API key as authorization_token when env var is set."""
        with patch("coderef.agent.anthropic.Anthropic") as mock_client:
            with patch.dict("os.environ", {"CONTEXT7_API_KEY": "test-key"}):
                mock_create = mock_client.return_value.beta.messages.create
                mock_create.return_value.content = []

                from coderef.agent import query

                query("test query")

                call_kwargs = mock_create.call_args.kwargs
                assert (
                    call_kwargs["mcp_servers"][0].get("authorization_token")
                    == "test-key"
                )

    def test_query_returns_fallback_on_empty_response(self):
        """Should return fallback message when no content blocks."""
        with patch("coderef.agent.anthropic.Anthropic") as mock_client:
            mock_create = mock_client.return_value.beta.messages.create
            mock_create.return_value.content = []

            from coderef.agent import query

            result = query("test query")

            assert result == "No response generated"

    def test_query_respects_max_tokens(self):
        """Should pass max_tokens to API call."""
        with patch("coderef.agent.anthropic.Anthropic") as mock_client:
            mock_create = mock_client.return_value.beta.messages.create
            mock_create.return_value.content = []

            from coderef.agent import query

            query("test query", max_tokens=500)

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["max_tokens"] == 500

    def test_query_uses_system_prompt(self):
        """Should include the system prompt in API call."""
        with patch("coderef.agent.anthropic.Anthropic") as mock_client:
            mock_create = mock_client.return_value.beta.messages.create
            mock_create.return_value.content = []

            from coderef.agent import query

            query("test query")

            call_kwargs = mock_create.call_args.kwargs
            assert "system" in call_kwargs
            assert "succinct" in call_kwargs["system"].lower()


class TestExtractFinalText:
    """Tests for text block filtering."""

    def test_filters_text_before_mcp_tool_result(self):
        """Should exclude text blocks before mcp_tool_result."""
        from coderef.agent import _extract_final_text

        # Simulate: [text, mcp_tool_use, mcp_tool_result, text]
        preamble = MagicMock()
        preamble.type = "text"
        preamble.text = "I'll search for that..."

        tool_use = MagicMock(spec=[])  # No text attr
        tool_use.type = "mcp_tool_use"

        tool_result = MagicMock(spec=[])  # No text attr
        tool_result.type = "mcp_tool_result"

        final_text = MagicMock()
        final_text.type = "text"
        final_text.text = "```python\nprint('hello')\n```"

        blocks = [preamble, tool_use, tool_result, final_text]
        result = _extract_final_text(blocks)

        assert result == "```python\nprint('hello')\n```"
        assert "I'll search" not in result

    def test_filters_text_between_tool_calls(self):
        """Should exclude text between multiple tool calls."""
        from coderef.agent import _extract_final_text

        # Simulate: [text, tool_use, tool_result, text, tool_use, tool_result, text]
        preamble1 = MagicMock()
        preamble1.type = "text"
        preamble1.text = "First I'll resolve the library..."

        tool_use1 = MagicMock(spec=[])
        tool_use1.type = "mcp_tool_use"

        tool_result1 = MagicMock(spec=[])
        tool_result1.type = "mcp_tool_result"

        preamble2 = MagicMock()
        preamble2.type = "text"
        preamble2.text = "Now I'll query the docs..."

        tool_use2 = MagicMock(spec=[])
        tool_use2.type = "mcp_tool_use"

        tool_result2 = MagicMock(spec=[])
        tool_result2.type = "mcp_tool_result"

        final_text = MagicMock()
        final_text.type = "text"
        final_text.text = "Here's the code example."

        blocks = [
            preamble1,
            tool_use1,
            tool_result1,
            preamble2,
            tool_use2,
            tool_result2,
            final_text,
        ]
        result = _extract_final_text(blocks)

        assert result == "Here's the code example."
        assert "resolve the library" not in result
        assert "query the docs" not in result

    def test_handles_web_search_tool_result(self):
        """Should also filter based on web_search_tool_result."""
        from coderef.agent import _extract_final_text

        preamble = MagicMock()
        preamble.type = "text"
        preamble.text = "I'll search the web..."

        tool_use = MagicMock(spec=[])
        tool_use.type = "server_tool_use"

        tool_result = MagicMock(spec=[])
        tool_result.type = "web_search_tool_result"

        final_text = MagicMock()
        final_text.type = "text"
        final_text.text = "Based on web search: here's the answer."

        blocks = [preamble, tool_use, tool_result, final_text]
        result = _extract_final_text(blocks)

        assert result == "Based on web search: here's the answer."
        assert "I'll search" not in result

    def test_returns_all_text_when_no_tools(self):
        """When no tool results, return all text blocks."""
        from coderef.agent import _extract_final_text

        text1 = MagicMock()
        text1.type = "text"
        text1.text = "Part 1. "

        text2 = MagicMock()
        text2.type = "text"
        text2.text = "Part 2."

        blocks = [text1, text2]
        result = _extract_final_text(blocks)

        assert result == "Part 1. Part 2."

    def test_returns_empty_when_no_text_after_tools(self):
        """Return empty string when tools used but no text after."""
        from coderef.agent import _extract_final_text

        preamble = MagicMock()
        preamble.type = "text"
        preamble.text = "I'll search..."

        tool_use = MagicMock(spec=[])
        tool_use.type = "mcp_tool_use"

        tool_result = MagicMock(spec=[])
        tool_result.type = "mcp_tool_result"

        blocks = [preamble, tool_use, tool_result]
        result = _extract_final_text(blocks)

        assert result == ""

    def test_concatenates_multiple_text_blocks_after_tools(self):
        """Should concatenate multiple text blocks after the last tool result."""
        from coderef.agent import _extract_final_text

        tool_result = MagicMock(spec=[])
        tool_result.type = "mcp_tool_result"

        text1 = MagicMock()
        text1.type = "text"
        text1.text = "```python\ncode\n```\n"

        text2 = MagicMock()
        text2.type = "text"
        text2.text = "This code does X."

        blocks = [tool_result, text1, text2]
        result = _extract_final_text(blocks)

        assert result == "```python\ncode\n```\nThis code does X."


class TestSystemPrompt:
    """Tests for the system prompt."""

    def test_system_prompt_mentions_context7(self):
        """System prompt should mention Context7 tools."""
        from coderef.agent import SYSTEM_PROMPT

        assert "Context7" in SYSTEM_PROMPT

    def test_system_prompt_mentions_web_search(self):
        """System prompt should mention web search fallback."""
        from coderef.agent import SYSTEM_PROMPT

        assert "web_search" in SYSTEM_PROMPT

    def test_system_prompt_emphasizes_conciseness(self):
        """System prompt should emphasize concise output."""
        from coderef.agent import SYSTEM_PROMPT

        assert "succinct" in SYSTEM_PROMPT.lower() or "concise" in SYSTEM_PROMPT.lower()

    def test_system_prompt_specifies_output_format(self):
        """System prompt should specify code first, explanation second."""
        from coderef.agent import SYSTEM_PROMPT

        assert "code" in SYSTEM_PROMPT.lower()
        assert "explanation" in SYSTEM_PROMPT.lower()
