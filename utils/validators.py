"""Defensive validation. Each function returns (ok: bool, message: str)."""
from __future__ import annotations
import pandas as pd

REQUIRED_AGENT_FIELDS = {
    "Agent ID", "name", "type", "FTE", "days-worked", "Hours-worked"
}


def validate_agent_payload(payload: dict) -> tuple[bool, str]:
    """Sanity-check an agent record before persisting it."""
    missing = REQUIRED_AGENT_FIELDS - payload.keys()
    if missing:
        return False, f"Missing fields: {missing}"
    if payload["type"] not in {"FT", "PT"}:
        return False, "type must be 'FT' or 'PT'"
    if not 0 < float(payload["FTE"]) <= 1:
        return False, "FTE must be in (0, 1]"
    days = payload["days-worked"]
    if not all(0 <= int(d) <= 6 for d in days):
        return False, "days-worked must be ints 0..6"
    s_min, s_max = payload["Hours-worked"]
    if not 0 <= s_min < s_max <= 23:
        return False, "Hours-worked must satisfy 0 <= start < end <= 23"
    return True, "ok"


def validate_demand_df(df: pd.DataFrame) -> tuple[bool, str]:
    """Sanity-check the demand DataFrame before passing it to the solver."""
    needed = {"Date", "Hour", "FTE_Brut"}
    if not needed.issubset(df.columns):
        return False, f"Demand frame must contain {needed}"
    if df.empty:
        return False, "Demand frame is empty"
    if not df["Hour"].between(0, 23).all():
        return False, "Hour values out of range 0..23"
    return True, "ok"
