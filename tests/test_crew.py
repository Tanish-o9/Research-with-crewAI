import os
import sys
from pathlib import Path
import pytest

src_path = str(Path(__file__).resolve().parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from researcher.crew import Researcher
from researcher.tools.search_tool import WebSearchTool

from researcher.tools.scraper_tool import PageScraperTool
from researcher.tools.pdf_export import export_markdown_to_pdf
from researcher.tools.audio_brief import extract_executive_summary_text
from researcher.tools.knowledge_utils import load_knowledge_documents


def test_researcher_initialization():
    """Test that the Researcher crew initializes properly."""
    crew_instance = Researcher()
    assert crew_instance is not None
    assert hasattr(crew_instance, 'crew')


def test_crew_structure():
    """Test that crew components (3 agents, 3 tasks) are correctly loaded."""
    crew_instance = Researcher()
    crew = crew_instance.crew()
    assert crew is not None
    assert len(crew.agents) == 3
    assert len(crew.tasks) == 3
    # Check that researcher has both search and scraper tools
    researcher_agent = next(a for a in crew.agents if "researcher" in a.role.lower())
    tool_names = [t.name for t in researcher_agent.tools]
    assert "web_search" in tool_names
    assert "read_webpage_content" in tool_names


def test_web_search_tool():
    """Test WebSearchTool instantiation and metadata."""
    tool = WebSearchTool()
    assert tool.name == "web_search"
    assert tool.description is not None


def test_page_scraper_tool():
    """Test PageScraperTool instantiation and validation."""
    tool = PageScraperTool()
    assert tool.name == "read_webpage_content"
    assert tool.description is not None
    # Test invalid URL safety
    res = tool._run("invalid_url_protocol")
    assert "Invalid URL" in res


def test_audio_brief_extraction():
    """Test extracting speech summary from Markdown report."""
    md = "# Executive Summary\nAI is accelerating autonomous engineering.\n\n## Key Takeaways\n1. Speed is key."
    summary = extract_executive_summary_text(md)
    assert len(summary) > 0
    assert "AI is accelerating" in summary


def test_pdf_export_flow(tmp_path):
    """Test PDF generation pipeline."""
    target_pdf = str(tmp_path / "test_report.pdf")
    md = "# Research Report: Test\n\n## Findings\n- Finding 1\n- Finding 2"
    result = export_markdown_to_pdf(md, "Test Topic", target_pdf)
    assert os.path.exists(result)
    assert os.path.getsize(result) > 0


def test_knowledge_ingestion():
    """Test knowledge document loading."""
    docs = load_knowledge_documents("knowledge")
    assert isinstance(docs, str)
