import os
from dotenv import load_dotenv
from pydantic import BaseModel
from ozhuk_poetry.llm_handler import LLMHandler
from ozhuk_poetry.critic import PoetryCritic, CritiqueVerdict
from ozhuk_poetry.ozhuk_engine import analyze_poem_with_ozhuk

load_dotenv()

class TestSchema(BaseModel):
    summary: str
    sentiment: str

def test_llm():
    handler = LLMHandler()
    print("--- Testing LLMHandler ---")
    print(f"Primary (Heavy) Model: {handler.primary_model}")
    print(f"Light Model: {handler.light_model}")
    print(f"Configured: {handler.is_configured()}")
    
    # Test 1: Light Model Standard Generation
    print("\nTest 1: Light Model Generation (gemini-flash-lite)...")
    res_light = handler.generate("Hello! Who are you?", model_tier="light")
    print(f"Mode: {res_light['mode']} | Model: {res_light.get('model')} | Response: {res_light['text'][:80]}...")
    assert res_light["mode"] == "cloud"

    # Test 2: Heavy Model Structured Generation (gemma-4-31b-it)
    print("\nTest 2: Heavy Model Structured Generation (gemma-4-31b-it)...")
    struct_res = handler.generate_structured(
        "Analyze this text: 'I love quiet rainy afternoons.'", 
        TestSchema,
        model_tier="heavy"
    )
    print(f"Structured Result: summary='{struct_res.summary}', sentiment='{struct_res.sentiment}'")
    assert isinstance(struct_res, TestSchema)

    # Test 3: PoetryCritic Structured Critique
    print("\nTest 3: PoetryCritic Evaluation...")
    critic = PoetryCritic(llm=handler)
    poem_sample = (
        "The wind whispers low through the pine,\n"
        "A song in the dusk that is mine."
    )
    critique = critic.critique_poem(poem=poem_sample, milestone_name="Rhythm & Rhyme", stage_name="The Foundations")
    print(f"Critique Verdict: {critique.verdict}")
    print(f"Strengths: {critique.strengths[:80]}...")
    print(f"Technical Analysis: {critique.technical_analysis[:80]}...")
    assert critique.verdict in [CritiqueVerdict.PASS, CritiqueVerdict.NEEDS_WORK]

    # Test 4: OzhukAnalysis Structured Scansion
    print("\nTest 4: OzhukAnalysis Engine Scansion...")
    analysis = analyze_poem_with_ozhuk(concept="Sensory Imagery", poem_text=poem_sample)
    print(f"Analysis Title: {analysis.title} by {analysis.author}")
    print(f"Stone 1 (Setup): {analysis.hearth_stone_1_setup[:80]}...")
    print(f"Stone 2 (Dev): {analysis.hearth_stone_2_development[:80]}...")
    print(f"Stone 3 (Res): {analysis.hearth_stone_3_resolution[:80]}...")
    print(f"Socratic Challenge: {analysis.socratic_challenge[:80]}...")
    assert analysis.hearth_stone_1_setup != ""

    print("\n--- ALL TESTS PASSED SUCCESSFULLY ---")

if __name__ == "__main__":
    test_llm()
