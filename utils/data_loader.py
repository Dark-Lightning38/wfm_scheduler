"""All file I/O lives here. Nothing in /pages should open a file directly."""
from __future__ import annotations
from pathlib import Path
import io
import json
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AGENTS_DB = DATA_DIR / "agents_db.json"


@st.cache_data(show_spinner="📥 Loading demand…")
def load_demand_excel(file_bytes: bytes) -> pd.DataFrame:
    """
    Parse the AXA need.xlsx layout into the canonical 3-column frame.

    We pass bytes (not the UploadedFile object) so st.cache_data can hash
    the input. The original Scheduler_v5 layout has Date, weekday, Hour
    string, label, FTE_Brut in columns 0,1,2,3,4 respectively.
    """
    df = pd.read_excel(io.BytesIO(file_bytes))
    clean = pd.DataFrame()
    clean["Date"] = pd.to_datetime(df.iloc[:, 0])
    clean["Hour"] = pd.to_numeric(
        df.iloc[:, 2].astype(str).str.split(":").str[0], errors="coerce"
    )
    clean["FTE_Brut"] = pd.to_numeric(df.iloc[:, 4], errors="coerce").fillna(0)
    return clean.dropna(subset=["Hour"]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_agents_db() -> list[dict]:
    """Load the agents JSON. Returns [] if the file doesn't exist yet."""
    if not AGENTS_DB.exists():
        return []
    with AGENTS_DB.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_agents_db(agents: list[dict]) -> None:
    """Persist agents to JSON and clear the load cache so reads pick it up."""
    DATA_DIR.mkdir(exist_ok=True)
    with AGENTS_DB.open("w", encoding="utf-8") as f:
        json.dump(agents, f, indent=2)
    load_agents_db.clear()  # invalidate cache


def dedupe_agents(agents: list[dict]) -> dict:
    """Deduplicate by Agent ID (first occurrence wins), returns {id: record}."""
    seen, clean = set(), []
    for a in agents:
        if a["Agent ID"] not in seen:
            seen.add(a["Agent ID"])
            clean.append(a)
    return {a["Agent ID"]: a for a in clean}


def export_schedule_xlsx(df: pd.DataFrame) -> bytes:
    """Serialize the schedule DataFrame to xlsx bytes for st.download_button."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        df.to_excel(xw, index=False, sheet_name="Schedule")
    return buf.getvalue()
