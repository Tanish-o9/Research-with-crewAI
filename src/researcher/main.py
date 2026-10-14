import os
import sys

# Force UTF-8 environment and encoding globally on Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import warnings
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Ensure 'src' is in sys.path when running main.py directly
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

load_dotenv()
if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from researcher.crew import Researcher
from researcher.tools.export_utils import export_report
from researcher.tools.knowledge_utils import load_knowledge_documents

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def get_research_topic() -> str:
    """Gets research topic from command line arguments or interactive input."""
    # Check CLI arguments first (e.g. python -m researcher.main "My Topic")
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        return sys.argv[1].strip()

    # If running interactively in terminal, prompt the user
    try:
        if sys.stdin and sys.stdin.isatty():
            prompt_input = input("Enter research topic (Press Enter for 'AI LLMs'): ").strip()
            if prompt_input:
                return prompt_input
    except Exception:
        pass

    return "AI LLMs"


def run():
    """
    Run the crew with dynamic topic input and multi-format export (MD, HTML, PDF, MP3).
    """
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    topic = get_research_topic()
    current_year = str(datetime.now().year)

    # Load background knowledge from knowledge/ directory if present
    doc_context = load_knowledge_documents("knowledge")
    knowledge_str = f"Internal Knowledge / Background Context:\n{doc_context}\n" if doc_context else ""

    research_depth = "Comprehensive Deep Dive"
    research_tone = "Professional & Analytical"

    print("\n" + "=" * 60)
    print(f"[*] Starting AI Research & Intelligence Crew")
    print(f"    Topic:          {topic}")
    print(f"    Current Year:   {current_year}")
    print(f"    Research Depth: {research_depth}")
    print(f"    Target Tone:    {research_tone}")
    if doc_context:
        print(f"    Knowledge Base: Ingested documents from knowledge/ directory")
    print("=" * 60 + "\n")

    inputs = {
        'topic': topic,
        'current_year': current_year,
        'research_depth': research_depth,
        'research_tone': research_tone,
        'knowledge_context': knowledge_str,
    }

    try:
        crew_instance = Researcher().crew()
        result = crew_instance.kickoff(inputs=inputs)

        # Export Markdown, HTML, PDF, and Audio reports
        report_text = getattr(result, "raw", str(result))
        exported = export_report(report_text, topic=topic)

        print("\n" + "=" * 60)
        print("[SUCCESS] Research Workflow Complete!")
        print(f"   Markdown Report : {exported.get('markdown_file')}")
        print(f"   HTML Dashboard   : {exported.get('html_file')}")
        if exported.get('pdf_file'):
            print(f"   PDF Document     : {exported.get('pdf_file')}")
        if exported.get('audio_file'):
            print(f"   Audio Briefing   : {exported.get('audio_file')}")
        print("=" * 60 + "\n")

        return result


    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "The most popular AI agent framework as of now.",
        'current_year': str(datetime.now().year)
    }
    try:
        Researcher().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Researcher().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    try:
        Researcher().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": trigger_payload.get("topic", "AI LLMs"),
        "current_year": str(datetime.now().year)
    }

    try:
        result = Researcher().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")


if __name__ == "__main__":
    run()
