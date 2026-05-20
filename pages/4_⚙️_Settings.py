"""Show audit log and session info."""
from __future__ import annotations
import streamlit as st
from pathlib import Path

from utils.auth import require_role
from utils.state import init_state

init_state()
st.title("⚙️ Settings")

st.subheader("👤 Session")
st.json({k: st.session_state.get(k) for k in ("username", "name", "roles")})

st.subheader("🧾 Audit log (last 200 lines)")
require_role("admin")
log_path = Path("data/audit.log")
if log_path.exists():
    tail = log_path.read_text().splitlines()[-200:]
    st.code("\n".join(tail) or "(empty)", language="text")
else:
    st.info("No audit entries yet.")
