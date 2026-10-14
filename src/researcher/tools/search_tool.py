import json
import re
import warnings
from typing import Type
import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

# Suppress ddgs rename runtime warning
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*duckduckgo_search.*")

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None


class WebSearchInput(BaseModel):
    """Input parameters for the WebSearchTool."""
    query: str = Field(..., description="The search query to look up on the web.")
    max_results: int = Field(default=5, description="Maximum number of search results to retrieve.")


def clean_search_query(raw_query: str) -> str:
    """Strips conversational noise and prefixes from search queries."""
    text = raw_query.strip()
    patterns = [
        r"^(?:please\s+)?(?:can\s+you\s+)?tell\s+me\s+about\s+",
        r"^(?:please\s+)?(?:can\s+you\s+)?explain\s+(?:to\s+me\s+)?",
        r"^(?:what\s+is|what\s+are)\s+",
        r"^(?:give\s+me\s+information\s+(?:on|about))\s+",
        r"^(?:research\s+(?:about|on))\s+",
        r"^(?:find\s+(?:information|details)\s+(?:about|on))\s+",
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)
    return text.strip()


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Searches the live web for recent and accurate information. "
        "Useful for gathering current events, technical developments, facts, and source links."
    )
    args_schema: Type[BaseModel] = WebSearchInput

    def _wiki_fallback(self, query: str, max_results: int = 5) -> list[dict]:
        """Fallback search using Wikipedia API when DuckDuckGo is rate-limited or unavailable."""
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "format": "json"
            }
            headers = {"User-Agent": "ResearchIntelligenceBot/1.0"}
            resp = requests.get(url, params=params, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("query", {}).get("search", [])
                results = []
                for it in items:
                    title = it.get("title", "")
                    clean_snippet = re.sub(r"<[^>]+>", "", it.get("snippet", ""))
                    page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                    results.append({
                        "title": title,
                        "href": page_url,
                        "body": clean_snippet
                    })
                return results
        except Exception:
            pass
        return []

    def _run(self, query: str, max_results: int = 5) -> str:
        """Executes the search using DuckDuckGo with fallback to Wikipedia."""
        raw_results = []
        cleaned = clean_search_query(query)
        target_query = cleaned if cleaned else query

        # 1. Try DuckDuckGo
        if DDGS:
            try:
                with DDGS(timeout=5) as ddgs:
                    raw_results = list(ddgs.text(target_query, max_results=max_results))
            except Exception:
                raw_results = []

            # If no results and query is long, try simplified keywords
            if not raw_results:
                words = [w for w in re.sub(r"[^\w\s]", "", target_query).split() if not w.isdigit()]
                if len(words) > 3:
                    simplified = " ".join(words[:4])
                    try:
                        with DDGS(timeout=5) as ddgs:
                            raw_results = list(ddgs.text(simplified, max_results=max_results))
                    except Exception:
                        pass

        # 2. Fallback to Wikipedia Knowledge Search if DDGS is empty or timed out
        if not raw_results:
            clean_q = " ".join([w for w in re.sub(r"[^\w\s]", "", target_query).split() if not w.isdigit()][:4])
            raw_results = self._wiki_fallback(clean_q or target_query, max_results=max_results)

        if not raw_results:
            return (
                f"No specific live web results found for query '{query}'. "
                f"Proceeding with established domain principles, industry benchmarks, and synthesized analysis."
            )

        formatted = []
        for i, item in enumerate(raw_results, start=1):
            title = item.get("title", "No Title")
            href = item.get("href", item.get("link", ""))
            body = item.get("body", item.get("snippet", ""))
            formatted.append(f"{i}. **{title}**\n   URL: {href}\n   Summary: {body}")

        return "\n\n".join(formatted)
