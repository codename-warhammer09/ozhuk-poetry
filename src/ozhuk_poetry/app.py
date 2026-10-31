# OZHUK POETRY TUTOR
# AI-ASSISTED DEVELOPMENT BY TEAM FUTRUS
# Powered by Gemma 4 & Gemini Flash-Lite

import os
import streamlit as st
from dotenv import load_dotenv

from ozhuk_poetry.ozhuk_engine import fetch_poem_excerpt, analyze_poem_with_ozhuk
from ozhuk_poetry.tutor import PoetryTutor
from ozhuk_poetry.critic import PoetryCritic, CritiqueVerdict

load_dotenv()

st.set_page_config(page_title="Ozhuk AI — Your Poetry Tutor", layout="wide")

# --- Environment & Key Verification ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.warning(
        "⚠️ **GEMINI_API_KEY is not detected.** Please set your Gemini API key in your `.env` file or environment variables to enable Gemma 4 literary analysis and the tutor engine."
    )

# --- Session State Initialization ---
if "mode" not in st.session_state:
    st.session_state.mode = None  # 'curriculum' or 'critic'

if "tutor" not in st.session_state:
    st.session_state.tutor = PoetryTutor()

if "critic" not in st.session_state:
    st.session_state.critic = PoetryCritic()

if "messages" not in st.session_state:
    st.session_state.messages = []

tutor: PoetryTutor = st.session_state.tutor
critic: PoetryCritic = st.session_state.critic

# --- Main Menu (Boot Sequence) ---
if st.session_state.mode is None:
    st.title("Ожук (Ozhuk AI)")
    st.markdown("### Welcome, Poet. Choose your path for this session:")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎓 Curriculum Mode")
        st.write(
            "A structured journey through the Three-Stone Hearth (Ozhuk Dazhy). Progress through milestones, study classical examples, and master the art of poetry."
        )
        if st.button("Start Learning Journey", use_container_width=True):
            st.session_state.mode = "curriculum"
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Greetings, Poet. I am Ozhuk. I will guide you through the Three-Stone Hearth of poetry. We begin with The Foundations. Ready to start?",
                }
            ]
            st.rerun()

    with col2:
        st.subheader("🖋️ Critic Mode")
        st.write(
            "A stateless, high-precision critique engine powered by Gemma 4. Submit your works for immediate, rigorous technical analysis and scansion."
        )
        if st.button("Enter the Critic's Study", use_container_width=True):
            st.session_state.mode = "critic"
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "The Critic's Study is open. Submit your poem, and I shall dissect its mechanics with the precision of the Three-Stone Hearth.",
                }
            ]
            st.rerun()
    st.stop()

# --- Common UI Header ---
st.title("Ожук (Ozhuk AI)")
if st.session_state.mode == "curriculum":
    st.caption("Your AI Guide to the Three-Stone Hearth of Poetic Scansion | Powered by Gemma 4 & Gemini Flash-Lite")
else:
    st.caption("High-Precision Poetic Analysis Engine | Stateless Mode | Powered by Gemma 4")

# --- Mode-Specific Sidebar ---
with st.sidebar:
    if st.session_state.mode == "curriculum":
        st.title("📚 Curriculum Map")
        current_stage = tutor.get_current_stage()
        st.markdown(f"### Current Stage: **{current_stage.name}**")

        for stage_id, stage in tutor.curriculum.items():
            status = "✅" if stage_id < tutor.profile.current_stage_id else ("⏳" if stage_id == tutor.profile.current_stage_id else "🔒")
            with st.expander(f"{status} Stage {stage_id}: {stage.name}"):
                for m in stage.milestones:
                    m_status = "✅" if m.id in tutor.profile.completed_milestones else "⚪"
                    st.write(f"{m_status} **{m.name}**")

        st.markdown("---")
        st.write(f"📜 **Total Poems Written:** {tutor.profile.total_poems_written}")

        # Student Portfolio Expander
        with st.expander(f"📖 Student Portfolio ({len(tutor.profile.portfolio)})"):
            if not tutor.profile.portfolio:
                st.caption("No accepted poems yet. Pass a milestone submission to record your work here!")
            else:
                for i, entry in enumerate(reversed(tutor.profile.portfolio), start=1):
                    st.markdown(f"**#{len(tutor.profile.portfolio) - i + 1} — {entry.milestone_name}**")
                    st.code(entry.poem)
                    st.caption(f"Analysis: {entry.critique[:120]}...")
                    st.markdown("---")

        if st.button("Reset Progress"):
            if os.path.exists(tutor.profile_path):
                os.remove(tutor.profile_path)
            st.session_state.tutor = PoetryTutor()
            st.rerun()
    else:
        st.title("🖋️ Critic's Study")
        st.info("Stateless Mode: No progress is tracked here. Every poem is judged on its own merits.")
        if st.button("Switch to Curriculum Mode"):
            st.session_state.mode = "curriculum"
            st.session_state.messages = []
            st.rerun()

# --- Common Chat Interface ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Your response or poetry..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ozhuk is reflecting..."):
            if st.session_state.mode == "curriculum":
                milestone = tutor.get_current_milestone()
                if not milestone:
                    response = "You have mastered the Three-Stone Hearth! You are now a Master of the Breath."
                else:
                    stage_obj = tutor.get_current_stage()

                    # Intent routing using fast light model tier
                    intent_prompt = (
                        f"Analyze the user's input and categorize it into one of these intents:\n"
                        f"LEARN: User wants an example, explanation, or to start learning about {milestone.name}.\n"
                        f"SUBMIT: User is providing a poem for critique or asking for a review.\n"
                        f"CHAT: User is asking a general question, greeting, or discussing poetry.\n\n"
                        f"User Input: '{prompt}'\n\n"
                        f"Respond with ONLY the word LEARN, SUBMIT, or CHAT."
                    )
                    intent_res = critic.llm.generate(intent_prompt, model_tier="light")
                    intent = intent_res.get("text", "").strip().upper()

                    if "LEARN" in intent:
                        poem_text = fetch_poem_excerpt("nature")
                        analysis = analyze_poem_with_ozhuk(concept=milestone.name, poem_text=poem_text)
                        response = (
                            f"### Teaching: {milestone.name}\n\n"
                            f"To understand **{milestone.name}**, let's examine this excerpt:\n\n"
                            f"```text\n{poem_text}\n```\n\n"
                            f"**Exposure (Stone 1 — Setup):**\n{analysis.hearth_stone_1_setup}\n\n"
                            f"**Mechanics (Stone 2 — Development):**\n{analysis.hearth_stone_2_development}\n\n"
                            f"**Scansion (Stone 3 — Resolution):**\n{analysis.hearth_stone_3_resolution}\n\n"
                            f"**Your Socratic Challenge:**\n{analysis.socratic_challenge}"
                        )
                    elif "SUBMIT" in intent:
                        critique_result = critic.critique_poem(
                            poem=prompt,
                            milestone_name=milestone.name,
                            stage_name=stage_obj.name,
                        )

                        verdict_badge = "✨ **VERDICT: PASS**" if critique_result.verdict == CritiqueVerdict.PASS else "⏳ **VERDICT: NEEDS WORK**"

                        response = (
                            f"### 🖋️ Ozhuk's Critique\n\n"
                            f"{verdict_badge}\n\n"
                            f"**Strengths:**\n{critique_result.strengths}\n\n"
                            f"**Technical Analysis ({milestone.name}):**\n{critique_result.technical_analysis}\n\n"
                            f"**Ozhuk's Suggestion:**\n{critique_result.suggestion}"
                        )

                        if critique_result.verdict == CritiqueVerdict.PASS:
                            tutor.mark_milestone_complete(milestone.id)
                            tutor.add_portfolio_poem(
                                milestone_id=milestone.id,
                                poem=prompt,
                                critique=critique_result.technical_analysis,
                            )
                            response += "\n\n🎉 **Milestone Complete!** Your poem has been preserved in your Portfolio, and you have advanced on the Ozhuk path."
                        else:
                            response += "\n\n*Revise your poem according to the suggestions above and submit it again to achieve this milestone.*"
                    else:
                        sys_prompt = (
                            f"You are Ozhuk, a classical poetry tutor. The student is currently studying "
                            f"'{milestone.name}' in '{stage_obj.name}'. Be encouraging, wise, and Socratic."
                        )
                        res = critic.llm.generate(prompt, system_prompt=sys_prompt, model_tier="light")
                        response = res.get("text", "")
            else:
                # --- CRITIC MODE LOGIC (Stateless) ---
                if len(prompt) < 30 and "hello" in prompt.lower():
                    sys_prompt = "You are the Ozhuk Critic, master of the Three-Stone Hearth. Be brief, dignified, and formal."
                    res = critic.llm.generate(prompt, system_prompt=sys_prompt, model_tier="light")
                    response = res.get("text", "")
                else:
                    critique_result = critic.critique_poem(
                        poem=prompt,
                        milestone_name="General Poetic Excellence",
                        stage_name="Mastery",
                    )
                    verdict_badge = "✨ **VERDICT: PASS**" if critique_result.verdict == CritiqueVerdict.PASS else "⏳ **VERDICT: NEEDS WORK**"
                    response = (
                        f"### 🖋️ High-Precision Critique\n\n"
                        f"{verdict_badge}\n\n"
                        f"**Strengths:**\n{critique_result.strengths}\n\n"
                        f"**Technical Analysis:**\n{critique_result.technical_analysis}\n\n"
                        f"**Ozhuk's Suggestion:**\n{critique_result.suggestion}"
                    )

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
