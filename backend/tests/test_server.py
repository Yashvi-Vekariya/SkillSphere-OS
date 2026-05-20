import unittest

from backend.server import build_overview


class ServerHelperTests(unittest.TestCase):
    def test_overview_counts_core_objects(self):
        overview = build_overview(
            {
                "learners": [{"id": "L1"}],
                "competencies": [{"id": "C1"}],
                "assessments": [{"id": "A1", "score": 88, "status": "verified"}],
                "credentials": [{"id": "R1"}],
            }
        )
        self.assertEqual(overview["learners"], 1)
        self.assertEqual(overview["average_score"], 88)
        self.assertTrue(overview["compliance_ready"])


if __name__ == "__main__":
    unittest.main()
