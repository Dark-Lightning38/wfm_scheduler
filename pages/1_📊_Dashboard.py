"""Overview KPIs — mirrors week5_day3.py's tab layout."""
from __future__ import annotations
import streamlit as st

from components.sidebar import render_data_sidebar
from utils.state import init_state

init_state()
render_data_sidebar()

st.title("📊 Dashboard")
st.write("High-level KPIs of your current demand and last solve.")

tab1, tab2, tab3 = st.tabs(["Overview", "Demand Profile", "Raw Data"])

with tab1:
    c1, c2, c3 = st.columns(3)
    df = st.session_state.demand_df
    if df is not None:
        c1.metric("Total hours of demand", f"{df['FTE_Brut'].sum():,.0f}")
        c2.metric("Peak hourly demand",    f"{df['FTE_Brut'].max():.1f}")
        c3.metric("Days planned",          f"{df['Date'].dt.date.nunique()}")
    else:
        st.info("Upload a `need.xlsx` from the sidebar to begin.")

with tab2:
    if st.session_state.demand_df is not None:
        df = st.session_state.demand_df.copy()
        df["DateOnly"] = df["Date"].dt.date
        pivot = df.pivot_table(
            index="DateOnly", columns="Hour",
            values="FTE_Brut", aggfunc="sum",
        ).fillna(0)
        st.dataframe(
            pivot.style.background_gradient(axis=None, cmap="Blues"),
            use_container_width=True,
        )
    else:
        st.info("No demand loaded.")

with tab3:
    st.write("Raw Data")
    if st.session_state.demand_df is not None:
        st.dataframe(
            st.session_state.demand_df,
            use_container_width=True, hide_index=True,
        )
