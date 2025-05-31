import streamlit as st
from app.candidate_ui import show_candidate_ui
from app.recruiter_ui import show_recruiter_ui

def run_app():
    st.set_page_config(page_title="AI Job App", layout="centered")

    # Zmieniony tytuł i styl
    st.markdown("<h1 style='text-align: center; font-size: 44px;'>🧠 AI Asystent Kariery</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>Twoje centrum do eksploracji ofert lub tworzenia rekrutacji z pomocą AI</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Sekcja wyboru roli z lepszym nagłówkiem
    st.markdown("## 👤 <strong>Kim jesteś?</strong>", unsafe_allow_html=True)
    user_type = st.radio("", ["👤 Kandydat", "💼 Rekruter"], horizontal=True)
    st.markdown("---")

    if user_type == "👤 Kandydat":
        show_candidate_ui()
    else:
        show_recruiter_ui()