"""Claims are the contract between the Tactician and the Fact-Checker.

A claim is one sentence plus machine-checkable facts. Whoever writes the
sentence (a template today, an LLM on Microsoft Foundry later) must also
fill in `evidence` and `facts`, so the Fact-Checker can verify the sentence
against the raw event data before it reaches a reader.

Supported `facts` keys (all optional):
  team          every evidence event belongs to this team
  event_type    every evidence event has this type (or one of a list of types)
  count         number of evidence events
  window        [start_minute, end_minute] containing every evidence event
  xg_total      summed xG of the evidence events (tolerance 0.011)
  min_x         every evidence event happened at x >= this (pitch coordinates)
  outcome       every evidence event has this outcome
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Claim:
    text: str
    evidence: List[int]
    facts: Dict[str, Any] = field(default_factory=dict)
    verified: bool = False
    problems: List[str] = field(default_factory=list)


@dataclass
class Explanation:
    moment_id: str
    headline: str
    claims: List[Claim]
