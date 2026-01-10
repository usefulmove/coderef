"""Succinct code example agent using Claude + Context7 MCP."""

import os

import anthropic

SYSTEM_PROMPT = """You are a succinct code example assistant.

Given a programming query:
1. Use Context7 tools (resolve-library-id, query-docs) to find accurate documentation
2. If Context7 has no relevant docs, use web_search to find official documentation
3. Synthesize a response with ONLY:
   - A minimal, working code snippet (use modern idioms)
   - A one-sentence explanation

Rules:
- Code first, explanation second
- No preamble, greetings, or filler
- Do NOT narrate what tools you are using or what you are about to do
- Output ONLY the final code example and explanation, nothing else
- If using web search instead of Context7, add "(Source: web search)" at the end
- If no documentation found anywhere, say "No documentation found for [query]"
"""


def _extract_final_text(content_blocks: list) -> str:
    """Extract text blocks that appear after the last tool result.

    Claude often outputs "thinking" text before/between tool calls.
    We only want the final synthesized response.

    Args:
        content_blocks: List of content blocks from the API response

    Returns:
        Concatenated text from blocks after the last tool result
    """
    # Find index of last tool result block
    last_tool_result_idx = -1
    for i, block in enumerate(content_blocks):
        block_type = getattr(block, "type", None)
        if block_type in ("mcp_tool_result", "web_search_tool_result"):
            last_tool_result_idx = i

    # Collect text blocks after the last tool result
    text_parts = []
    for i, block in enumerate(content_blocks):
        if i > last_tool_result_idx and hasattr(block, "text"):
            text_parts.append(block.text)

    # Fallback: if no tool results, return all text (no filtering needed)
    if last_tool_result_idx == -1 and not text_parts:
        for block in content_blocks:
            if hasattr(block, "text"):
                text_parts.append(block.text)

    return "".join(text_parts) if text_parts else ""


def query(question: str, max_tokens: int = 2000) -> str:
    """Query the agent for a code example.

    Args:
        question: The programming query (e.g., "modern C++ fold_left")
        max_tokens: Maximum tokens in the response

    Returns:
        A concise code example with explanation
    """
    client = anthropic.Anthropic()

    # Configure Context7 MCP server
    mcp_servers = [
        {
            "type": "url",
            "url": "https://mcp.context7.com/mcp",
            "name": "context7",
        }
    ]

    # Add Context7 API key if available (as authorization token)
    if api_key := os.environ.get("CONTEXT7_API_KEY"):
        mcp_servers[0]["authorization_token"] = api_key

    # Tools: Context7 MCP + Web Search fallback
    tools = [
        {"type": "mcp_toolset", "mcp_server_name": "context7"},
        {"type": "web_search_20250305", "name": "web_search", "max_uses": 3},
    ]

    response = client.beta.messages.create(
        model="claude-haiku-4-5",
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
        mcp_servers=mcp_servers,
        tools=tools,
        betas=["mcp-client-2025-11-20", "web-search-2025-03-05"],
    )

    # Extract final text (filtering out pre-tool preamble)
    result = _extract_final_text(response.content)
    return result if result else "No response generated"
