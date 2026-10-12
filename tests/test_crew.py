import pytest
from researcher.crew import Researcher
from researcher.tools.search_tool import WebSearchTool


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


def test_web_search_tool():
    """Test WebSearchTool instantiation and metadata."""
    tool = WebSearchTool()
    assert tool.name == "web_search"
    assert tool.description is not None
