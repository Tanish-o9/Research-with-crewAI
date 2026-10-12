import json
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


class WebSearchInput(BaseModel):
    """Input parameters for the WebSearchTool."""
    query: str = Field(..., description="The search query to look up on the web.")
    max_results: int = Field(default=5, description="Maximum number of search results to retrieve.")


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Searches the live web for recent and accurate information. "
        "Useful for gathering current events, technical developments, facts, and source links."
    )
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str, max_results: int = 5) -> str:
        """Executes the search using DuckDuckGo."""
        if not DDGS:
            return (
                f"[Search Notice] Web search library not available. "
                f"Proceeding with query keywords: '{query}'."
            )

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return f"No live web results found for query: '{query}'."

            formatted = []
            for i, item in enumerate(results, start=1):
                title = item.get("title", "No Title")
                href = item.get("href", item.get("link", ""))
                body = item.get("body", item.get("snippet", ""))
                formatted.append(f"{i}. **{title}**\n   URL: {href}\n   Summary: {body}")

            return "\n\n".join(formatted)

        except Exception as err:
            return (
                f"Web search encountered a temporary issue ({str(err)}). "
                f"Continue analysis using best available context for '{query}'."
            )
