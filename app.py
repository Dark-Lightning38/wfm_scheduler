"""
AXA WFM Scheduler — Streamlit entrypoint.

Runs the auth gate, then delegates to st.navigation for multipage routing.
Pages live in /pages and are dumb presenters — all logic is in /core and /utils.
"""
from __future__ import annotations
import streamlit as st

from utils.auth import build_authenticator, current_user, is_authenticated
from utils.state import init_state
from components.theme import inject_theme
from components.header import render_header


def main() -> None:
    st.set_page_config(
        page_title="AXA WFM Scheduler",
        page_icon="🗓️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_theme()
    init_state()

    authenticator = build_authenticator()
    authenticator.login(location="main", key="login-form")

    if not is_authenticated():
        status = st.session_state.get("authentication_status")
        if status is False:
            st.error("❌ Username or password incorrect.")
        elif status is None:
            st.warning("🔐 Please log in to continue.")
        st.stop()

    # ----- authenticated zone -----
    render_header(current_user(), authenticator)

    pages = [
        st.Page("pages/1_📊_Dashboard.py", title="Dashboard", icon="📊", default=True),
        st.Page("pages/2_🗓️_Scheduler.py", title="Scheduler", icon="🗓️"),
        st.Page("pages/3_👥_Agents.py",    title="Agents",    icon="👥"),
        st.Page("pages/4_⚙️_Settings.py",  title="Settings",  icon="⚙️"),
    ]
    nav = st.navigation(pages)
    nav.run()


if __name__ == "__main__":
    main()
