"""Solve the schedule. Wraps core/scheduler.py in a cached function."""
from __future__ import annotations
import streamlit as st
import pandas as pd

from components.sidebar import render_data_sidebar
from core.scheduler import solve_schedule
from utils.data_loader import (
    load_agents_db, dedupe_agents, export_schedule_xlsx,
)
from utils.audit import write_audit_log
from utils.state import init_state
from utils.validators import validate_demand_df

init_state()
render_data_sidebar()

st.title("🗓️ Scheduler")
st.write("Run the PuLP/CBC optimiser on the loaded demand and agents.")


@st.cache_data(show_spinner="Solving with CBC (≤240 s)…", ttl=3600)
def scheduler_solve_cached(demand_df: pd.DataFrame, agents: dict, params: dict):
    """Cached wrapper — page-prefixed name to avoid Streamlit issue #14639."""
    return solve_schedule(demand_df, agents, params)


with st.sidebar:
    st.divider()
    st.header("⚙️ Solver Params")
    slack_w = st.number_input("Slack weight",      value=100, min_value=1)
    over_w  = st.number_input("Overwork weight",   value=10,  min_value=1)
    max_sh  = st.number_input("Max shifts/period", value=5,   min_value=1)
    tlimit  = st.slider("Time limit (s)", min_value=15, max_value=600, value=240)


col_a, col_b = st.columns([3, 1])
with col_a:
    st.subheader("Inputs")
    df = st.session_state.demand_df
    agents_dict = dedupe_agents(load_agents_db())
    if df is None or not agents_dict:
        st.warning("Need both demand and ≥1 agent. Use the sidebar / Agents page.")
        st.stop()
    ok, msg = validate_demand_df(df)
    if not ok:
        st.error(f"Demand frame invalid: {msg}")
        st.stop()
    st.write(f"**Agents loaded:** {len(agents_dict)} · **Demand rows:** {len(df):,}")
with col_b:
    run = st.button("▶️ Run solver", type="primary", use_container_width=True)

if run:
    params = dict(
        slack_weight=slack_w, overwork_weight=over_w,
        max_shifts_per_period=max_sh, time_limit_seconds=tlimit,
    )
    result = scheduler_solve_cached(df, agents_dict, params)
    st.session_state.last_result = result
    write_audit_log(
        "solve",
        f"status={result.status} obj={result.objective_value:.0f} "
        f"slack={result.total_slack:.1f}",
    )

result = st.session_state.last_result
if result is not None:
    tab1, tab2, tab3 = st.tabs(["Overview", "Schedule", "Raw"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Solver status", result.status)
        c2.metric("Total slack (uncovered FTE·h)", f"{result.total_slack:,.1f}")
        c3.metric("Objective value", f"{result.objective_value:,.0f}")

    with tab2:
        sched_df = result.to_dataframe()
        st.dataframe(sched_df, use_container_width=True, hide_index=True)
        st.download_button(
            "💾 Download as Excel",
            data=export_schedule_xlsx(sched_df),
            file_name="final_schedule_global.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with tab3:
        st.json([s.__dict__ for s in result.shifts][:50])
