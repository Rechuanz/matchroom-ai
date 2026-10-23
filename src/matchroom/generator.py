"""Synthetic, football-realistic match generator.

Everything here is invented: fictional clubs, fictional players, simulated
events. The simulation is seeded, so the same seed always yields the same
match. One tactical story is baked in so the analysis has something to find:
at some point in the second half the home side switches to a high press.
"""

from __future__ import annotations

import random
from typing import Dict, List

from .schema import AWAY, HOME, Event, Match

TEAM_NAMES = {HOME: "Northgate FC", AWAY: "Riverside United"}
FORMATIONS = {HOME: "4-3-3", AWAY: "4-4-2"}
POSITIONS = ["GK", "LB", "CB", "CB", "RB", "CM", "CM", "CM", "LW", "ST", "RW"]
INITIALS = "ABCDEFGHJKLMNPRSTVW"
SURNAMES = [
    "Alvarez", "Brandt", "Castell", "Dufresne", "Eriksen", "Farrow",
    "Grealish", "Halvorsen", "Ibarra", "Jansen", "Kowalski", "Lindqvist",
    "Moreau", "Novak", "Okafor", "Petrov", "Quintero", "Rossi", "Santoro",
    "Tanaka", "Underhill", "Vasquez", "Whitlock", "Yilmaz", "Zielinski",
    "Abara", "Bellamy", "Costa", "Dimitrov", "Esposito", "Fontaine",
    "Gallagher", "Hartmann", "Iverson", "Jovanovic", "Keane", "Lombardi",
    "Mbeki", "Nakamura", "Oyelaran", "Pellegrini", "Rasmussen",
]


def _squad(rng: random.Random) -> List[Dict[str, str]]:
    names = rng.sample(SURNAMES, len(POSITIONS) + 3)
    return [
        {"name": f"{rng.choice(INITIALS)}. {n}", "pos": POSITIONS[i] if i < 11 else "SUB"}
        for i, n in enumerate(names)
    ]


def generate_match(seed: int = 7) -> Match:
    rng = random.Random(seed)
    squads = {HOME: _squad(rng), AWAY: _squad(rng)}
    strength = {HOME: rng.uniform(0.95, 1.1), AWAY: rng.uniform(0.9, 1.05)}
    momentum = {HOME: 0.0, AWAY: 0.0}
    press_from = rng.randint(50, 62)  # minute when the home side starts pressing high
    sub_minutes = {HOME: sorted(rng.sample(range(58, 80), 2)), AWAY: sorted(rng.sample(range(58, 80), 2))}
    yellows: Dict[str, int] = {}
    events: List[Event] = []
    state = {"t": 0.0, "bench": {HOME: 11, AWAY: 11}}

    def other(team: str) -> str:
        return AWAY if team == HOME else HOME

    def add(team: str, etype: str, **kw) -> Event:
        t = state["t"]
        ev = Event(id=len(events) + 1, minute=int(t // 60), second=int(t % 60), team=team, type=etype, **kw)
        events.append(ev)
        return ev

    sent_off: set = set()

    def on_pitch(team: str) -> str:
        pool = [p["name"] for p in squads[team][:11] if p["pos"] != "GK" and p["name"] not in sent_off]
        return rng.choice(pool)

    def pressing(team: str, minute: int) -> bool:
        return team == HOME and minute >= press_from

    def simulate_possession(team: str) -> str:
        """Plays out one possession and returns the team that gets the ball next."""
        opp = other(team)
        minute = int(state["t"] // 60)
        atk = strength[team] * (1 + momentum[team])
        n_passes = rng.randint(1, 4) if pressing(opp, minute) else rng.randint(2, 7)
        x = rng.uniform(15, 40)
        for _ in range(n_passes):
            x = min(95.0, x + rng.uniform(2, 14))
            add(team, "pass", player=on_pitch(team), x=round(x, 1), y=round(rng.uniform(10, 90), 1),
                outcome="complete")
            state["t"] += rng.uniform(3, 7)
        for k in momentum:
            momentum[k] *= 0.97

        r = rng.random()
        shot_p = 0.085 * atk * (0.5 + x / 100)
        if r < shot_p:
            sx = rng.uniform(78, 96)
            sy = rng.gauss(50, 14)
            xg = round(max(0.02, min(0.6, 0.02 + (sx - 72) / 100 * 0.9 * (1 - abs(sy - 50) / 90))), 2)
            outcome = "goal" if rng.random() < xg else rng.choice(["saved", "blocked", "off_target"])
            add(team, "shot", player=on_pitch(team), x=round(sx, 1), y=round(sy, 1), xg=xg, outcome=outcome)
            state["t"] += rng.uniform(2, 5)
            if outcome == "goal":
                momentum[team] = min(0.5, momentum[team] + 0.15)
                momentum[opp] = max(-0.3, momentum[opp] - 0.1)
                return opp
            if outcome == "saved" and rng.random() < 0.3:
                add(team, "corner", x=100.0, y=rng.choice([0.0, 100.0]))
                state["t"] += rng.uniform(15, 25)
            return opp
        if r < shot_p + 0.07:
            who = on_pitch(opp)
            add(opp, "foul", player=who, x=round(100 - x, 1), y=round(rng.uniform(10, 90), 1))
            state["t"] += rng.uniform(15, 30)
            roll = rng.random()
            if roll < 0.01 or (roll < 0.19 and yellows.get(who, 0) >= 1):
                add(opp, "card", player=who, outcome="red")
                sent_off.add(who)
                strength[opp] *= 0.75
            elif roll < 0.19:
                yellows[who] = yellows.get(who, 0) + 1
                add(opp, "card", player=who, outcome="yellow")
            return team
        # Turnover: the opponent wins the ball. A pressing side wins it high up the pitch.
        if pressing(opp, minute):
            dx = rng.uniform(62, 82)
        else:
            dx = rng.uniform(22, 52)
        add(opp, rng.choice(["tackle", "interception"]), player=on_pitch(opp), x=round(dx, 1),
            y=round(rng.uniform(10, 90), 1), outcome="won")
        state["t"] += rng.uniform(3, 8)
        return opp

    def next_team(minute: int) -> str:
        ph = strength[HOME] * (1 + momentum[HOME]) * (1.35 if pressing(HOME, minute) else 1.0)
        pa = strength[AWAY] * (1 + momentum[AWAY])
        return HOME if rng.random() < ph / (ph + pa) else AWAY

    add(HOME, "kickoff")
    team = HOME
    for period, end in ((1, 45 * 60 + rng.randint(1, 3) * 60), (2, 90 * 60 + rng.randint(2, 5) * 60)):
        while state["t"] < end:
            minute = int(state["t"] // 60)
            for side in (HOME, AWAY):
                if sub_minutes[side] and minute >= sub_minutes[side][0]:
                    sub_minutes[side].pop(0)
                    idx = rng.randrange(1, 11)
                    off = squads[side][idx]["name"]
                    on = squads[side][state["bench"][side]]["name"] if state["bench"][side] < len(squads[side]) else off
                    state["bench"][side] += 1
                    squads[side][idx] = {"name": on, "pos": squads[side][idx]["pos"]}
                    add(side, "substitution", player=off, detail={"on": on})
            team = simulate_possession(team)
            if rng.random() < 0.35:
                team = next_team(minute)
        add(HOME, "halftime" if period == 1 else "fulltime")
        state["t"] = max(state["t"], 45 * 60.0)

    return Match(
        match_id=f"synthetic-{seed}",
        seed=seed,
        teams=dict(TEAM_NAMES),
        formations=dict(FORMATIONS),
        events=events,
    )
