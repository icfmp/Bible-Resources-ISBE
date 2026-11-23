"""Negative controls for SHA-locked 1915 printed-heading visual audit."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.validate_1915_ocr_print_heading_visual_inspection import validate

ROOT = Path(__file__).resolve().parents[1]


class PrintHeadingVisualProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def read(path):
            return json.loads((ROOT / path).read_text(encoding="utf-8"))
        cls.ledger = read("workspace/reviews/1915-ocr-print-heading-visual-inspection-v1.json")
        cls.manifest = read("sources/print/1915-volume-witnesses.json")
        cls.article_index = read("cleaned/en/article-index.json")

    def try_check(self, ledger):
        return validate(ledger, self.manifest, self.article_index)

    def test_actual_five_original_sha_locks_and_distinct_outcomes(self):
        result = self.try_check(self.ledger)
        self.assertEqual(result["case_count"], 5)
        self.assertEqual(result["categories"]["visually_confirmed_intervening_print_article"], 3)
        self.assertEqual(result["categories"][
            "visually_checked_heading_boundary_no_intervening_print_article_seen"], 2)
        self.assertEqual(result["textual_corrections_authorized"], 0)
        self.assertFalse(result["publication_permitted"])

    def test_unearned_full_article_approval_is_rejected(self):
        ledger = deepcopy(self.ledger)
        ledger["records"][0]["print_content_certified"] = True
        with self.assertRaises(ValueError):
            self.try_check(ledger)

    def test_wrong_jpeg_or_original_volume_hash_is_rejected(self):
        ledger = deepcopy(self.ledger)
        ledger["records"][0]["pages"][0]["image_sha256"] = "not-an-authentic-sha"
        with self.assertRaises(ValueError):
            self.try_check(ledger)
        ledger = deepcopy(self.ledger)
        ledger["records"][0]["source_pdf_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            self.try_check(ledger)

    def test_invented_original_source_key_or_xml_identity_is_rejected(self):
        ledger = deepcopy(self.ledger)
        ledger["records"][0]["intervening_source_article_xml_id"] = "invented"
        with self.assertRaises(ValueError):
            self.try_check(ledger)
        ledger = deepcopy(self.ledger)
        ledger["records"][0]["source_article_xml_id"] = "invented"
        with self.assertRaises(ValueError):
            self.try_check(ledger)

    def test_duplicate_article_or_page_image_is_rejected(self):
        ledger = deepcopy(self.ledger)
        ledger["records"].append(deepcopy(ledger["records"][0]))
        with self.assertRaises(ValueError):
            self.try_check(ledger)
        ledger = deepcopy(self.ledger)
        ledger["records"][0]["pages"].append(deepcopy(ledger["records"][0]["pages"][0]))
        with self.assertRaises(ValueError):
            self.try_check(ledger)

    def test_pretended_printed_heading_proof_cannot_be_promoted(self):
        ledger = deepcopy(self.ledger)
        ledger["records"][0]["editorial_correction_approved"] = True
        with self.assertRaises(ValueError):
            self.try_check(ledger)
        ledger = deepcopy(self.ledger)
        ledger["redistribution_authorized"] = True
        with self.assertRaises(ValueError):
            self.try_check(ledger)

    def test_source_pdf_page_number_must_exist_in_original_volume(self):
        ledger = deepcopy(self.ledger)
        ledger["records"][0]["pages"][-1]["pdf_page_1_based"] = 760
        with self.assertRaises(ValueError):
            self.try_check(ledger)

    def test_nonconflict_cannot_invent_an_intervening_article(self):
        ledger = deepcopy(self.ledger)
        for record in ledger["records"]:
            if record["classification"] == (
                    "visually_checked_heading_boundary_no_intervening_print_article_seen"):
                record["intervening_source_key"] = "JOHN THE BAPTIST"
                break
        with self.assertRaises(ValueError):
            self.try_check(ledger)


if __name__ == "__main__":
    unittest.main()
