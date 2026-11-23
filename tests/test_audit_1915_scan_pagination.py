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
    def test_ten_page_jump_is_not_silently_discarded_on_ocr_evidence(self):
        # Page 2950 misread as 2960; a second, correctly placed 2960
        # provides a strong sequence clue but no visual certification.
        numbers=list(range(2949,2962))
        numbers[1]=2960
        pages=[f"THE INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA {n}" for n in numbers]
        out=audit_pages(pages)
        self.assertEqual(out["adjacent_page_jump_candidates"],1)
        candidate=out["candidate_gaps"][0]
        self.assertEqual(candidate["unseen_printed_folios"],list(range(2950,2960)))
        self.assertTrue(candidate["ocr_followup"]["probable_header_misread_not_image_certified"])
        self.assertEqual(candidate["ocr_followup"]["next_recognized_folio"],2951)
        self.assertEqual(candidate["ocr_followup"]["later_recognized_folio"],2960)
        self.assertFalse(candidate["confirmed_missing_from_print"])

    def test_real_scan_jump_has_no_automatic_ocr_dismissal(self):
        pages=[f"THE INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA {n}"
               for n in (2886,2889,2890,2891,2892)]
        candidate=audit_pages(pages)["candidate_gaps"][0]
        self.assertFalse(candidate["ocr_followup"]["probable_header_misread_not_image_certified"])
        self.assertTrue(candidate["unseen_printed_folios"]==[2887,2888])

    def test_normal_consecutive_printed_folios_not_a_gap(self):
        pages=["INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA 1000",
               "INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA 1001"]
        self.assertEqual(audit_pages(pages)["adjacent_page_jump_candidates"],0)

if __name__=="__main__":
    unittest.main()
