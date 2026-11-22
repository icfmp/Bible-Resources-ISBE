"""Source-lock the original 1915 print-scan OCR location audit."""
import json
from pathlib import Path
import unittest

from scripts.research_1915_print_pages import expected_volume

ROOT = Path(__file__).resolve().parents[1]


class PrintSourceLocationLedgerTests(unittest.TestCase):
    def test_all_31_source_gaps_are_covered_by_historic_volume(self):
        original = json.loads(
            (ROOT / "workspace/reviews/empty-article-recovery-ledger.json")
            .read_text(encoding="utf-8")
        )
        scans = json.loads(
            (ROOT / "sources/print/1915-volume-witnesses.json")
            .read_text(encoding="utf-8")
        )
        locations = json.loads(
            (ROOT / "workspace/reviews/1915-printed-headword-ocr-locations.json")
            .read_text(encoding="utf-8")
        )
        volumes = {v["volume"]: v for v in scans["volumes"]}
        self.assertEqual(len(volumes), 5)
        self.assertEqual(
            locations["canonical_source_sha256"],
            original["baseline_canonical_tei_sha256"]
        )
        self.assertFalse(locations["source_based_print_image_certification"])
        expected = {
            (row["source_key"], row["paragraph_xml_id"])
            for row in original["cases"]
        }
        actual = {
            (row["source_key"], row["source_paragraph_xml_id"])
            for row in locations["cases"]
        }
        self.assertEqual(len(locations["cases"]), 31)
        self.assertEqual(expected, actual)
        strong = 0
        for row in locations["cases"]:
            with self.subTest(key=row["source_key"]):
                vol = row["expected_print_volume"]
                self.assertEqual(vol, expected_volume(row["source_key"]))
                self.assertEqual(
                    row["scan_pdf_sha256"], volumes[vol]["pdf_sha256"]
                )
                self.assertFalse(row["page_image_visually_reviewed"])
                self.assertFalse(row["original_1915_wording_approved"])
                if row["pdf_page_1_based"] is not None:
                    strong += 1
                    self.assertGreaterEqual(row["ocr_heading_score"], 4)
                    self.assertEqual(
                        row["evidence_status"], "strong_ocr_heading_candidate"
                    )
                    self.assertGreaterEqual(row["pdf_page_1_based"], 1)
                    self.assertLessEqual(
                        row["pdf_page_1_based"], volumes[vol]["pages"]
                    )
                else:
                    self.assertIsNone(row["ocr_heading_score"])
                    self.assertEqual(
                        row["evidence_status"],
                        "not_located_in_original_volume_by_strict_ocr"
                    )
        self.assertEqual(strong, locations["strict_ocr_locations_found"])
        self.assertEqual(strong, 25)
        self.assertEqual(locations["not_yet_located"], 6)


if __name__ == "__main__":
    unittest.main()
