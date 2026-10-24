# OZHUK POETRY TUTOR
# AI-ASSISTED DEVELOPMENT BY TEAM FUTRUS
# Powered by Gemma 4

import streamlit as st
from PIL import Image
from ozhuk_poetry.ozhuk_engine import fetch_poem_excerpt, analyze_poem_with_ozhuk
from ozhuk_poetry.tutor import PoetryTutor
from ozhuk_poetry.critic import PoetryCritic
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Ozhuk AI — Your Poetry Tutor", layout="wide")

# --- Session State Initialization ---
if "mode" not in st.session_state:
    st.session_state.mode = None # 'curriculum' or 'critic'

if "tutor" not in st.session_state:
    st.session_state.tutor = PoetryTutor()

if "critic" not in st.session_state:
    st.session_state.critic = PoetryCritic()

if "messages" not in st.session_state:
    st.session_state.messages = []

tutor = st.session_state.tutor
critic = st.session_state.critic

# --- Main Menu (Boot Sequence) ---
if st.session_state.mode is None:
    st.title("Ожук (Ozhuk AI)")
    st.markdown("### Welcome, Poet. Choose your path for this session:")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎓 Curriculum Mode")
        st.write("A structured journey through the Three-Stone Hearth. Progress through milestones and master the art of poetry.")
        if st.button("Start Learning Journey"):
            st.session_state.mode = 'curriculum'
            st.session_state.messages = [
                {"role": "assistant", "content": "Greetings, Poet. I am Ozhuk. I will guide you through the Three-Stone Hearth of poetry. We begin with The Foundations. Ready to start?"}
            ]
            st.rerun()

    with col2:
        st.subheader("🖋️ Critic Mode")
        st.write("A stateless, high-precision critique engine. Submit your works for immediate, rigorous technical analysis.")
        if st.button("Enter the Critic's Study"):
            st.session_state.mode = 'critic'
            st.session_state.messages = [
                {"role": "assistant", "content": "The Critic's Study is open. Submit your poem, and I shall dissect its mechanics with the precision of the Three-Stone Hearth."}
            ]
            st.rerun()
    st.stop()

# --- Common UI Header ---
st.title("Ожук (Ozhuk AI)")
if st.session_state.mode == 'curriculum':
    st.caption("Your AI Guide to the Three-Stone Hearth of Poetic Scansion | Powered by Gemma 4")
else:
    st.caption("High-Precision Poetic Analysis Engine | Stateless Mode | Powered by Gemma 4")

# --- Mode-Specific Sidebar ---
with st.sidebar:
    if st.session_state.mode == 'curriculum':
        st.title("📚 Curriculum Map")
        current_stage = tutor.get_current_stage()
        st.markdown(f"### Current Stage: **{current_stage.name}**")

        for stage_id, stage in tutor.curriculum.items():
            status = "✅" if stage_id < tutor.profile.current_stage_id else ("⏳" if stage_id == tutor.profile.current_stage_id else "🔒")
            with st.expander(f"{status} Stage {stage_id}: {stage.name}"):
                for m in stage.milestones:
                    m_status = "✅" if m.id in tutor.profile.completed_milestones else "⚪"
                    st.write(f"{m_status} {m.name}")

        st.markdown("---")
        st.write(f"**Total Poems Written:** {tutor.profile.total_poems_written}")
        if st.button("Reset Progress"):
            if os.path.exists(tutor.profile_path):
                os.remove(tutor.profile_path)
            st.session_state.tutor = PoetryTutor()
            st.rerun()
    else:
        st.title("🖋️ Critic's Study")
        st.info("Stateless Mode: No progress is tracked here. Every poem is judged on its own merits.")
        if st.button("Switch to Curriculum Mode"):
            st.session_state.mode = 'curriculum'
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

            if st.session_state.mode == 'curriculum':
                # --- CURRICULUM LOGIC ---
                milestone = tutor.get_current_milestone()
                if not milestone:
                    response = "You have mastered the Three-Stone Hearth! You are now a Master of the Breath."
                else:
                    # Capture stage name for the critic
                    stage_obj = tutor.get_current_stage()

                    intent_prompt = (
                        f"Analyze the user's input and categorize it into one of these intents:\n"
                        f"LEARN: User wants an example, explanation, or to start learning about {milestone.name}.\n"
                        f"SUBMIT: User is providing a poem for critique or explicitly asking for a review.\n"
                        f"CHAT: User is asking a general question, greeting, or discussing poetry.\n\n"
                        f"User Input: '{prompt}'\n\n"
                        f"Respond with ONLY the word LEARN, SUBMIT, or CHAT."
                    )
                    intent_res = critic.llm.generate(intent_prompt, model_tier="light")
                    intent = intent_res["text"].strip().upper()

                    if "LEARN" in intent:
                        poem_text = fetch_poem_excerpt("nature")
                        analysis = analyze_poem_with_ozhuk(concept=milestone.name, poem_text=poem_text)
                        response = f"### Teaching: {milestone.name}\n\nTo understand {milestone.name}, let's examine this excerpt:\n\n```{poem_text}```\n\n"
                        response += f"**Exposure (Stone 1):** {analysis.hearth_stone_1_setup}\n\n"
                        response += f"**Mechanics (Stone 2):** {analysis.hearth_stone_2_development}\n\n"
                        response += f"**Scansion (Stone 3):** {analysis.hearth_stone_3_resolution}\n\n"
                        response += f"**Your Challenge:** {analysis.socratic_challenge}"
                    elif "SUBMIT" in intent:
                        critique_res = critic.critique_poem(poem=prompt, milestone_name=milestone.name, stage_name=stage_obj.name)
                        response = f"### 🖋️ Ozhuk's Critique\n\n{critique_res['critique']}"
                        if "Pass" in critique_res['critique']:
                            tutor.mark_milestone_complete(milestone.id)
                            response += "\n\n✨ **Milestone Complete!** You have advanced on the Ozhuk path."
                    else:
                        sys_prompt = f"You are Ozhuk, a poetry tutor. The student is currently learning {milestone.name} in {stage_obj.name}. Be encouraging and Socratic."
                        res = critic.llm.generate(prompt, system_prompt=sys_prompt, model_tier="light")
                        response = res["text"]
            else:
                # --- CRITIC MODE LOGIC (Stateless) ---
                if len(prompt) < 30 and "hello" in prompt.lower():
                    sys_prompt = "You are the Ozhuk Critic. Be brief and formal."
                    res = critic.llm.generate(prompt, system_prompt=sys_prompt, model_tier="light")
                    response = res["text"]
                else:
                    with st.spinner("Performing high-precision analysis..."):
                        critique_res = critic.critique_poem(
                            poem=prompt,
                            milestone_name="General Poetic Excellence",
                            stage_name="Mastery"
                        )
                        response = f"### 🖋️ High-Precision Critique\n\n{critique_res['critique']}"

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Multimodal Upload
st.markdown("---")
with st.expander("📷 Upload Manuscript for Analysis"):
    uploaded_file = st.file_uploader("Upload a poem image", type=["png", "jpg", "jpeg"])
    if uploaded_file and st.button("Ozhuk Analysis"):
        img = Image.open(uploaded_file)
        with st.spinner("Analyzing image..."):
            if st.session_state.mode == 'curriculum':
                milestone = tutor.get_current_milestone()
                concept = milestone.name if milestone else "General Poetry"
            else:
                concept = "General Poetic Excellence"

            result = analyze_poem_with_ozhuk(concept=concept, image=img)
            st.image(img, width=300)
            st.subheader(f"Analysis: {result.title} by {result.author}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info("🔥 **Exposure**")
                st.write(result.hearth_stone_1_setup)
            with col2:
                st.warning("🔥 **Mechanics**")
                st.write(result.hearth_stone_2_development)
            with col3:
                st.success("🔥 **Scansion**")
                st.write(result.hearth_stone_3_resolution)
            st.markdown(f"**Socratic Challenge:** {result.socratic_challenge}")
