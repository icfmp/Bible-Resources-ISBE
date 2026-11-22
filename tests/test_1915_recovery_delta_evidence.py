"""Ensure all historical recovery deltas are reproducible and source-locked."""
import hashlib
import json
from pathlib import Path
import unittest

from scripts.report_1915_recovery_deltas import build, text_sha

ROOT = Path(__file__).resolve().parents[1]


class RecoveryDeltaEvidenceTests(unittest.TestCase):
    def test_complete_traceability_without_canonical_modification(self):
        canonical = ROOT / "cleaned/en/ISBE.xml"
        before = hashlib.sha256(canonical.read_bytes()).hexdigest()
        result = build(ROOT)
        self.assertEqual(result["canonical_source_sha256"], before)
        self.assertEqual(result["original_article_count"], 9380)
        self.assertEqual(result["affected_originally_empty_articles"], 31)
        self.assertEqual(result["candidate_prose"], 20)
        self.assertEqual(result["candidate_redirects"], 11)
        self.assertEqual(result["source_print_pages"], 30)
        self.assertEqual(len(result["entries"]), 31)
        self.assertEqual(len({r["source_key"] for r in result["entries"]}), 31)
        for row in result["entries"]:
            with self.subTest(key=row["source_key"]):
                self.assertEqual(row["original_text_sha256"], text_sha(""))
                self.assertEqual(len(row["candidate_block_sha256"]), row["candidate_block_count"])
                self.assertTrue(all(len(x) == 64 for x in row["candidate_block_sha256"]))
                self.assertTrue(row["page_visually_inspected"])
                self.assertFalse(row["complete_transcription_certified"])
                self.assertFalse(row["canonical_change_approved"])
                self.assertTrue(row["evidence_workflow_run"].startswith(
                    "https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/"))
        self.assertEqual(hashlib.sha256(canonical.read_bytes()).hexdigest(), before)

    def test_candidate_hashes_match_exact_current_unapproved_text(self):
        review = ROOT / "workspace/reviews"
        prose = json.loads((review / "print-prose-candidate-v1.json").read_text(encoding="utf-8"))
        redirects = json.loads((review / "redirect-candidate-v1.json").read_text(encoding="utf-8"))
        by_key = {r["source_key"]: r for r in build(ROOT)["entries"]}
        for r in prose["records"]:
            self.assertEqual(by_key[r["source_key"]]["candidate_block_sha256"],
                             [text_sha(b) for b in r["blocks"]])
        for r in redirects["records"]:
            text = r.get("proposed_print_collated_text") or r["observed_secondary_witness_text"]
            self.assertEqual(by_key[r["article_key"]]["candidate_block_sha256"], [text_sha(text)])


if __name__ == "__main__":
    unittest.main()
