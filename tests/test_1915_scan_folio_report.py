"""Source-fidelity and evidence-status controls for five-volume pagination reports."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"workspace/reports/1915-scan-folio-continuity-v1.json"

class FiveVolumeGapReportTests(unittest.TestCase):
    def test_gap_report_covers_all_volumes_without_claiming_print_absence(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertFalse(d["claims_original_book_missing_pages"])
        self.assertFalse(d["correction_authorized"])
        self.assertFalse(d["claims_comprehensive_print_text_collation"])
        rows=d["cases"]
        self.assertEqual(len(rows),d["total_adjacent_jump_candidates"])
        for volume in "12345":
            self.assertEqual(sum(c["volume"]==volume for c in rows),d["by_volume"][volume])
        for c in rows:
            self.assertEqual(c["pdf_page_after"],c["pdf_page_before"]+1)
            self.assertEqual(c["unseen_printed_folios"],
                             list(range(c["printed_folio_before"]+1,c["printed_folio_after"])))
            self.assertTrue(c["source_scan_only"])
            self.assertIn(c["review_status"],
                          {"source_scan_gap_visually_confirmed_ai_assisted","ocr_candidate_unreviewed"})
        observed=[c for c in rows if c["review_status"]=="source_scan_gap_visually_confirmed_ai_assisted"]
        self.assertEqual(len(observed),1)
        self.assertEqual(observed[0]["volume"],"5")
        self.assertEqual(observed[0]["unseen_printed_folios"],[2887,2888])
        for p in ("page_before_jpeg_sha256","page_after_jpeg_sha256"):
            self.assertRegex(observed[0][p],r"^[a-f0-9]{64}$")

if __name__=="__main__":
    unittest.main()
