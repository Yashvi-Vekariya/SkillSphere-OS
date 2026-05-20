import unittest

from backend.scoring import score_assessment


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.competency = {
            "required_score": 80,
            "steps": ["A", "B", "C", "D"],
        }

    def test_verified_when_steps_and_quality_are_strong(self):
        result = score_assessment(
            {
                "observed_steps": ["A", "B", "C", "D"],
                "evidence_quality": 92,
                "safety_events": 0,
            },
            self.competency,
        )
        self.assertEqual(result["status"], "verified")
        self.assertGreaterEqual(result["score"], 80)

    def test_safety_event_blocks_assessment(self):
        result = score_assessment(
            {
                "observed_steps": ["A", "B", "C", "D"],
                "evidence_quality": 95,
                "safety_events": 1,
            },
            self.competency,
        )
        self.assertEqual(result["status"], "blocked")

    def test_missing_steps_create_coaching_action(self):
        result = score_assessment(
            {
                "observed_steps": ["A"],
                "evidence_quality": 70,
                "safety_events": 0,
            },
            self.competency,
        )
        self.assertEqual(result["status"], "coaching_required")
        self.assertIn("B", result["coach_action"])


if __name__ == "__main__":
    unittest.main()
