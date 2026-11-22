"""Keep provenance of provisional text distinct from a 1915 page inspection."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "workspace/reviews"


class ProseWitnessStateTests(unittest.TestCase):
    def test_all_twenty_candidates_keep_secondary_origin_and_primary_page_evidence(self):
        prose = json.loads((ROOT / "print-prose-candidate-v1.json").read_text(encoding="utf-8"))
        visual = json.loads((ROOT / "1915-visual-page-collation-v1.json").read_text(encoding="utf-8"))
        by_key = {r["source_key"]: r for r in visual["records"]}
        self.assertEqual(len(prose["records"]), 20)
        known_sources = {
            "1915_print_pdf_searchable_text_provisional",
            "1915_attributed_secondary_transcription_provisional",
            "1915_attributed_independent_web_transcription_provisional",
        }
        for row in prose["records"]:
            with self.subTest(key=row["source_key"]):
                page = by_key[row["source_key"]]
                self.assertIn(row["source_status"], known_sources)
                self.assertTrue(row["pre_visual_review_source_status"])
                self.assertTrue(page["visual_page_inspected"])
                self.assertTrue(row["print_image_reviewed"])
                self.assertEqual(row["print_page_inspection_status"],
                                 "visually_inspected_not_fully_text_collated")
                self.assertEqual(row["full_transcription_review"],
                                 "pending_character_level_1915_fidelity_review")
                self.assertFalse(row["approved"])
                self.assertFalse(row["print_text_fully_certified"])
                self.assertFalse(page["all_text_punctuation_and_foreign_script_certified"])
                self.assertEqual(row["source_paragraph_id"],
                                 page["original_source_paragraph_xml_id"])
                self.assertEqual(row["visual_print_witness_review"],
                                 "workspace/reviews/1915-visual-page-collation-v1.json")
        self.assertEqual(sum(r["source_status"] ==
                         "1915_print_pdf_searchable_text_provisional"
                         for r in prose["records"]), 3)
        self.assertEqual(sum(r["source_status"] ==
                         "1915_attributed_secondary_transcription_provisional"
                         for r in prose["records"]), 6)
        self.assertEqual(sum(r["source_status"] ==
                         "1915_attributed_independent_web_transcription_provisional"
                         for r in prose["records"]), 11)


if __name__ == "__main__":
    unittest.main()
