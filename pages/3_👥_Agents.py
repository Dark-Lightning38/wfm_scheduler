"""CRUD UI for the agents roster. Replaces the CLI add_agent() loop."""
from __future__ import annotations
import streamlit as st

from utils.data_loader import load_agents_db, save_agents_db
from utils.validators import validate_agent_payload
from utils.audit import write_audit_log
from utils.auth import require_role
from utils.state import init_state

init_state()
require_role("admin")   # only admins mutate the roster
st.title("👥 Agents")

agents = load_agents_db()
st.caption(f"Roster size: {len(agents)} agents")

with st.expander("➕ Add a new agent", expanded=False):
    with st.form("add-agent"):
        col1, col2 = st.columns(2)
        with col1:
            agent_id = st.text_input("Agent ID")
            name = st.text_input("Name")
            type_fte = st.selectbox("Type", ["FT", "PT"])
            fte = st.number_input("FTE", 0.1, 1.0, 1.0, 0.1)
        with col2:
            days = st.multiselect(
                "Days worked", options=list(range(7)),
                format_func=lambda d: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][d],
                default=[0, 1, 2, 3, 4],
            )
            hours = st.slider("Hour window (start–latest)", 0, 23, (8, 14))

        if st.form_submit_button("Add agent", type="primary"):
            payload = {
                "Agent ID": agent_id.strip(),
                "name": name.strip(),
                "type": type_fte,
                "FTE": float(fte),
                "days-worked": days,
                "Hours-worked": list(hours),
            }
            ok, msg = validate_agent_payload(payload)
            if not ok:
                st.error(msg)
            else:
                agents.append(payload)
                save_agents_db(agents)
                write_audit_log("add_agent", agent_id)
                st.success(f"Agent {agent_id} added.")
                st.rerun()

st.subheader("Current roster")
if agents:
    st.dataframe(agents, use_container_width=True, hide_index=True)
else:
    st.info("No agents yet.")

if st.button("🗑️ Clear all agents", type="secondary"):
    save_agents_db([])
    write_audit_log("clear_agents")
    st.rerun()
