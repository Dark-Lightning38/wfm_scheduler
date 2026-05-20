"""Common sidebar block reused by Dashboard and Scheduler."""
from __future__ import annotations
import streamlit as st
from utils.data_loader import load_demand_excel


def render_data_sidebar() -> None:
    """Render the standard 'Controls' sidebar with demand upload."""
    with st.sidebar:
        st.header("Controls MENU")
        st.write("Use the controls below to interact with the data 🙂")
        st.divider()
        st.header("➕ Upload Demand")
        up = st.file_uploader("Upload need.xlsx", type=["xlsx"], key="demand_upload")
        if up is not None:
            st.session_state.demand_df = load_demand_excel(up.getvalue())
            st.success(f"Loaded {len(st.session_state.demand_df):,} demand rows")
        st.divider()
        if st.session_state.demand_df is not None:
            st.metric("Demand rows", f"{len(st.session_state.demand_df):,}")
            st.metric(
                "Distinct days",
                st.session_state.demand_df["Date"].dt.date.nunique(),
            )
