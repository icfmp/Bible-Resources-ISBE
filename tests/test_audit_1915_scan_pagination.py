import unittest
from scripts.audit_1915_scan_pagination import audit_pages, printed_folio

class ScanPaginationTests(unittest.TestCase):
    def test_detects_adjacent_original_folio_jump_as_candidate_only(self):
        pages=[
            "Syrians    THE INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA  2886\ntext",
            "Tabernacle  THE INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA  2889\ntext"]
        out=audit_pages(pages)
        self.assertEqual(out["recognized_printed_folios"],2)
        self.assertEqual(out["adjacent_page_jump_candidates"],1)
        self.assertEqual(out["candidate_gaps"][0]["unseen_printed_folios"],[2887,2888])
        self.assertFalse(out["candidate_gaps"][0]["confirmed_missing_from_print"])
    def test_unreadable_or_ambiguous_headers_do_not_invent_folios(self):
        self.assertIsNone(printed_folio("UNKNOWN TITLE 2003 2004\ntext"))
        self.assertIsNone(printed_folio("THE INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA 1200 1300\ntext"))
        self.assertEqual(audit_pages(["random text","THE INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA 1300"])["adjacent_page_jump_candidates"],0)
    def test_normal_consecutive_printed_folios_not_a_gap(self):
        pages=["INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA 1000",
               "INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA 1001"]
        self.assertEqual(audit_pages(pages)["adjacent_page_jump_candidates"],0)

if __name__=="__main__":
    unittest.main()
