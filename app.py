"""
ATS Resume Studio - Full Stack Interactive Application
Main Entry Point
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import configure_page, init_session_state
from src.ui.sidebar import render_sidebar
from src.ui.home import render_home
from src.ui.analyzer import render_analyzer
from src.ui.builder import render_builder
from src.ui.optimizer import render_optimizer
from src.ui.cover_letter import render_cover_letter
from src.ui.interview_prep import render_interview_prep
from src.ui.cool_features import render_cool_features


def main():
    configure_page()
    init_session_state()
    render_sidebar()

    page = st.session_state.current_page

    if page == "🏠 Home":
        render_home()
    elif page == "🔍 ATS Analyzer":
        render_analyzer()
    elif page == "🏗️ Resume Builder":
        render_builder()
    elif page == "✨ Resume Optimizer":
        render_optimizer()
    elif page == "✉️ Cover Letter":
        render_cover_letter()
    elif page == "🎯 Interview Prep":
        render_interview_prep()
    elif page == "🚀 Cool Features":
        render_cool_features()


if __name__ == "__main__":
    main()
