"""Authenticated header strip: title on the left, logout button on the right."""
from __future__ import annotations
import streamlit as st


def render_header(user: dict, authenticator) -> None:
    """Render the top header. Pass in the current_user() dict and the authenticator."""
    left, right = st.columns([6, 1])
    with left:
        st.markdown(
            f"### 🗓️ AXA WFM Scheduler  &nbsp;·&nbsp; "
            f"<span style='color:#1f3b8c'>welcome **{user['name']}**</span>",
            unsafe_allow_html=True,
        )
    with right:
        authenticator.logout("Logout", location="main", key="logout-btn")
    st.divider()
