import re
import html
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("page-rag")


async def _fetch_page_html(url: str) -> str:
    headers = {
        "User-Agent": "weather-chat-rag/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    transport = httpx.AsyncHTTPTransport(verify=False)
    async with httpx.AsyncClient(transport=transport, timeout=30.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


def _clean_html(html_text: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html_text)
    text = re.sub(r"(?is)<!--.*?-->", " ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@mcp.tool()
async def extract_page_content(url: str, max_chars: int = 2000) -> str:
    """Fetch a web page and return cleaned text content for the model."""
    try:
        html_text = await _fetch_page_html(url)
    except Exception as exc:
        return f"Failed to fetch page: {exc}"

    cleaned = _clean_html(html_text)
    if not cleaned:
        return "The page contained no readable text content."

    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars].rstrip()
        cleaned += "\n\n[Content truncated to max_chars]"

    return cleaned


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
