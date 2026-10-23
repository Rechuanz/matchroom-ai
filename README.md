# MatchRoom AI

Multi-agent AI newsroom that turns synthetic football match events into explainable tactical insight, live narratives and multilingual recaps. Built for *Inside the Game: Developer Hackathon*.

> All data in this repository is synthetic. Clubs and players are fictional.

## The idea

Raw match data arrives faster than anyone can turn it into stories, and an AI narrative that invents facts is worse than none. MatchRoom AI is built around one rule: **every claim must point to the events that prove it, and a Fact-Checker verifies it before anyone reads it.**

```
synthetic events -> key moments -> Tactician -> Fact-Checker -> Storyteller -> recap
  (generator)       (detected,      (explains    (rejects        (writes for
                     deterministic)  w/ evidence) unsupported)    an audience)
```

- **Generator** (`src/matchroom/generator.py`): seeded, football-realistic matches with a baked-in tactical story (a high press in the second half, cards, substitutions). Average ~3 goals and ~20 shots per match.
- **Moments** (`src/matchroom/moments.py`): goals, red cards, shot bursts and high-press spells, detected from the data, each with the ids of its evidence events.
- **Tactician** (`src/matchroom/agents/tactician.py`): turns a moment into claims (a sentence + evidence ids + checkable facts).
- **Fact-Checker** (`src/matchroom/agents/fact_checker.py`): verifies each claim against the raw events (team, counts, time window, xG total, pitch position, outcome). Not an LLM.
- **Storyteller** (`src/matchroom/agents/storyteller.py`): writes the recap from verified claims only, for a `fan` or an `analyst` audience.

## Status

| Part | State |
|---|---|
| Synthetic match generator | working, tested |
| Moment detection | working, tested |
| Template Tactician / Storyteller (offline, no model) | working |
| Fact-Checker | working, tested |
| Microsoft Foundry agents (LLM Tactician and Storyteller) | **not built yet** (see [docs/TASKS.md](docs/TASKS.md)) |
| Web app (match replay, evidence view) | not built yet |
| Multilingual output | not built yet |
| Azure deployment | not built yet |

## Quick start

Requires Python 3.9+. No third-party dependencies yet.

```bash
git clone https://github.com/Rechuanz/matchroom-ai.git
cd matchroom-ai
export PYTHONPATH=src

python3 -m unittest discover -s tests                       # run the tests
python3 -m matchroom generate --seed 54 --out data/m.json   # generate a match
python3 -m matchroom recap data/m.json --audience analyst   # verified recap with evidence ids
python3 -m matchroom recap data/m.json --json               # full structured output
```

`data/sample_match.json` is a ready-made match (seed 54).

## Data format

One JSON file per match: `teams`, `formations` and a list of `events`. Each event has `id`, `minute`, `second`, `team` (`HOME`/`AWAY`), `type` (`pass`, `shot`, `tackle`, `interception`, `foul`, `card`, `corner`, `substitution`, `kickoff`, `halftime`, `fulltime`), and optionally `player`, `x`, `y` (0-100, in the attacking direction of the acting team), `xg`, `outcome`, `detail`. See `src/matchroom/schema.py`.

## Contributing / team

Two people are building this. The split and the remaining work are in [docs/TASKS.md](docs/TASKS.md).

## License

MIT
