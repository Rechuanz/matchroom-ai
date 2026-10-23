import unittest

from matchroom.agents import fact_checker
from matchroom.agents.claims import Claim
from matchroom.generator import generate_match
from matchroom.moments import detect_moments
from matchroom.pipeline import build_recap
from matchroom.schema import Match


class GeneratorTests(unittest.TestCase):
    def test_same_seed_same_match(self):
        self.assertEqual(generate_match(3).to_dict(), generate_match(3).to_dict())

    def test_different_seed_different_match(self):
        self.assertNotEqual(generate_match(3).to_dict(), generate_match(4).to_dict())

    def test_match_is_football_shaped(self):
        match = generate_match(7)
        types = {e.type for e in match.events}
        self.assertTrue({"kickoff", "pass", "shot", "halftime", "fulltime"} <= types)
        self.assertGreater(len(match.events), 200)
        clocks = [e.clock for e in match.events]
        self.assertEqual(clocks, sorted(clocks))
        self.assertEqual([e.id for e in match.events], list(range(1, len(match.events) + 1)))

    def test_scorelines_are_realistic(self):
        matches = [generate_match(s) for s in range(1, 31)]
        goals = [sum(m.score().values()) for m in matches]
        shots = [sum(e.type == "shot" for e in m.events) for m in matches]
        self.assertTrue(2.0 <= sum(goals) / len(goals) <= 4.0)
        self.assertTrue(15 <= sum(shots) / len(shots) <= 30)

    def test_roundtrip_through_dict(self):
        match = generate_match(5)
        self.assertEqual(Match.from_dict(match.to_dict()).to_dict(), match.to_dict())


class FactCheckerTests(unittest.TestCase):
    def setUp(self):
        self.match = generate_match(7)
        self.shot = next(e for e in self.match.events if e.type == "shot")

    def test_accepts_true_claim(self):
        claim = Claim("x", [self.shot.id], {"team": self.shot.team, "event_type": "shot", "count": 1})
        self.assertTrue(fact_checker.verify(claim, self.match).verified)

    def test_rejects_wrong_team(self):
        wrong = "AWAY" if self.shot.team == "HOME" else "HOME"
        claim = Claim("x", [self.shot.id], {"team": wrong})
        self.assertFalse(fact_checker.verify(claim, self.match).verified)

    def test_rejects_missing_event_and_wrong_count(self):
        claim = Claim("x", [999999], {"count": 2})
        result = fact_checker.verify(claim, self.match)
        self.assertFalse(result.verified)
        self.assertGreaterEqual(len(result.problems), 2)

    def test_rejects_claim_without_evidence(self):
        self.assertFalse(fact_checker.verify(Claim("x", []), self.match).verified)


class PipelineTests(unittest.TestCase):
    def test_moments_have_evidence(self):
        match = generate_match(7)
        moments = detect_moments(match)
        self.assertTrue(moments)
        for m in moments:
            self.assertTrue(m.evidence)

    def test_recap_claims_all_verify_across_seeds(self):
        for seed in range(1, 21):
            recap = build_recap(generate_match(seed))
            self.assertEqual(recap["rejected_claims"], 0, f"seed {seed}")
            self.assertIn("-", recap["text"].splitlines()[0])


if __name__ == "__main__":
    unittest.main()
