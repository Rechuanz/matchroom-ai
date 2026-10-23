# Tasks and split (deadline: Oct 27, 11:59 PM Pacific = Oct 28, 03:59 Brasilia)

Two people. **Person A** owns the data and the agents. **Person B** owns the app and the cloud. Both write the README, the project description and the demo video.

## Rules of the hackathon that shape the work

- Public GitHub repo, working demo link available free until the end of judging, demo video under 2 minutes (YouTube/Vimeo/etc.), everything in English.
- Must use Microsoft/Azure technologies (Foundry, Agent Framework, Azure MCP, GitHub Copilot, Azure services). A project with no real Azure usage can fail stage one.
- Data must be synthetic. Judges score: technological implementation, agentic design and innovation, real-world impact, UX and presentation, fit to category (20% each).
- Do not promise in the project description anything that is not in the video.

## Person A: data and agents

- [ ] Create a Microsoft Foundry project and deploy a model; fill in `FoundryClient.complete` in `src/matchroom/llm.py`
- [ ] LLM `Tactician`: same output as `TemplateTactician` (claims with `evidence` and `facts`, JSON), and the Fact-Checker must still pass it. Reject and retry on failure
- [ ] LLM `Storyteller`: audience (`fan`, `analyst`, `presenter`) and language (start with `en`, `pt`, `es`), using only verified claims
- [ ] Orchestrate the agents with Microsoft Agent Framework (Event Analyst -> Tactician -> Fact-Checker -> Storyteller), with the retry loop
- [ ] Optional: more tactical patterns in `moments.py` (momentum swing, formation change), more match variety in the generator
- [ ] Add tests for every new claim type

## Person B: app and cloud

- [ ] API (FastAPI or Azure Functions) exposing: list matches, get match, get recap (audience, language), stream events for replay
- [ ] Web UI: match replay with a timeline, live-style narrative, click any claim to see its evidence events, audience and language switch
- [ ] Deploy to Azure (Container Apps or Static Web Apps + Functions); keep the URL free and public through judging
- [ ] Secrets in environment variables or Key Vault, never in the repo

## Both, last two days

- [ ] README with architecture diagram, setup steps and the list of Microsoft technologies actually used
- [ ] Demo video under 2 minutes, public, showing the app running
- [ ] Fill the Innovation Studio project page (title, tagline, description, repo link, video link) and submit before the deadline
- [ ] Choose one **Representative** who submits for the team

## Suggested order if time runs short

1. One match end to end through the Foundry agents.
2. Evidence view in the UI (the explainability story).
3. Azure deployment and demo video.
4. Languages and extra audiences.
