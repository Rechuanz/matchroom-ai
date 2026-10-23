"""Storyteller: turns verified explanations into a recap for a given audience.

Only claims that passed the Fact-Checker are used. Offline baseline; the
Foundry-backed version should keep the same signature (see docs/TASKS.md).
"""

from __future__ import annotations

from typing import List

from ..schema import HOME, AWAY, Match
from .claims import Explanation

AUDIENCES = ("fan", "analyst")


def write_recap(match: Match, explanations: List[Explanation], audience: str = "fan") -> str:
    if audience not in AUDIENCES:
        raise ValueError(f"audience must be one of {AUDIENCES}")
    score = match.score()
    home, away = match.teams[HOME], match.teams[AWAY]
    lines = [f"{home} {score[HOME]}-{score[AWAY]} {away}", ""]
    for ex in explanations:
        verified = [c for c in ex.claims if c.verified]
        if not verified:
            continue
        lines.append(f"{ex.headline}")
        for claim in verified:
            lines.append(f"  {claim.text}")
            if audience == "analyst":
                lines.append(f"  [evidence: events {', '.join(str(i) for i in claim.evidence)}]")
    return "\n".join(lines)
