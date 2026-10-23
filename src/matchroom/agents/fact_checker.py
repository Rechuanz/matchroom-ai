"""Fact-Checker: verifies every claim against the raw event data.

Deliberately not an LLM. Whatever generates the text, nothing is shown to a
reader unless this check passes.
"""

from __future__ import annotations

from typing import List

from ..schema import Match
from .claims import Claim

XG_TOLERANCE = 0.011


def verify(claim: Claim, match: Match) -> Claim:
    problems: List[str] = []
    events = []
    for event_id in claim.evidence:
        event = match.event(event_id)
        if event is None:
            problems.append(f"evidence event {event_id} does not exist")
        else:
            events.append(event)
    if not claim.evidence:
        problems.append("claim has no evidence")

    facts = claim.facts
    if "team" in facts and any(e.team != facts["team"] for e in events):
        problems.append(f"not all evidence belongs to {facts['team']}")
    if "event_type" in facts:
        allowed = facts["event_type"] if isinstance(facts["event_type"], (list, tuple)) else [facts["event_type"]]
        if any(e.type not in allowed for e in events):
            problems.append(f"not all evidence is of type {allowed}")
    if "count" in facts and len(claim.evidence) != facts["count"]:
        problems.append(f"claim says {facts['count']} events but cites {len(claim.evidence)}")
    if "window" in facts:
        lo, hi = facts["window"]
        if any(not (lo <= e.clock <= hi) for e in events):
            problems.append(f"evidence falls outside minutes {lo:.1f}-{hi:.1f}")
    if "xg_total" in facts:
        total = sum(e.xg or 0 for e in events)
        if abs(total - facts["xg_total"]) > XG_TOLERANCE:
            problems.append(f"xG total is {total:.2f}, claim says {facts['xg_total']}")
    if "min_x" in facts and any((e.x or 0) < facts["min_x"] for e in events):
        problems.append(f"not all evidence is at x >= {facts['min_x']}")
    if "outcome" in facts and any(e.outcome != facts["outcome"] for e in events):
        problems.append(f"not all evidence has outcome {facts['outcome']}")

    claim.problems = problems
    claim.verified = not problems
    return claim
