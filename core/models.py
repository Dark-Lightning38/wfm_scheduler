"""Pure dataclasses used across the engine. No streamlit, no I/O."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Literal, List, Tuple

FteType = Literal["FT", "PT"]


@dataclass(frozen=True)
class Agent:
    """Read-only agent record. Hashable so it can sit in sets/keys."""
    agent_id: str
    name: str
    fte_type: FteType
    fte: float
    days_worked: Tuple[int, ...]      # 0=Mon ... 6=Sun
    hours_worked: Tuple[int, int]     # (earliest start, latest start)

    @property
    def shift_duration(self) -> int:
        return 8 if self.fte_type == "FT" else 4


@dataclass(frozen=True)
class Shift:
    """A single scheduled shift assigned to one agent on one day."""
    agent_id: str
    agent_name: str
    date: date
    start_hour: int
    end_hour: int


@dataclass
class ScheduleResult:
    """Output of solve_schedule(). Holds shifts + solver diagnostics."""
    shifts: List[Shift] = field(default_factory=list)
    total_slack: float = 0.0
    objective_value: float = 0.0
    status: str = "Unknown"

    def to_dataframe(self):
        """View as a pandas DataFrame (for Streamlit display / Excel export)."""
        import pandas as pd
        return pd.DataFrame([{
            "Date": s.date,
            "Agent": s.agent_name,
            "Agent ID": s.agent_id,
            "Start": f"{s.start_hour:02d}:00",
            "End": f"{s.end_hour:02d}:00",
        } for s in self.shifts])
