"""Lock all 20 machine-OCR concordance observations to exact source revisions.

A high text match is not print-page typography certification.
"""
import hashlib
import json
from pathlib import Path
import unittest

from scripts.audit_1915_prose_evidence import audit

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "workspace/reviews"


def git_blob_sha1(path):
    contents = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(contents)).encode() + b"\0" + contents).hexdigest()


class OriginalProseOCRReportTests(unittest.TestCase):
    def test_all_twenty_are_accounted_for_with_reproducible_source_locks(self):
        data = json.loads((REVIEWS / "1915-prose-ocr-concordance-v1.json")
                          .read_text(encoding="utf-8"))
        audited = {r["source_key"]: r for r in audit(ROOT)["records"]}
        self.assertEqual(data["canonical_source_sha256"],
                         hashlib.sha256((ROOT / "workspace/witnesses/crosswire-2.2/ISBE.xml").read_bytes()).hexdigest())
        self.assertEqual(data["candidate_file_git_blob_sha1"],
                         git_blob_sha1(REVIEWS / "print-prose-candidate-v1.json"))
        self.assertEqual(data["visual_page_evidence_git_blob_sha1"],
                         git_blob_sha1(REVIEWS / "1915-visual-page-collation-v1.json"))
        self.assertEqual(len(data["records"]), 20)
        self.assertEqual({r["source_key"] for r in data["records"]}, set(audited))
        self.assertEqual(data["fully_character_collated_articles"], 0)
        self.assertFalse(data["source_rights_cleared"])
        self.assertFalse(data["editorial_approval"])
        for row in data["records"]:
            with self.subTest(key=row["source_key"]):
                original = audited[row["source_key"]]
                self.assertEqual(row["source_paragraph_xml_id"],
                                 original["source_paragraph_xml_id"])
                self.assertEqual(row["original_pdf_sha256"],
                                 original["original_pdf_sha256"])
                self.assertEqual(row["volume"], original["printed_volume"])
                self.assertEqual(row["pdf_page_1_based"],
                                 original["pdf_page_1_based"])
                self.assertTrue(row["ocr_collation_only"])
                self.assertFalse(row["full_print_text_certified"])
                self.assertGreater(row["candidate_token_count"], 0)
                self.assertLessEqual(row["matched_candidate_tokens"],
                                     row["candidate_token_count"])
                self.assertTrue(0 <= row["ordered_token_recall"] <= 1)
        self.assertEqual(
            set(data["high_priority_image_review"]),
            {r["source_key"] for r in data["records"]
             if r["ordered_token_recall"] < 0.8},
        )


if __name__ == "__main__":
    unittest.main()
