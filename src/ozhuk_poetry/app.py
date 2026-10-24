# OZHUK POETRY APP (works with Ozhuk Engine).
# AI-ASSISTED DEVELOPMENT BY TEAM FUTRUS (A.A Mirza and M. A. Qaisar)
# FOR HACKTOBERFEST HACK DAY 24/10/2026
# As part of the Challenge, for best Use, of Gemma4

import streamlit as st
from PIL import Image
from ozhuk_engine import fetch_poem_excerpt, analyze_poem_with_ozhuk
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Ozhuk AI — Poetic Scansion Agent", layout="wide")

st.title("Ожук (Ozhuk AI)")
st.caption("Multimodal Open-Source Agent Skill for Interactive Poetic Scansion & Literary Analysis | Powered by Gemma 4")

st.sidebar.header("Poetic Mechanics")
concept = st.sidebar.selectbox(
    "Select Target Concept",
    [
        "Metaphor & Imagery", 
        "Iambic Pentameter & Meter", 
        "Sonnet Voltas & Turns", 
        "Rhyme Scheme & Scansion"
    ]
)

tab1, tab2 = st.tabs(["Web Example Mode", "Multimodal Manuscript / Image Mode"])

with tab1:
    st.subheader("Live Web Retrieval + Structural Triad Analysis")
    search_query = st.text_input("Poem Title / Topic to Fetch", "road")
    
    if st.button("Fetch Example & Analyze"):
        with st.spinner("Fetching excerpt from web & running Gemma 4 Triad analysis..."):
            poem_data = fetch_poem_excerpt(search_query)
            st.code(poem_data, language="text")
            
            result = analyze_poem_with_ozhuk(concept=concept, poem_text=poem_data)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info("🔥 **Hearth Stone 1: Exposure**")
                st.write(result.hearth_stone_1_setup)
            with col2:
                st.warning("🔥 **Hearth Stone 2: Mechanics**")
                st.write(result.hearth_stone_2_development)
            with col3:
                st.success("🔥 **Hearth Stone 3: Scansion**")
                st.write(result.hearth_stone_3_resolution)
                
            st.markdown("---")
            st.subheader("Socratic Exercise")
            st.write(result.socratic_challenge)

with tab2:
    st.subheader("Multimodal Analysis (Book Page / Handwritten Poem)")
    uploaded_file = st.file_uploader("Upload an Image of a Poem", type=["png", "jpg", "jpeg"])
    
    if uploaded_file and st.button("Analyze Manuscript"):
        img = Image.open(uploaded_file)
        st.image(img, width=300)
        
        with st.spinner("Gemma 4 processing image OCR & structural analysis..."):
            result = analyze_poem_with_ozhuk(concept=concept, image=img)
            
            st.subheader(f"Analysis: {result.title} by {result.author}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info("🔥 **Hearth Stone 1: Exposure**")
                st.write(result.hearth_stone_1_setup)
            with col2:
                st.warning("🔥 **Hearth Stone 2: Mechanics**")
                st.write(result.hearth_stone_2_development)
            with col3:
                st.success("🔥 **Hearth Stone 3: Scansion**")
                st.write(result.hearth_stone_3_resolution)
                
            st.markdown("---")
            st.subheader("Socratic Exercise")
            st.write(result.socratic_challenge)