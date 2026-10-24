# OZHUK POETRY TUTOR
# AI-ASSISTED DEVELOPMENT BY TEAM FUTRUS
# Powered by Gemma 4

import streamlit as st
from PIL import Image
from ozhuk_engine import fetch_poem_excerpt, analyze_poem_with_ozhuk
from ozhuk_poetry.tutor import PoetryTutor
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Ozhuk AI — Your Poetry Tutor", layout="wide")

# Initialize Tutor and Session State
if "tutor" not in st.session_state:
    st.session_state.tutor = PoetryTutor()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Greetings, Poet. I am Ozhuk. I will guide you through the Three-Stone Hearth of poetry. We begin with The Foundations. Ready to start?"}
    ]

tutor = st.session_state.tutor

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

            if milestone:
                # Socratic Loop
                if "example" in prompt.lower() or "start" in prompt.lower():
                    poem_text = fetch_poem_excerpt("nature")
                    analysis = analyze_poem_with_ozhuk(concept=milestone.name, poem_text=poem_text)

                    response = f"Let's look at an example for **{milestone.name}**:\n\n"
                    response += f"```{poem_text}```\n\n"
                    response += f"**Exposure:** {analysis.hearth_stone_1_setup}\n\n"
                    response += f"**Mechanics:** {analysis.hearth_stone_2_development}\n\n"
                    response += f"**Scansion:** {analysis.hearth_stone_3_resolution}\n\n"
                    response += f"**Challenge:** {analysis.socratic_challenge}"
                else:
                    response = f"I've noted your response regarding {milestone.name}. To advance, try to apply this to a short poem of your own."

                    if "correct" in prompt.lower() or "poem" in prompt.lower():
                        tutor.mark_milestone_complete(milestone.id)
                        response += "\n\n✨ **Milestone Complete!** You've progressed further on the Ozhuk path."
            else:
                response = "You have mastered the Three-Stone Hearth! You are now a Master of the Breath."

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
