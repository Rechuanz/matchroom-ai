"""Deterministic key-moment detection.

No LLM here on purpose: moments are computed from the event data so they are
reproducible and every one carries the ids of the events that prove it. The
agents downstream only explain moments; they never invent them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .schema import AWAY, HOME, Event, Match

SHOT_BURST_MIN_SHOTS = 3
SHOT_BURST_WINDOW = 6.0  # minutes
HIGH_PRESS_MIN_REGAINS = 4
HIGH_PRESS_WINDOW = 10.0  # minutes
HIGH_PRESS_X = 60.0


@dataclass
class Moment:
    id: str
    kind: str  # goal | red_card | shot_burst | high_press
    team: str
    start: float
    end: float
    evidence: List[int]
    facts: Dict[str, Any] = field(default_factory=dict)


def _windows(events: List[Event], size: float, min_count: int) -> List[List[Event]]:
    """Greedy, non-overlapping groups of at least `min_count` events inside `size` minutes."""
    groups: List[List[Event]] = []
    i = 0
    while i < len(events):
        j = i
        while j + 1 < len(events) and events[j + 1].clock - events[i].clock <= size:
            j += 1
        if j - i + 1 >= min_count:
            groups.append(events[i : j + 1])
            i = j + 1
        else:
            i += 1
    return groups


def detect_moments(match: Match) -> List[Moment]:
    moments: List[Moment] = []

    for e in match.events:
        if e.type == "shot" and e.outcome == "goal":
            score = match.score(up_to_minute=e.clock)
            moments.append(Moment(
                id="", kind="goal", team=e.team, start=e.clock, end=e.clock, evidence=[e.id],
                facts={"scorer": e.player, "xg": e.xg, "score_after": f"{score[HOME]}-{score[AWAY]}"},
            ))
        elif e.type == "card" and e.outcome == "red":
            moments.append(Moment(
                id="", kind="red_card", team=e.team, start=e.clock, end=e.clock, evidence=[e.id],
                facts={"player": e.player},
            ))

    for team in (HOME, AWAY):
        shots = [e for e in match.events if e.team == team and e.type == "shot"]
        for group in _windows(shots, SHOT_BURST_WINDOW, SHOT_BURST_MIN_SHOTS):
            moments.append(Moment(
                id="", kind="shot_burst", team=team, start=group[0].clock, end=group[-1].clock,
                evidence=[e.id for e in group],
                facts={"shots": len(group), "xg": round(sum(e.xg or 0 for e in group), 2)},
            ))
        regains = [
            e for e in match.events
            if e.team == team and e.type in ("tackle", "interception") and (e.x or 0) >= HIGH_PRESS_X
        ]
        for group in _windows(regains, HIGH_PRESS_WINDOW, HIGH_PRESS_MIN_REGAINS):
            moments.append(Moment(
                id="", kind="high_press", team=team, start=group[0].clock, end=group[-1].clock,
                evidence=[e.id for e in group],
                facts={"regains": len(group), "avg_x": round(sum(e.x or 0 for e in group) / len(group), 1)},
            ))

    moments.sort(key=lambda m: (m.start, m.kind))
    for n, m in enumerate(moments, start=1):
        m.id = f"M{n:02d}"
    return moments
