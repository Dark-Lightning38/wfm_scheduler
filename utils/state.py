"""Centralised session-state initialisation. Call init_state() at top of each page."""
from __future__ import annotations
import streamlit as st

DEFAULTS = {
    "demand_df":   None,
    "agents":      [],
    "last_result": None,
    "audit_log":   [],
}


def init_state() -> None:
    """Idempotent — only sets keys that don't already exist."""
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v
