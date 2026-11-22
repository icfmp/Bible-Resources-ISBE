"""Tests for the historical witness comparison, without network access."""
import unittest
from scripts.research_1915_empty_articles import clean, search_headword, analyze

class OCRWitnessMatchingTests(unittest.TestCase):
    def test_prefix_only_matching_and_false_mention(self):
        lines=["A sentence about AMNON as a person.", "AMNON, am-non", "First son.", "AMNONITES", "ABISSEI", "This is a paragraph."]
        hits=search_headword(lines,"AMNON")
        self.assertEqual([r["line_number"] for r in hits],[2])
        self.assertEqual(search_headword(lines,"ABISSEI")[0]["line_number"],5)

    def test_punctuation_normalization(self):
        self.assertEqual(clean("ASTARTE; ASTORETH"),"ASTARTE ASTORETH")
        self.assertEqual(search_headword(["ASTARTE; ASTORETH, a name"],"ASTARTE; ASTORETH")[0]["line_number"],1)

    def test_not_a_publication_decision(self):
        ledger={"cases":[{"source_key":"AMNON","paragraph_xml_id":"stable-id"}]}
        ocr={"I":{"lines":["AMNON, am-non"]}}
        cases=analyze(ledger,ocr)
        self.assertEqual(len(cases),1)
        self.assertFalse(cases[0]["source_transcription_approved"])
        self.assertFalse(cases[0]["printed_page_verified"])

if __name__=="__main__":
    unittest.main()
