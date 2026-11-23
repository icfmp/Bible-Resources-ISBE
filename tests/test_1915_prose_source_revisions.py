"""Validate source-backed, reversible 1915 prose revisions without promoting them."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "workspace/reviews"

class ProseSourceImageRevisionTests(unittest.TestCase):
    def test_six_revisions_are_source_bound_reversible_and_not_approved(self):
        data = json.loads((REVIEWS / "1915-prose-source-image-revisions-v1.json")
                          .read_text(encoding="utf-8"))
        records = data["records"]
        prose = {r["source_key"]: r for r in json.loads(
            (REVIEWS / "print-prose-candidate-v1.json").read_text(encoding="utf-8"))["records"]}
        pages = {r["source_key"]: r for r in json.loads(
            (REVIEWS / "1915-visual-page-collation-v1.json").read_text(encoding="utf-8"))["records"]}
        self.assertEqual(data["records_count"], 6)
        self.assertTrue(data["originals_untouched"])
        self.assertEqual({r["source_key"] for r in records},
                         {"FROWARDNESS", "HASRAH", "HEMDAN",
                          "SEPHARVITES", "THOCANUS", "THOMEI"})
        for row in records:
            with self.subTest(key=row["source_key"]):
                key = row["source_key"]
                candidate, page = prose[key], pages[key]
                self.assertEqual(candidate["blocks"], [row["proposed_direct_print_reading"]])
                self.assertEqual(candidate["pre_second_direct_facsimile_blocks"],
                                 row["original_secondary_candidate_blocks"])
                self.assertNotEqual(candidate["blocks"], row["original_secondary_candidate_blocks"])
                self.assertEqual(row["original_paragraph_xml_id"], candidate["source_paragraph_id"])
                self.assertEqual(row["original_paragraph_xml_id"], page["original_source_paragraph_xml_id"])
                self.assertEqual(row["original_pdf_sha256"], page["original_pdf_sha256"])
                self.assertEqual(row["rendered_print_page_sha256"], page["rendered_jpeg_sha256"])
                self.assertEqual(row["printed_folio"], page["printed_page_number"])
                self.assertIn("/actions/runs/",row["magnified_print_evidence_job"])
                self.assertTrue(row["direct_primary_image_inspected"])
                self.assertFalse(row["independent_second_reading_complete"])
                self.assertFalse(row["canonical_change_approved"])
                self.assertFalse(row["publication_rights_cleared"])
                self.assertFalse(candidate["approved"])
                self.assertFalse(candidate["print_text_fully_certified"])

if __name__ == "__main__":
    unittest.main()
