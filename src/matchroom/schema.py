"""Data model shared by the generator, the analysis code and the agents.

Pitch coordinates are 0-100 on both axes and always expressed in the
attacking direction of the team that performed the event: x=0 is the team's
own goal line, x=100 is the opponent's goal line.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

HOME = "HOME"
AWAY = "AWAY"

EVENT_TYPES = (
    "kickoff",
    "pass",
    "shot",
    "tackle",
    "interception",
    "foul",
    "card",
    "corner",
    "substitution",
    "halftime",
    "fulltime",
)


@dataclass
class Event:
    id: int
    minute: int
    second: int
    team: str
    type: str
    player: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    xg: Optional[float] = None
    outcome: Optional[str] = None
    detail: Dict[str, Any] = field(default_factory=dict)

    @property
    def clock(self) -> float:
        """Match time in fractional minutes."""
        return self.minute + self.second / 60.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        return cls(**data)


@dataclass
class Match:
    match_id: str
    seed: int
    teams: Dict[str, str]
    formations: Dict[str, str]
    events: List[Event]

    def event(self, event_id: int) -> Optional[Event]:
        for e in self.events:
            if e.id == event_id:
                return e
        return None

    def score(self, up_to_minute: Optional[float] = None) -> Dict[str, int]:
        score = {HOME: 0, AWAY: 0}
        for e in self.events:
            if up_to_minute is not None and e.clock > up_to_minute:
                break
            if e.type == "shot" and e.outcome == "goal":
                score[e.team] += 1
        return score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "match_id": self.match_id,
            "seed": self.seed,
            "teams": self.teams,
            "formations": self.formations,
            "events": [e.to_dict() for e in self.events],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Match":
        return cls(
            match_id=data["match_id"],
            seed=data["seed"],
            teams=data["teams"],
            formations=data["formations"],
            events=[Event.from_dict(e) for e in data["events"]],
        )
