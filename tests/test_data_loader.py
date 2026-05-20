"""Tests for data_loader helpers that don't need Streamlit running."""
from utils.data_loader import dedupe_agents


def test_dedupe_keeps_first():
    raw = [
        {"Agent ID": "A1", "name": "first"},
        {"Agent ID": "A1", "name": "duplicate"},
        {"Agent ID": "A2", "name": "second"},
    ]
    out = dedupe_agents(raw)
    assert set(out) == {"A1", "A2"}
    assert out["A1"]["name"] == "first"


def test_dedupe_empty():
    assert dedupe_agents([]) == {}
