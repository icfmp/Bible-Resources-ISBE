"""The FR pilot selects 50 *real* articles from the immutable English index."""
import json
import unittest
from pathlib import Path

from scripts.select_translation_pilot import (
    SOURCE_SHA256, SOURCE_COUNT, ANCHORS, PILOT_COUNT, SLOTS, select,
)
from scripts.validate_translation_identity import sha256

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml"


class TranslationPilotSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selection = select(SOURCE)

    def test_source_and_roster_are_exact(self):
        report = self.selection
        self.assertEqual(report["source_sha256"], SOURCE_SHA256)
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(report["source_article_count"], SOURCE_COUNT)
        self.assertEqual(report["pilot_article_count"], PILOT_COUNT)
        self.assertEqual(len(report["articles"]), 50)
        self.assertEqual(report["summary"]["pending"], 50)
        self.assertEqual(report["summary"]["translated"], 0)
        self.assertEqual(report["summary"]["human_reviewed"], 0)
        self.assertFalse(report["published"])

    def test_original_article_identifiers_keys_and_order(self):
        article_rows = self.selection["articles"]
        self.assertEqual(len({r["source_key"] for r in article_rows}), 50)
        self.assertEqual(len({r["article_id"] for r in article_rows}), 50)
        self.assertEqual([r["source_position"] for r in article_rows],
                         sorted(r["source_position"] for r in article_rows))
        self.assertTrue(set(ANCHORS).issubset(
            {r["source_key"] for r in article_rows}))
        self.assertEqual(self.selection["summary"]["selection_criteria"],
                         {"source_attested_anchor": 10, **dict(SLOTS)})
        for row in article_rows:
            self.assertTrue(row["article_id"].startswith("isbe-"))
            self.assertEqual(len(row["source_article_sha256"]), 64)
            self.assertEqual(row["translation_status"], "pending")
            self.assertEqual(row["editorial_review_status"], "not_started")

    def test_deterministic_selector_does_not_infer_french_article_ids(self):
        rerun = select(SOURCE)
        self.assertEqual(json.dumps(self.selection, sort_keys=True),
                         json.dumps(rerun, sort_keys=True))
        self.assertNotIn("translation_text", json.dumps(rerun))

    def test_fail_closed_on_wrong_source_hash_or_article_count(self):
        with self.assertRaisesRegex(ValueError, "source revision"):
            select(SOURCE, expected_sha="0" * 64)
        with self.assertRaisesRegex(ValueError, "article count"):
            select(SOURCE, expected_count=SOURCE_COUNT + 1)


if __name__ == "__main__":
    unittest.main()
