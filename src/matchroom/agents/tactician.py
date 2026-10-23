"""Tactician: explains a detected moment as a list of checkable claims.

`TemplateTactician` is the offline baseline: no model, no network. It defines
the output shape that an LLM-backed tactician (Microsoft Foundry agent) must
also produce: sentences with `evidence` ids and `facts` for the Fact-Checker.
See docs/TASKS.md.
"""

from __future__ import annotations

from ..moments import Moment
from ..schema import Match
from .claims import Claim, Explanation


def _mins(m: Moment) -> str:
    return f"{int(m.start)}'" if int(m.start) == int(m.end) else f"{int(m.start)}'-{int(m.end) + 1}'"


class TemplateTactician:
    def explain(self, moment: Moment, match: Match) -> Explanation:
        team = match.teams[moment.team]
        window = [moment.start - 0.01, moment.end + 0.01]
        f = moment.facts

        if moment.kind == "goal":
            claim = Claim(
                text=f"{f['scorer']} scores for {team} at {_mins(moment)}, making it {f['score_after']}.",
                evidence=moment.evidence,
                facts={"team": moment.team, "event_type": "shot", "outcome": "goal", "count": 1, "window": window},
            )
            headline = f"Goal for {team}"
        elif moment.kind == "red_card":
            claim = Claim(
                text=f"{f['player']} ({team}) is sent off at {_mins(moment)}, leaving the side a player short.",
                evidence=moment.evidence,
                facts={"team": moment.team, "event_type": "card", "outcome": "red", "count": 1, "window": window},
            )
            headline = f"Red card for {team}"
        elif moment.kind == "shot_burst":
            claim = Claim(
                text=f"{team} fire {f['shots']} shots between {_mins(moment)}, worth {f['xg']} expected goals.",
                evidence=moment.evidence,
                facts={"team": moment.team, "event_type": "shot", "count": f["shots"],
                       "xg_total": f["xg"], "window": window},
            )
            headline = f"{team} turn the screw"
        elif moment.kind == "high_press":
            claim = Claim(
                text=(f"{team} press high between {_mins(moment)}: {f['regains']} regains in the opposition half, "
                      f"on average {f['avg_x']:.0f}% of the way up the pitch."),
                evidence=moment.evidence,
                facts={"team": moment.team, "event_type": ["tackle", "interception"], "count": f["regains"],
                       "min_x": 60.0, "window": window},
            )
            headline = f"{team} switch to a high press"
        else:
            raise ValueError(f"unknown moment kind: {moment.kind}")

        return Explanation(moment_id=moment.id, headline=headline, claims=[claim])
