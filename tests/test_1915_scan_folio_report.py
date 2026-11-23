"""Verify independently preserved OCR findings and SHA-pinned image decisions."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "workspace/reports/1915-scan-folio-continuity-v1.json"
MANIFEST = ROOT / "sources/print/1915-volume-witnesses.json"

REVIEWED_FOLIOS = {
    ("1", 408, 409): (374, 375),
    ("2", 408, 409): (1058, 1059),
    ("2", 528, 529): (1174, 1175),
    ("2", 688, 689): (1331, 1332),
    ("2", 706, 707): (1349, 1350),
    ("4", 53, 54): (2149, 2150),
    ("5", 143, 144): (2949, 2950),
}


class FiveVolumeGapReportTests(unittest.TestCase):
    def test_image_review_evidence_and_original_ocr_observations(self):
        d = json.loads(PATH.read_text(encoding="utf-8"))
        witnesses = json.loads(MANIFEST.read_text(encoding="utf-8"))
        by_volume = {x["volume"]: x for x in witnesses["volumes"]}
        self.assertFalse(d["claims_original_book_missing_pages"])
        self.assertFalse(d["correction_authorized"])
        self.assertFalse(d["claims_comprehensive_print_text_collation"])
        rows = d["cases"]
        self.assertEqual(len(rows), 8)
        self.assertEqual(len(rows), d["total_adjacent_jump_candidates"])
        self.assertEqual(d["visually_reviewed_candidate_count"], 8)
        self.assertEqual(d["visually_confirmed_ocr_false_positive_count"], 7)
        self.assertEqual(d["visually_confirmed_source_scan_gap_count"], 1)
        for volume in "12345":
            self.assertEqual(sum(c["volume"] == volume for c in rows),
                             d["by_volume"][volume])

        image_reviewed = []
        source_gaps = []
        for c in rows:
            self.assertEqual(c["pdf_page_after"], c["pdf_page_before"] + 1)
            self.assertEqual(c["unseen_printed_folios"],
                             list(range(c["printed_folio_before"] + 1,
                                        c["printed_folio_after"])))
            self.assertTrue(c["source_scan_only"])
            key = (c["volume"], c["pdf_page_before"], c["pdf_page_after"])
            if c["review_status"] == "ocr_folio_misread_source_images_checked_ai_assisted":
                image_reviewed.append(c)
                self.assertIn(key, REVIEWED_FOLIOS)
                proof = c["image_review"]
                before, after = REVIEWED_FOLIOS[key]
                self.assertEqual((proof["printed_folio_before_read_from_image"],
                                  proof["printed_folio_after_read_from_image"]),
                                 (before, after))
                self.assertEqual(after, before + 1)
                self.assertEqual(proof["pdf_sha256"],
                                 by_volume[c["volume"]]["pdf_sha256"])
                self.assertEqual(proof["source_image_workflow_run"], 45125508778)
                self.assertGreater(proof["source_image_job_id"], 0)
                self.assertEqual(proof["outcome"], "no_folio_gap_in_this_source_scan")
                for tag in ("page_before_jpeg_sha256", "page_after_jpeg_sha256"):
                    self.assertRegex(proof[tag], r"^[a-f0-9]{64}$")
                self.assertNotEqual(c["printed_folio_after"], after,
                                    "Do not rewrite original OCR findings")
            elif c["review_status"] == "source_scan_gap_visually_confirmed_ai_assisted":
                source_gaps.append(c)
                self.assertEqual(key, ("5", 78, 79))
                self.assertEqual(c["unseen_printed_folios"], [2887, 2888])
                for tag in ("page_before_jpeg_sha256", "page_after_jpeg_sha256"):
                    self.assertRegex(c[tag], r"^[a-f0-9]{64}$")
            else:
                self.fail("Unreviewed or unexpected folio state: " + str(key))

        self.assertEqual(len(image_reviewed), 7)
        self.assertEqual(len(source_gaps), 1)
        self.assertEqual({(c["volume"], c["pdf_page_before"], c["pdf_page_after"])
                          for c in image_reviewed}, set(REVIEWED_FOLIOS))
        prior_ocr = next(c for c in image_reviewed
                         if c["volume"] == "5" and c["pdf_page_before"] == 143)
        self.assertEqual(prior_ocr["ocr_neighborhood_review"]["expected_intermediate_folio"],
                         2950)
        self.assertEqual(prior_ocr["ocr_neighborhood_review"]["status"],
                         "strong_ocr_misread_indication_not_image_certified")


if __name__ == "__main__":
    unittest.main()
