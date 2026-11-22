"""Verify scoped, page-bound exact printed readings of historical short redirects."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "workspace/reviews"


def read(name):
    return json.loads((REVIEWS / name).read_text(encoding="utf-8"))


class ShortRedirectPrintedTextCollationTests(unittest.TestCase):
    def test_nine_complete_short_redirect_bodies_match_unapproved_candidates(self):
        proof = read("1915-short-redirect-text-collation-v1.json")
        redirects = read("redirect-candidate-v1.json")
        pages = read("1915-visual-page-collation-v1.json")
        canonical = hashlib.sha256((ROOT / "cleaned/en/ISBE.xml").read_bytes()).hexdigest()
        self.assertEqual(proof["canonical_source_sha256"], canonical)
        self.assertEqual(proof["compared_short_redirect_paragraphs"], 9)
        self.assertEqual(len(proof["records"]), 9)
        self.assertEqual(len(proof["remaining_redirects_pending_exact_body_proofreading"]), 2)
        candidates = {r["article_key"]: r for r in redirects["records"]}
        visual = {r["source_key"]: r for r in pages["records"]}
        checked = set()
        for row in proof["records"]:
            key = row["source_key"]
            with self.subTest(source_key=key):
                self.assertNotIn(key, checked)
                checked.add(key)
                candidate = candidates[key]
                page = visual[key]
                self.assertEqual(row["original_paragraph_xml_id"],
                                 candidate["original_empty_paragraph_id"])
                self.assertEqual(row["original_paragraph_xml_id"],
                                 page["original_source_paragraph_xml_id"])
                self.assertEqual(row["exact_candidate_paragraph_reading"],
                                 candidate["proposed_print_collated_text"])
                self.assertTrue(row["printed_entry_reading_with_heading"].startswith(key))
                self.assertTrue(row["printed_entry_reading_with_heading"].endswith(
                    row["exact_candidate_paragraph_reading"]))
                self.assertEqual(row["source_pdf_volume"], page["scan_volume"])
                self.assertEqual(row["source_pdf_page_1_based"], page["pdf_page_1_based"])
                self.assertEqual(row["printed_page"], page["printed_page_number"])
                self.assertEqual(row["original_pdf_sha256"], page["original_pdf_sha256"])
                self.assertEqual(row["rendered_page_jpeg_sha256"],
                                 page["rendered_jpeg_sha256"])
                self.assertEqual(row["evidence_workflow_run"], page["evidence_workflow_run"])
                self.assertTrue(page["visual_page_inspected"])
                self.assertTrue(row["inspected_at_2000px"])
                self.assertFalse(row["editorial_approval"])
                self.assertFalse(row["canonical_change"])
                self.assertFalse(candidate["approved"])
                self.assertFalse(candidate["print_text_fully_certified"])
        self.assertEqual(checked | set(proof["remaining_redirects_pending_exact_body_proofreading"]),
                         set(candidates))
        self.assertFalse(checked & set(proof["remaining_redirects_pending_exact_body_proofreading"]))

    def test_historical_section_and_linewrap_readings_do_not_drift(self):
        rows = {r["source_key"]: r["exact_candidate_paragraph_reading"]
                for r in read("1915-short-redirect-text-collation-v1.json")["records"]}
        self.assertEqual(rows["PATRIARCHS, TESTAMENTS OF THE TWELVE"],
                         "See APOCALYPTIC LITERATURE, IV, 1.")
        self.assertEqual(rows["PAUL, VOYAGE AND SHIPWRECK OF"],
                         "See PAUL THE APOSTLE, V, 9; PHOENIX.")
        self.assertEqual(rows["COMING OF CHRIST"], "See ADVENT; PAROUSIA.")


if __name__ == "__main__":
    unittest.main()
