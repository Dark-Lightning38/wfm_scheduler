"""AXA-blue light theme + CSS injection."""
from __future__ import annotations
from pathlib import Path
import streamlit as st

CSS_PATH = Path(__file__).resolve().parent.parent / "assets" / "style.css"


def inject_theme() -> None:
    """Inject custom CSS if assets/style.css exists. Safe to call repeatedly."""
    if CSS_PATH.exists():
        st.markdown(f"<style>{CSS_PATH.read_text()}</style>", unsafe_allow_html=True)
