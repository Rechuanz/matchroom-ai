"""Model access point for the LLM-backed agents.

Not wired up yet. The offline pipeline (template Tactician + Storyteller +
Fact-Checker) runs without any model. The Foundry integration is the first
item in docs/TASKS.md: implement `FoundryClient.complete` and plug it into a
Tactician / Storyteller that returns the same `Explanation` / `Claim` objects.
"""

from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    def complete(self, system: str, prompt: str) -> str: ...


class FoundryClient:
    """Placeholder for a Microsoft Foundry (Azure AI) model deployment."""

    def __init__(self, endpoint: str, deployment: str) -> None:
        self.endpoint = endpoint
        self.deployment = deployment

    def complete(self, system: str, prompt: str) -> str:
        raise NotImplementedError("TODO: call the Foundry deployment (see docs/TASKS.md)")
