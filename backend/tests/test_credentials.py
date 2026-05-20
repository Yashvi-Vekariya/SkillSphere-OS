import unittest

from backend.credentials import issue_credential


class CredentialTests(unittest.TestCase):
    def test_credential_contains_proof_hash(self):
        credential = issue_credential(
            {"id": "LRN-1"},
            {"id": "CMP-1", "name": "Demo Skill"},
            {"id": "ASM-1", "score": 91},
        )
        self.assertEqual(len(credential["proof_hash"]), 64)
        self.assertEqual(credential["title"], "Demo Skill")
        self.assertEqual(credential["chain"], "local-tamper-evident-ledger")


if __name__ == "__main__":
    unittest.main()
