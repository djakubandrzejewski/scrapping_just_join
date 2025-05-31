# app/app.py

import streamlit as st
from app.candidate_ui import show_candidate_ui
from app.recruiter_ui import show_recruiter_ui
from app.learning_ui import show_learning_ui

def run_app():
    st.set_page_config(page_title="AI Job App", layout="centered")
    st.title("🎯 AI Job Platform")

    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page in ["home", "candidate"]:
        user_type = st.radio("👤 Kim jesteś?", ["Kandydat", "Rekruter"])

        if user_type == "Kandydat":
            show_candidate_ui()
        else:
            show_recruiter_ui()

    elif st.session_state.page == "learning":
        selected_techs = st.session_state.get("selected_techs", [])
        show_learning_ui(selected_techs)