"""Check that manual editorial review matches every scanned candidate."""
import json
from pathlib import Path
import unittest
from scripts.audit_editorial_notices import scan

ROOT = Path(__file__).resolve().parents[1]


class EditorialNoticeReviewTests(unittest.TestCase):
    def test_all_reviewed_candidates_match_source(self):
        ledger=json.loads((ROOT/"workspace/reviews/editorial-notices-reviewed-v1.json").read_text(encoding="utf-8"))
        actual=scan(ROOT/"cleaned/en/ISBE.xml")
        self.assertEqual(actual["input_sha256"],ledger["canonical_tei_sha256"])
        expected={(row["article_key"],row["unit_xml_id"]) for row in actual["cases"]}
        checked={(row["source_key"],row["unit_xml_id"]) for row in ledger["entries"]}
        self.assertEqual(len(actual["cases"]),21)
        self.assertEqual(len(ledger["entries"]),21)
        self.assertEqual(expected,checked)
        self.assertTrue(all(row["decision"]=="retain" for row in ledger["entries"]))
        self.assertTrue(all(row["rationale"].strip() for row in ledger["entries"]))


if __name__=="__main__":
    unittest.main()
