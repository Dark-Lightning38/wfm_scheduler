"""
Pure-Python scheduler engine — no Streamlit imports.

Faithful refactor of Scheduler_v5.py::solve_full_period. The single
80-line function is split along lines of responsibility:

  _build_variables    -> decision vars + "1 shift/day" link
  constraints.py      -> coverage, equity, no-3-day-gap (each in its own fn)
  _get_solver         -> isolates PuLP version drift
  solve_schedule      -> orchestrator: composes the pieces, sets objective,
                         runs solver, extracts ScheduleResult.
"""
from __future__ import annotations
from typing import Dict, Tuple
import pandas as pd
import pulp

from .models import ScheduleResult, Shift
from .constraints import (
    add_coverage_constraints,
    add_equity_constraints,
    add_no_three_day_gap,
)

DEFAULT_PARAMS = dict(
    slack_weight=100,
    shift_weight=1,
    overwork_weight=10,
    max_shifts_per_period=5,
    time_limit_seconds=240,
)


def _build_variables(prob, agents_dict, all_dates):
    """
    Build binary decision variables and the per-day work indicator.

    Returns
    -------
    choices : {(agent_id, date, start_hour) -> Binary LpVariable}
        1 iff the agent starts a shift at that hour on that day.
    agent_daily_work : {(agent_id, date) -> Binary LpVariable}
        1 iff the agent works on that day. Linked to choices via:
            sum_s choices[(a,d,s)] == agent_daily_work[(a,d)]
    """
    choices: Dict[Tuple[str, pd.Timestamp, int], pulp.LpVariable] = {}
    agent_daily_work: Dict[Tuple[str, pd.Timestamp], pulp.LpVariable] = {}
    for d in all_dates:
        weekday = pd.to_datetime(d).weekday()
        for agent_id, info in agents_dict.items():
            if weekday not in info["days-worked"]:
                continue
            s_min, s_max = info["Hours-worked"]
            agent_daily_work[(agent_id, d)] = pulp.LpVariable(
                f"Work_{agent_id}_{d}", cat="Binary"
            )
            day_choices = []
            for s in range(s_min, s_max + 1):
                v = pulp.LpVariable(f"S_{agent_id}_{d}_{s}", cat="Binary")
                choices[(agent_id, d, s)] = v
                day_choices.append(v)
            prob += pulp.lpSum(day_choices) == agent_daily_work[(agent_id, d)]
    return choices, agent_daily_work


def _get_solver(time_limit: int):
    """
    Try modern PuLP first; fall back to PULP_CBC_CMD for older installs.

    PuLP 3.x removed the bundled CBC and the legacy PULP_CBC_CMD path;
    install with `pulp[cbc]` to get the new COIN_CMD path. Wrapping both
    here means version drift is contained to ONE function.
    """
    try:
        return pulp.COIN_CMD(msg=0, timeLimit=time_limit)
    except (pulp.PulpSolverError, AttributeError):
        return pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)


def solve_schedule(
    demand_df: pd.DataFrame,
    agents_dict: dict,
    params: dict | None = None,
) -> ScheduleResult:
    """
    Solve the shift-assignment ILP.

    Parameters
    ----------
    demand_df : DataFrame with columns ['Date', 'Hour', 'FTE_Brut']
    agents_dict : {agent_id: {'name', 'type', 'FTE', 'days-worked', 'Hours-worked'}}
        Match the legacy Scheduler_v5 format so existing agents_db.json
        files load without conversion.
    params : optional tuning weights (see DEFAULT_PARAMS).

    Returns
    -------
    ScheduleResult
    """
    p = {**DEFAULT_PARAMS, **(params or {})}
    all_dates = sorted(demand_df["Date"].unique())

    prob = pulp.LpProblem("Global_Schedule", pulp.LpMinimize)
    choices, agent_daily_work = _build_variables(prob, agents_dict, all_dates)
    slack_vars: Dict[Tuple[pd.Timestamp, int], pulp.LpVariable] = {}

    # Compose the business rules. Each function adds constraints in place.
    add_coverage_constraints(prob, choices, slack_vars, agents_dict, demand_df, all_dates)
    over_work_vars = add_equity_constraints(
        prob, agent_daily_work, agents_dict, all_dates,
        max_shifts=p["max_shifts_per_period"],
    )
    add_no_three_day_gap(prob, agent_daily_work, agents_dict, all_dates)

    # The objective lives here (only the orchestrator sees ALL var families).
    prob += (
        pulp.lpSum(slack_vars.values())       * p["slack_weight"]
        + pulp.lpSum(choices.values())        * p["shift_weight"]
        + pulp.lpSum(over_work_vars.values()) * p["overwork_weight"]
    )

    prob.solve(_get_solver(p["time_limit_seconds"]))

    res = ScheduleResult(
        status=pulp.LpStatus[prob.status],
        objective_value=pulp.value(prob.objective) or 0.0,
        total_slack=sum(pulp.value(v) or 0 for v in slack_vars.values()),
    )
    for (a, d, s), var in choices.items():
        if (pulp.value(var) or 0) > 0.5:
            info = agents_dict[a]
            dur = 8 if info["type"] == "FT" else 4
            res.shifts.append(Shift(
                agent_id=a, agent_name=info["name"],
                date=pd.to_datetime(d).date(),
                start_hour=s, end_hour=(s + dur) % 24,
            ))
    return res
