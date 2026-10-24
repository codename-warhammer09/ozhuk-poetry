import os
from dotenv import load_dotenv
from src.ozhuk_poetry.llm_handler import LLMHandler
from pydantic import BaseModel

load_dotenv()

class TestSchema(BaseModel):
    summary: str
    sentiment: str

def test_llm():
    handler = LLMHandler()
    print(f"--- Testing LLMHandler ---")
    
    # Test 1: Standard Generation
    print("\nTest 1: Standard Generation...")
    res = handler.generate("Hello! Who are you?")
    print(f"Mode: {res['mode']} | Response: {res['text'][:100]}...")

    # Test 2: Structured Generation
    print("\nTest 2: Structured Generation...")
    try:
        struct_res = handler.generate_structured(
            "Analyze this text: 'I love poetry!'", 
            TestSchema
        )
        print(f"Structured Result: {struct_res}")
    except Exception as e:
        print(f"Structured Result Failed: {e}")

if __name__ == "__main__":
    test_llm()
