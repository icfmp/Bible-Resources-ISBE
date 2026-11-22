"""Ensure the scholarly recovery ledger remains tied to the complete source."""
import json
from pathlib import Path
import unittest

from scripts.audit_empty_paragraphs import inventory

ROOT = Path(__file__).resolve().parents[1]


class EmptyArticleRecoveryLedgerTests(unittest.TestCase):
    def test_all_empty_source_records_are_accounted_for(self):
        corpus = ROOT / "cleaned/en/ISBE.xml"
        ledger = json.loads(
            (ROOT / "workspace/reviews/empty-article-recovery-ledger.json").read_text(encoding="utf-8")
        )
        measured = inventory(corpus)
        self.assertEqual(
            ledger["baseline_canonical_tei_sha256"], measured["source_xml_sha256"]
        )
        expected = {(row["article_key"], row["paragraph_xml_id"]) for row in measured["cases"]}
        recorded = {(row["source_key"], row["paragraph_xml_id"]) for row in ledger["cases"]}
        self.assertEqual(len(ledger["cases"]), 31)
        self.assertEqual(expected, recorded)
        self.assertTrue(all(row["source_status"] == "empty_article" for row in ledger["cases"]))
        self.assertTrue(all(
            row["source_recovery_approved"] is False and
            row["editorial_action"] == "preserve_pending_verification"
            for row in ledger["cases"]
        ))
        self.assertTrue(all(
            row["print_image_reviewed"] is False or
            (row["print_volume"] is not None and row["printed_page"] is not None)
            for row in ledger["cases"]
        ))


if __name__ == "__main__":
    unittest.main()
