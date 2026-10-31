import sys
from pathlib import Path

from .llm_handler import LLMHandler
from .tutor import PoetryTutor
from .critic import PoetryCritic, CritiqueVerdict, CritiqueResult
from .ozhuk_engine import analyze_poem_with_ozhuk, fetch_poem_excerpt, OzhukAnalysis

def main() -> None:
    """CLI entrypoint that launches the Ozhuk Poetry Streamlit web application."""
    try:
        import streamlit.web.cli as stcli
    except ImportError:
        print("Error: Streamlit is required to launch Ozhuk Poetry UI. Please run 'uv sync'.")
        sys.exit(1)

    app_path = Path(__file__).parent / "app.py"
    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(stcli.main())
