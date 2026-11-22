import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_references import audit


class ReferenceAuditTests(unittest.TestCase):
    def test_numbered_entries_are_candidates_not_auto_links(self):
        index = [{"key": "ABIGAIL (1)"}, {"key": "ABIGAIL (2)"}]
        report = {"unresolved_isbe_links": {"ABIGAIL": 3}, "unresolved_link_occurrences": 3}
        result = audit(index, report)
        entry = result["review_queue"][0]
        self.assertEqual(entry["category"], "multiple_numbered_entries")
        self.assertEqual(entry["status"], "needs_review")
        self.assertEqual(entry["review_candidates"], ["ABIGAIL (1)", "ABIGAIL (2)"])

    def test_report_counts_must_match(self):
        with self.assertRaisesRegex(ValueError, "totals mismatch"):
            audit([], {"unresolved_isbe_links": {"X": 2}, "unresolved_link_occurrences": 3})


if __name__ == "__main__":
    unittest.main()
