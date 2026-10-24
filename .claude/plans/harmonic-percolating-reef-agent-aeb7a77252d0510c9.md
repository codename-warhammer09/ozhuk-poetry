# Implementation Plan: AI Poetry Tutor (Ozhuk AI)

## Goal
Build an AI poetry tutor that teaches users how to write poetry from scratch using an interactive chat experience, a 3-stage curriculum, and the "Three-Stone Hearth" (Ozhuk Dazhy) analysis framework.

## Architecture
The system will follow a layered architecture:
1.  **UI Layer (Streamlit):** 
    - A chat-centric interface using `st.chat_message`.
    - Sidebar for curriculum tracking and current stage visibility.
2.  **Tutoring Logic Layer (`tutor.py`):**
    - Manages the user's session state (current stage, progress).
    - Orchestrates the flow between the LLM and the PoetryDB tool.
    - Implements the curriculum progression logic.
3.  **LLM Handler Layer (`llm_handler.py`):**
    - Implements a fallback mechanism: `Ollama (local gemma4:4b)` $\rightarrow$ `Gemini API (gemma4:31b-it)`.
    - Handles structured output using Pydantic.
4.  **Tool Layer (`ozhuk_engine.py`):**
    - PoetryDB integration for fetching examples.
    - Multimodal capabilities (Image $\rightarrow$ Analysis).

## Curriculum Design
The tutor will guide users through three stages of learning:

### Stage 1: The Foundations (Basics)
- **Focus:** Rhythm, Rhyme, and Sensory Imagery.
- **Key Concepts:** Iambic meter, simple rhyme schemes (AABB, ABAB), "showing not telling."
- **Goal:** Write a short, structured stanza.

### Stage 2: The Architect's Tools (Intermediate)
- **Focus:** Poetic Forms and Literary Devices.
- **Key Concepts:** Sonnets, Haikus, Metaphors, Similes, Personification, and the "Volta" (turn).
- **Goal:** Write a poem following a specific formal constraint.

### Stage 3: The Master's Breath (Advanced)
- **Focus:** Synthesis, Originality, and Complex Scansion.
- **Key Concepts:** Free verse, Enjambment, Caesura, and thematic cohesion.
- **Goal:** Create an original piece of poetry with a critical self-analysis.

## State Management
- **Session State:** Use `st.session_state` to track:
    - `current_stage`: (1, 2, or 3).
    - `progress_score`: Numeric value reflecting user's mastery.
    - `chat_history`: List of messages for context.
    - `completed_lessons`: Set of topics mastered.
- **Progression:** The tutor analyzes user responses to Socratic challenges. If the user demonstrates mastery, the tutor suggests moving to the next stage or confirms the transition.

## LLM Handler & Fallback Logic
The `LLMHandler` class will encapsulate the logic:
1.  **Primary Attempt:** Try calling the Ollama API (`http://localhost:11434/api/generate`) with `gemma4:4b`.
2.  **Fallback Trigger:** If the local request fails (connection error, timeout, or empty response), it catches the exception.
3.  **Secondary Attempt:** Use the `google-genai` SDK to call `gemma-4-31b-it` via the Gemini API.
4.  **Consistency:** Both paths will use the same prompt templates and return Pydantic models for structured data.

## Three-Stone Hearth Integration (Ozhuk Dazhy)
Every analysis provided by the tutor will follow the triad structure:
1.  **Hearth Stone 1 (Exposure):** Focus on the surface level—imagery, setting, and mood.
2.  **Hearth Stone 2 (Development):** Focus on the mechanics—metaphors, devices, and structural choices.
3.  **Hearth Stone 3 (Resolution):** Focus on the technical—scansion, rhythm, and the "soul" or core theme.
4.  **The Spark:** A Socratic challenge that asks the user to apply one of these stones to their own writing.

## Implementation Steps

### Phase 1: Infrastructure & LLM Handler
1.  Create `src/ozhuk_poetry/llm_handler.py` to implement the Ollama $\rightarrow$ Gemini fallback.
2.  Update `src/ozhuk_poetry/ozhuk_engine.py` to use the new `LLMHandler` instead of direct `genai` calls.
3.  Define Pydantic schemas for tutoring responses (e.g., `TutorResponse` containing `feedback`, `lesson`, `socratic_prompt`).

### Phase 2: Tutoring Logic & Curriculum
1.  Create `src/ozhuk_poetry/tutor.py` to implement the `PoetryTutor` class.
2.  Define the curriculum mapping (Stage $\rightarrow$ Topics).
3.  Implement the logic for assessment and stage progression.

### Phase 3: UI Overhaul
1.  Modify `src/ozhuk_poetry/app.py` to transition from a "tool" interface to a "chat" interface.
2.  Implement the sidebar for curriculum tracking.
3.  Integrate the `PoetryTutor` and `LLMHandler` into the Streamlit loop.

### Phase 4: Refinement & Verification
1.  **Verification:** 
    - Test local Ollama flow.
    - Simulate local failure to verify Gemini API fallback.
    - Walk through the curriculum from Stage 1 to 3.
    - Verify multimodal analysis still works within the chat context.

## Critical Files for Implementation
- `src/ozhuk_poetry/llm_handler.py` (New: Fallback logic)
- `src/ozhuk_poetry/tutor.py` (New: Curriculum and state management)
- `src/ozhuk_poetry/ozhuk_engine.py` (Modified: Tooling and analysis logic)
- `src/ozhuk_poetry/app.py` (Modified: Chat UI and session handling)
EOF`
