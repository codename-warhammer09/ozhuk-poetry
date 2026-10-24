from .llm_handler import LLMHandler
from .tutor import PoetryTutor
from .critic import PoetryCritic
from .ozhuk_engine import analyze_poem_with_ozhuk, fetch_poem_excerpt

def main() -> None:
    print("Ozhuk Poetry Tutor initialized.")
