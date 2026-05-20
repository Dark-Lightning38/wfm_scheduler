"""Append-only audit log (data/audit.log) — viewable on the Settings page."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st

AUDIT_FILE = Path(__file__).resolve().parent.parent / "data" / "audit.log"


def write_audit_log(action: str, detail: str = "") -> None:
    """
    Append one line to the audit log. Format: ISO timestamp \\t user \\t action \\t detail.

    Streamlit Cloud's filesystem is ephemeral — for production-grade
    auditing you'd swap this for a managed sink (Postgres, S3, CloudWatch).
    """
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    user = st.session_state.get("username", "anon")
    line = f"{ts}\t{user}\t{action}\t{detail}\n"
    AUDIT_FILE.parent.mkdir(exist_ok=True)
    AUDIT_FILE.touch(exist_ok=True)
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(line)
    st.session_state.audit_log.append(line)
