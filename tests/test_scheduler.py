"""Engine tests. Note we import `core.scheduler` directly — no Streamlit."""
from core.scheduler import solve_schedule


def test_solver_returns_shifts(tiny_demand, tiny_agents):
    res = solve_schedule(
        tiny_demand, tiny_agents,
        params={"time_limit_seconds": 30},
    )
    assert res.status in {"Optimal", "Not Solved", "Feasible"}
    assert len(res.shifts) >= 1


def test_ft_shift_duration(tiny_demand, tiny_agents):
    """FT shifts should span 8 hours (modular for end-of-day wrap)."""
    res = solve_schedule(
        tiny_demand, tiny_agents,
        params={"time_limit_seconds": 30},
    )
    for s in res.shifts:
        info = tiny_agents[s.agent_id]
        if info["type"] == "FT":
            assert (s.end_hour - s.start_hour) % 24 == 8


def test_no_agent_works_more_than_soft_cap(tiny_demand, tiny_agents):
    """The equity constraint is soft — small over-shoot is allowed but not wild."""
    res = solve_schedule(
        tiny_demand, tiny_agents,
        params={"max_shifts_per_period": 5, "time_limit_seconds": 30},
    )
    counts = {}
    for s in res.shifts:
        counts[s.agent_id] = counts.get(s.agent_id, 0) + 1
    assert all(v <= 7 for v in counts.values())
