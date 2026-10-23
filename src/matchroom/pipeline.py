"""End-to-end offline pipeline: events -> moments -> explanations -> verified recap."""

from __future__ import annotations

from typing import Any, Dict

from .agents import fact_checker
from .agents.storyteller import write_recap
from .agents.tactician import TemplateTactician
from .moments import detect_moments
from .schema import HOME, AWAY, Match


def build_recap(match: Match, audience: str = "fan") -> Dict[str, Any]:
    tactician = TemplateTactician()
    explanations = []
    rejected = 0
    for moment in detect_moments(match):
        explanation = tactician.explain(moment, match)
        for claim in explanation.claims:
            fact_checker.verify(claim, match)
            rejected += 0 if claim.verified else 1
        explanations.append(explanation)

    score = match.score()
    return {
        "match_id": match.match_id,
        "score": {match.teams[HOME]: score[HOME], match.teams[AWAY]: score[AWAY]},
        "moments": [
            {
                "id": ex.moment_id,
                "headline": ex.headline,
                "claims": [
                    {"text": c.text, "evidence": c.evidence, "verified": c.verified, "problems": c.problems}
                    for c in ex.claims
                ],
            }
            for ex in explanations
        ],
        "rejected_claims": rejected,
        "text": write_recap(match, explanations, audience),
    }
