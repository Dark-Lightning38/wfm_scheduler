"""Shared pytest fixtures used across the test modules."""
import pandas as pd
import pytest


@pytest.fixture
def tiny_demand() -> pd.DataFrame:
    """A single weekday (Monday 2026-06-01) with 2 FTE needed 08:00–17:59."""
    rows = []
    for hour in range(8, 18):
        rows.append({
            "Date": pd.Timestamp("2026-06-01"),
            "Hour": hour,
            "FTE_Brut": 2,
        })
    return pd.DataFrame(rows)


@pytest.fixture
def tiny_agents() -> dict:
    """Three agents: 2 FT and 1 PT, all available Mon-Fri."""
    return {
        "A1": {
            "Agent ID": "A1", "name": "Alice", "type": "FT", "FTE": 1.0,
            "days-worked": [0, 1, 2, 3, 4], "Hours-worked": [8, 10],
        },
        "A2": {
            "Agent ID": "A2", "name": "Bob", "type": "FT", "FTE": 1.0,
            "days-worked": [0, 1, 2, 3, 4], "Hours-worked": [9, 11],
        },
        "A3": {
            "Agent ID": "A3", "name": "Chloé", "type": "PT", "FTE": 0.5,
            "days-worked": [0, 1, 2, 3, 4], "Hours-worked": [13, 14],
        },
    }
