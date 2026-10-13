import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from bs4 import BeautifulSoup


class PageScraperInput(BaseModel):
    """Input parameters for PageScraperTool."""
    url: str = Field(..., description="The HTTP or HTTPS URL of the webpage to scrape and read.")
    max_words: int = Field(default=2000, description="Maximum number of words to extract from the page.")


class PageScraperTool(BaseTool):
    name: str = "read_webpage_content"
    description: str = (
        "Visits a specific webpage URL and extracts its main article text, headers, and key details. "
        "Use this after finding promising URLs from search to perform deep-dive reading on facts and technical data."
    )
    args_schema: Type[BaseModel] = PageScraperInput

    def _run(self, url: str, max_words: int = 2000) -> str:
        """Fetches and cleans text from the specified URL."""
        if not url or not url.startswith(("http://", "https://")):
            return f"Invalid URL provided: '{url}'. Please provide a valid http or https URL."

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            response = requests.get(url, headers=headers, timeout=12)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove non-content elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form"]):
                tag.decompose()

            # Attempt to target main content tags if present
            main_container = (
                soup.find("article")
                or soup.find("main")
                or soup.find(class_=lambda c: c and any(k in str(c).lower() for k in ["article", "content", "post-body", "entry-content"]))
                or soup.body
            )

            if not main_container:
                return f"Could not extract readable content from {url}."

            # Get text and clean excess whitespace
            lines = [line.strip() for line in main_container.get_text(separator="\n").splitlines()]
            clean_text = "\n".join(chunk for chunk in lines if chunk)

            # Limit words
            words = clean_text.split()
            if len(words) > max_words:
                clean_text = " ".join(words[:max_words]) + f"\n\n[...Content truncated to {max_words} words for brevity...]"

            if len(clean_text) < 100:
                return f"Page at {url} returned minimal or protected content (e.g., paywall/captcha)."

            return f"=== Scraped Content from: {url} ===\n\n{clean_text}"

        except requests.exceptions.Timeout:
            return f"Request timed out while trying to reach {url}."
        except requests.exceptions.RequestException as e:
            return f"Unable to fetch content from {url} (Error: {str(e)})."
        except Exception as e:
            return f"Error parsing page {url}: {str(e)}"
