"""
Reusable constraint builders.

Each function takes the LpProblem and adds constraints in-place. Splitting
this way means:
  - One business rule = one function = one place to read/test/extend.
  - The orchestrator (scheduler.py) just composes them.
"""
from __future__ import annotations
from typing import Dict, Tuple, List
import pandas as pd
import pulp


def add_coverage_constraints(
    prob: pulp.LpProblem,
    choices: Dict[Tuple[str, pd.Timestamp, int], pulp.LpVariable],
    slack_vars: Dict[Tuple[pd.Timestamp, int], pulp.LpVariable],
    agents_dict: dict,
    clean_df: pd.DataFrame,
    all_dates: List[pd.Timestamp],
) -> None:
    """
    Coverage: sum(active agents at hour h on day d) + slack >= demand.

    FT shifts cover 8 hours with a 1-hour unpaid break at slot (start+4),
    during which the agent does NOT count toward coverage. PT shifts cover
    4 consecutive hours with no break.
    """
    for d in all_dates:
        day_data = clean_df[clean_df["Date"] == d]
        demand = dict(zip(day_data["Hour"], day_data["FTE_Brut"]))
        for h in range(24):
            coverage = []
            for (a, date_, s), var in choices.items():
                if date_ != d:
                    continue
                info = agents_dict[a]
                dur = 8 if info["type"] == "FT" else 4
                if s <= h < s + dur:
                    if info["type"] == "FT" and h == (s + 4):
                        continue          # unpaid break — no coverage
                    coverage.append(var)
            slack = pulp.LpVariable(f"Slack_{d}_{h}", lowBound=0)
            slack_vars[(d, h)] = slack
            prob += pulp.lpSum(coverage) + slack >= demand.get(h, 0)


def add_equity_constraints(
    prob: pulp.LpProblem,
    agent_daily_work: Dict[Tuple[str, pd.Timestamp], pulp.LpVariable],
    agents_dict: dict,
    all_dates: List[pd.Timestamp],
    max_shifts: int = 5,
) -> Dict[str, pulp.LpVariable]:
    """
    Soft cap: each agent works <= max_shifts + over_work (over_work is
    penalised in the objective). Returns the over_work_vars so the
    orchestrator can wire them into the objective.
    """
    over_work_vars: Dict[str, pulp.LpVariable] = {}
    for a in agents_dict:
        total = pulp.lpSum(
            agent_daily_work[(a, d)] for d in all_dates if (a, d) in agent_daily_work
        )
        ow = pulp.LpVariable(f"Over_{a}", lowBound=0)
        over_work_vars[a] = ow
        prob += total <= max_shifts + ow
    return over_work_vars


def add_no_three_day_gap(
    prob: pulp.LpProblem,
    agent_daily_work: Dict[Tuple[str, pd.Timestamp], pulp.LpVariable],
    agents_dict: dict,
    all_dates: List[pd.Timestamp],
) -> None:
    """In every rolling 3-valid-day window, the agent works at least 1 day."""
    for a, info in agents_dict.items():
        workdays = info["days-worked"]
        for i in range(len(all_dates) - 2):
            window = all_dates[i:i + 3]
            valid = [d for d in window if pd.to_datetime(d).weekday() in workdays]
            if len(valid) == 3:
                prob += pulp.lpSum(
                    agent_daily_work[(a, d)]
                    for d in valid
                    if (a, d) in agent_daily_work
                ) >= 1
