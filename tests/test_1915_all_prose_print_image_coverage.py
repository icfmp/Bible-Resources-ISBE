"""Show all 20 provisional prose candidates have original-page first-pass reading evidence.

Original-image inspection is distinct from independent editorial certification.
"""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]/"workspace/reviews"
def read(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))

class WholeProsePrintedPageCoverage(unittest.TestCase):
    def test_twenty_candidates_have_two_nonoverlapping_proof_ledgers(self):
        direct=read("1915-prose-direct-image-readings-v1.json")["records"]
        revisions=read("1915-prose-source-image-revisions-v1.json")["records"]
        candidates={r["source_key"]:r for r in read("print-prose-candidate-v1.json")["records"]}
        visual={r["source_key"]:r for r in read("1915-visual-page-collation-v1.json")["records"]}
        self.assertEqual(len(direct),14)
        self.assertEqual(len(revisions),6)
        first={r["source_key"]:r for r in direct}
        second={r["source_key"]:r for r in revisions}
        self.assertFalse(set(first)&set(second))
        self.assertEqual(set(first)|set(second),set(candidates))
        self.assertEqual(len(candidates),20)
        for key,entry in first.items():
            with self.subTest(key=key):
                page=visual[key]
                self.assertEqual(entry["source_pdf_sha256"],page["original_pdf_sha256"])
                self.assertEqual(entry["rendered_page_sha256"],page["rendered_jpeg_sha256"])
                self.assertEqual(entry["original_paragraph_xml_id"],candidates[key]["source_paragraph_id"])
                expected_blocks = entry.get("exact_print_body_blocks")
                if expected_blocks is None:
                    expected_blocks = [entry["exact_print_body_reading"]]
                self.assertEqual(candidates[key]["blocks"], expected_blocks)
                self.assertTrue(entry["whole_body_visual_comparison"])
                self.assertFalse(entry["full_bibliographic_text_certified_by_independent_reviewer"])
        for key,entry in second.items():
            with self.subTest(key=key):
                page=visual[key]
                self.assertEqual(entry["original_pdf_sha256"],page["original_pdf_sha256"])
                self.assertEqual(entry["rendered_print_page_sha256"],page["rendered_jpeg_sha256"])
                self.assertEqual(entry["original_paragraph_xml_id"],candidates[key]["source_paragraph_id"])
                self.assertTrue(entry["direct_primary_image_inspected"])
                self.assertFalse(entry["independent_second_reading_complete"])
                self.assertEqual(candidates[key]["blocks"],[entry["proposed_direct_print_reading"]])
        for key,entry in candidates.items():
            with self.subTest(key=key):
                self.assertFalse(entry["approved"])
                self.assertFalse(entry["print_text_fully_certified"])

if __name__=="__main__":
    unittest.main()
