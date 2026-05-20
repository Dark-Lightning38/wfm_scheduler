"""Tests for the defensive input validators."""
import pandas as pd
from utils.validators import validate_agent_payload, validate_demand_df


def test_agent_ok():
    ok, _ = validate_agent_payload({
        "Agent ID": "A1", "name": "A", "type": "FT", "FTE": 1.0,
        "days-worked": [0, 1, 2], "Hours-worked": [8, 10],
    })
    assert ok


def test_agent_bad_type():
    ok, msg = validate_agent_payload({
        "Agent ID": "A1", "name": "A", "type": "XX", "FTE": 1.0,
        "days-worked": [0], "Hours-worked": [8, 10],
    })
    assert not ok
    assert "FT" in msg


def test_agent_bad_fte():
    ok, msg = validate_agent_payload({
        "Agent ID": "A1", "name": "A", "type": "FT", "FTE": 1.5,
        "days-worked": [0], "Hours-worked": [8, 10],
    })
    assert not ok
    assert "FTE" in msg


def test_demand_ok():
    df = pd.DataFrame({
        "Date": [pd.Timestamp("2026-01-01")],
        "Hour": [9],
        "FTE_Brut": [1],
    })
    ok, _ = validate_demand_df(df)
    assert ok


def test_demand_missing_col():
    ok, msg = validate_demand_df(pd.DataFrame({"Date": [1]}))
    assert not ok


def test_demand_empty():
    df = pd.DataFrame({"Date": [], "Hour": [], "FTE_Brut": []})
    ok, msg = validate_demand_df(df)
    assert not ok
    assert "empty" in msg.lower()
