"""Negative controls for non-authoritative six-key print OCR triage."""
import unittest
from scripts.triage_1915_unresolved import GAPS, candidate_pages, score_line

class HistoricalTriageTests(unittest.TestCase):
    def test_6_cases_are_only_in_correct_original_print_volumes(self):
        self.assertEqual(sum(len(x) for x in GAPS.values()),6)
        self.assertEqual(set(GAPS),{"1","3","4","5"})

    def test_heading_candidate_outscores_incidental_article_mention(self):
        key="THOCANUS"
        ctx=("EZEKIAS","TIKVAH")
        heading=score_line("THOCANUS, tho-ka'-nus",key,ctx)
        mention=score_line("Elsewhere the father Thocanus appears.",key,ctx)
        self.assertGreater(heading,mention)

    def test_span_extraction_from_scanned_double_columns(self):
        page="Other article prose in left column             THOCANUS, tho-ka'-nus\n"
        result=candidate_pages([page], "THOCANUS",1,1,("EZEKIAS",), maximum=4)
        self.assertTrue(result)
        self.assertEqual(result[0]["pdf_page_1_based"],1)
        self.assertFalse(result[0]["visually_verified"])

    def test_low_information_normal_prose_not_heading(self):
        results=candidate_pages(["Here we recall the patriarchs of old times."],
            "PATRIARCHS, TESTAMENTS OF THE TWELVE",1,1,("APOCALYPTIC",),maximum=3)
        self.assertFalse(results)

if __name__=="__main__":
    unittest.main()
