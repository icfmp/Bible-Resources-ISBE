"""Make later editorial reports distinguish page inspection from full proofreading."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "workspace" / "reviews"


class ReviewStatusConsistencyTests(unittest.TestCase):
    def test_redirect_notes_do_not_claim_print_pages_are_uninspected(self):
        visual = json.loads((ROOT / "1915-visual-page-collation-v1.json").read_text(encoding="utf-8"))
        redirects = json.loads((ROOT / "redirect-candidate-v1.json").read_text(encoding="utf-8"))
        pages = {x["source_key"]: x for x in visual["records"]}
        self.assertEqual(len(redirects["records"]), 11)
        for row in redirects["records"]:
            with self.subTest(key=row["article_key"]):
                page = pages[row["article_key"]]
                self.assertTrue(page["visual_page_inspected"])
                self.assertTrue(row["source_image_verified"])
                self.assertFalse(row["approved"])
                self.assertFalse(row["print_text_fully_certified"])
                self.assertFalse(page["all_text_punctuation_and_foreign_script_certified"])
                note = row["editorial_note"]
                self.assertIn("Original 1915 printed page visually inspected", note)
                self.assertIn("Complete character-by-character certification", note)
                self.assertIn("pre_visual_review_editorial_note", row)
                self.assertIn("physical 1915 printed-page verification is still pending",
                              row["pre_visual_review_editorial_note"])


if __name__ == "__main__":
    unittest.main()
