import pytest
from researcher.crew import Researcher

def test_researcher_initialization():
    """Test that the Researcher crew initializes properly."""
    crew_instance = Researcher()
    assert crew_instance is not None
    assert hasattr(crew_instance, 'crew')

def test_crew_structure():
    """Test that crew components are loaded."""
    crew_instance = Researcher()
    crew = crew_instance.crew()
    assert crew is not None
    assert len(crew.agents) == 2
    assert len(crew.tasks) == 2
