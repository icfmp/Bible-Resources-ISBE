"""Guard first-pass full original-image readings without implying editorial approval."""
import json
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "workspace/reviews"

class FirstOriginalPrintReadingTests(unittest.TestCase):
    def test_exact_short_prose_readings_are_bound_to_primary_images(self):
        data = json.loads((REVIEWS / "1915-prose-direct-image-readings-v1.json")
                          .read_text(encoding="utf-8"))
        candidates = {r["source_key"]: r for r in json.loads(
            (REVIEWS / "print-prose-candidate-v1.json").read_text(encoding="utf-8"))["records"]}
        pages = {r["source_key"]: r for r in json.loads(
            (REVIEWS / "1915-visual-page-collation-v1.json").read_text(encoding="utf-8"))["records"]}
        self.assertEqual(data["print_collated_articles"], 5)
        self.assertEqual(data["remaining_prose_articles_pending_initial_exact_print_collation"], 15)
        self.assertEqual({r["source_key"] for r in data["records"]}, {"ABISSEI","MANKIND","BEERA","CHORBE","ITHLAH"})
        for row in data["records"]:
            key = row["source_key"]
            with self.subTest(key=key):
                c, p = candidates[key], pages[key]
                self.assertEqual([row["exact_print_body_reading"]], c["blocks"])
                self.assertEqual(row["original_paragraph_xml_id"], c["source_paragraph_id"])
                self.assertEqual(row["original_paragraph_xml_id"], p["original_source_paragraph_xml_id"])
                self.assertEqual(row["source_pdf_sha256"], p["original_pdf_sha256"])
                self.assertEqual(row["rendered_page_sha256"], p["rendered_jpeg_sha256"])
                self.assertEqual(row["printed_folio"], p["printed_page_number"])
                self.assertEqual(row["source_pdf_page_1_based"], p["pdf_page_1_based"])
                self.assertTrue(row["whole_body_visual_comparison"])
                self.assertEqual(row["foreign_script_present"], key in {"BEERA","CHORBE","ITHLAH"})
                self.assertFalse(row["editorial_approval"])
                self.assertFalse(row["canonical_tei_changed"])
                self.assertFalse(row["full_bibliographic_text_certified_by_independent_reviewer"])
                self.assertIn("github.com/icfmp/Bible-Resources-ISBE/actions/runs/",row["image_evidence_review_job"])
        self.assertEqual(candidates["ABISSEI"]["blocks"][0].split(" ",1)[0],"a-bis'ē-i")
        self.assertTrue(candidates["MANKIND"]["blocks"][0].endswith("to the human nature."))
        self.assertEqual(
            hashlib.sha256((ROOT / "cleaned/en/ISBE.xml").read_bytes()).hexdigest(),
            "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25",
        )

if __name__ == "__main__":
    unittest.main()
