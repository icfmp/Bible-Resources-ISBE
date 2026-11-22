"""Guard the 31-entry print recovery against candidate/ledger drift.

This checks provenance and review status, not character-by-character fidelity.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "workspace" / "reviews"


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class PrintRecoveryCandidateConsistencyTests(unittest.TestCase):
    def test_every_candidate_matches_one_print_page_and_original_paragraph(self):
        visual = read("1915-visual-page-collation-v1.json")
        ledger = read("empty-article-recovery-ledger.json")
        prose = read("print-prose-candidate-v1.json")
        redirects = read("redirect-candidate-v1.json")

        pages = {row["source_key"]: row for row in visual["records"]}
        baseline = {row["source_key"]: row for row in ledger["cases"]}
        self.assertEqual(len(pages), 31)
        self.assertEqual(len(baseline), 31)
        self.assertEqual(set(pages), set(baseline))

        candidates = []
        for row in prose["records"]:
            candidates.append((row["source_key"], row["source_paragraph_id"], row,
                               "print_text_fully_certified"))
            self.assertTrue(row["blocks"])
            self.assertTrue(all(isinstance(block, str) and block.strip()
                                for block in row["blocks"]))
        for row in redirects["records"]:
            candidates.append((row["article_key"], row["original_empty_paragraph_id"], row,
                               "print_text_fully_certified"))
            # Some redirects still have only a secondary reading, not a\n            # source-image-collated text. Never fill the gap by inference.\n            if "proposed_print_collated_text" in row:\n                self.assertTrue(row["proposed_print_collated_text"].strip())\n            else:\n                self.assertTrue(row["observed_secondary_witness_text"].strip())\n                self.assertTrue(row["proposed_lead"].strip())
            self.assertTrue(row["proposed_targets"])

        self.assertEqual(len(candidates), 31)
        self.assertEqual(len({key for key, _, _, _ in candidates}), 31)
        self.assertEqual({key for key, _, _, _ in candidates}, set(pages))
        for key, paragraph_id, row, certification_field in candidates:
            with self.subTest(key=key):
                evidence = pages[key]
                original = baseline[key]
                self.assertEqual(paragraph_id, evidence["original_source_paragraph_xml_id"])
                self.assertEqual(paragraph_id, original["paragraph_xml_id"])
                self.assertTrue(evidence["visual_page_inspected"])
                self.assertTrue(original["print_image_reviewed"])
                self.assertFalse(row["approved"])
                self.assertFalse(row[certification_field])
                self.assertFalse(evidence["all_text_punctuation_and_foreign_script_certified"])
                self.assertFalse(evidence["canonical_modification_approved"])
                self.assertFalse(original["source_recovery_approved"])
                self.assertFalse(original["print_transcription_fully_certified"])

        self.assertEqual(
            prose["document_base_sha256"],
            visual["canonical_source_sha256"],
        )
        self.assertEqual(
            redirects["canonical_sha256"],
            visual["canonical_source_sha256"],
        )
        self.assertEqual(
            ledger["baseline_canonical_tei_sha256"],
            visual["canonical_source_sha256"],
        )

    def test_exactly_thirty_distinct_printed_pages_are_accounted_for(self):
        data = read("1915-visual-page-collation-v1.json")
        pages = {(row["scan_volume"], row["printed_page_number"])
                 for row in data["records"]}
        self.assertEqual(len(pages), 30)
        self.assertEqual(data["unique_print_pages_examined"], 30)
        self.assertEqual(data["complete_article_transcriptions_certified"], 0)


if __name__ == "__main__":
    unittest.main()
