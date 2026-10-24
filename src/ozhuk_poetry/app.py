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

# Initialize Tutor, Critic, and Session State
if "tutor" not in st.session_state:
    st.session_state.tutor = PoetryTutor()

if "critic" not in st.session_state:
    st.session_state.critic = PoetryCritic()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Greetings, Poet. I am Ozhuk. I will guide you through the Three-Stone Hearth of poetry. We begin with The Foundations. Ready to start?"}
    ]

tutor = st.session_state.tutor
critic = st.session_state.critic

# --- Sidebar: Curriculum Map ---
with st.sidebar:
    st.title("📚 Curriculum Map")
    current_stage = tutor.get_current_stage()
    st.markdown(f"### Current Stage: **{current_stage.name}**")

    # Display all stages and milestones
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

# --- Main Chat Interface ---
st.title("Ожук (Ozhuk AI)")
st.caption("Your AI Guide to the Three-Stone Hearth of Poetic Scansion | Powered by Gemma 4")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Your response or poetry..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ozhuk is reflecting..."):
            # Determine the current tutoring goal
            milestone = tutor.get_current_milestone()

            if not milestone:
                response = "You have mastered the Three-Stone Hearth! You are now a Master of the Breath."
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                # --- DYNAMIC INTENT DETECTION ---
                # We use the LLM to decide if the user wants to:
                # 1. Learn (get an example/explanation)
                # 2. Submit (get a critique)
                # 3. Chat (general question)

                intent_prompt = (
                    f"Analyze the user's input and categorize it into one of these intents:\n"
                    f"LEARN: User wants an example, explanation, or to start learning about {milestone.name}.\n"
                    f"SUBMIT: User is providing a poem for critique or explicitly asking for a review.\n"
                    f"CHAT: User is asking a general question, greeting, or discussing poetry.\n\n"
                    f"User Input: '{prompt}'\n\n"
                    f"Respond with ONLY the word LEARN, SUBMIT, or CHAT."
                )

                intent_res = critic.llm.generate(intent_prompt)
                intent = intent_res["text"].strip().upper()

                if "LEARN" in intent:
                    poem_text = fetch_poem_excerpt("nature")
                    analysis = analyze_poem_with_ozhuk(concept=milestone.name, poem_text=poem_text)

                    response = f"### Teaching: {milestone.name}\n\n"
                    response += f"To understand {milestone.name}, let's examine this excerpt:\n\n"
                    response += f"```{poem_text}```\n\n"
                    response += f"**Exposure (Stone 1):** {analysis.hearth_stone_1_setup}\n\n"
                    response += f"**Mechanics (Stone 2):** {analysis.hearth_stone_2_development}\n\n"
                    response += f"**Scansion (Stone 3):** {analysis.hearth_stone_3_resolution}\n\n"
                    response += f"**Your Challenge:** {analysis.socratic_challenge}"

                elif "SUBMIT" in intent:
                    with st.spinner("Criticizing your work..."):
                        critique_res = critic.critique_poem(
                            poem=prompt,
                            milestone_name=milestone.name,
                            stage_name=current_stage.name
                        )

                        response = f"### 🖋️ Ozhuk's Critique\n\n{critique_res['critique']}"

                        if "Pass" in critique_res['critique']:
                            tutor.mark_milestone_complete(milestone.id)
                            response += "\n\n✨ **Milestone Complete!** You have advanced on the Ozhuk path."

                else: # CHAT
                    sys_prompt = f"You are Ozhuk, a poetry tutor. The student is currently learning {milestone.name} in {current_stage.name}. Be encouraging and Socratic."
                    res = critic.llm.generate(prompt, system_prompt=sys_prompt)
                    response = res["text"]

                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Multimodal Upload
st.markdown("---")
with st.expander("📷 Upload Manuscript for Analysis"):
    uploaded_file = st.file_uploader("Upload a poem image", type=["png", "jpg", "jpeg"])
    if uploaded_file and st.button("Ozhuk Analysis"):
        img = Image.open(uploaded_file)
        with st.spinner("Analyzing image..."):
            milestone = tutor.get_current_milestone()
            concept = milestone.name if milestone else "General Poetry"
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
