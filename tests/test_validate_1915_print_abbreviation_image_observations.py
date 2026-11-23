"""Provenance, source-key and no-certification controls for 1915 AV/RV examples."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from scripts.audit_1915_article_ocr_word_counts import LOCK, digest
from scripts.validate_1915_print_abbreviation_image_observations import validate


ROOT = Path(__file__).resolve().parents[1]


class Original1915AbbreviationImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def read(path):
            return json.loads((ROOT / path).read_text(encoding="utf-8"))
        cls.ledger = read(
            "workspace/reviews/1915-print-abbreviation-image-observations-v1.json"
        )
        cls.sources = read("workspace/witnesses/print/1915-volume-witnesses.json")
        cls.root = ET.parse(ROOT / "workspace/witnesses/crosswire-2.2/ISBE.xml").getroot()
        cls.lock = digest(ROOT / "workspace/witnesses/crosswire-2.2/ISBE.xml")

    def check(self, ledger):
        return validate(ledger, self.sources, self.root, self.lock)

    def test_three_original_image_observations_are_bounded_and_identity_verified(self):
        result = self.check(self.ledger)
        self.assertEqual(set(result), {"ABIDE", "MEADOW", "REPAIR"})
        self.assertEqual(self.lock, LOCK)
        self.assertTrue(all(not r["full_article_print_certified"]
                            for r in result.values()))

    def test_no_revision_or_publication_claim_possible(self):
        x = deepcopy(self.ledger)
        x["entries"][0]["source_digital_text_changed"] = True
        with self.assertRaises(ValueError):
            self.check(x)
        x = deepcopy(self.ledger)
        x["entries"][1]["approved_textual_corrections"] = ["made-up"]
        with self.assertRaises(ValueError):
            self.check(x)
        x = deepcopy(self.ledger)
        x["entries"][2]["full_historical_prose_collation_completed"] = True
        with self.assertRaises(ValueError):
            self.check(x)

    def test_source_key_and_id_cannot_be_exchanged(self):
        x = deepcopy(self.ledger)
        x["entries"][0]["source_article_xml_id"] = x["entries"][1]["source_article_xml_id"]
        with self.assertRaises(ValueError):
            self.check(x)

    def test_print_volume_and_hash_must_be_source_locked(self):
        x = deepcopy(self.ledger)
        x["entries"][1]["original_pdf_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            self.check(x)
        x = deepcopy(self.ledger)
        x["entries"][2]["research_jpeg_sha256"] = "not-a-source-image-hash"
        with self.assertRaises(ValueError):
            self.check(x)

    def test_expansion_must_exist_in_canonical_article_without_source_rewrite(self):
        x = deepcopy(self.ledger)
        x["entries"][0]["digital_expansions_seen"][0] = "fictional expansion"
        with self.assertRaises(ValueError):
            self.check(x)
        x = deepcopy(self.ledger)
        x["entries"][0]["digital_expansions_seen"][0] = "Greek"
        with self.assertRaises(ValueError):
            self.check(x)

    def test_print_abbreviation_pairing_is_not_a_permissive_normalization(self):
        x = deepcopy(self.ledger)
        x["entries"][0]["printed_abbreviations_seen"][0] = "SOMETHING"
        with self.assertRaises(ValueError):
            self.check(x)
        x = deepcopy(self.ledger)
        x["entries"][0]["printed_abbreviations_seen"].append("AV")
        with self.assertRaises(ValueError):
            self.check(x)

    def test_no_omission_or_authorial_certification_comes_from_image_observation(self):
        x = deepcopy(self.ledger)
        x["full_edition_print_certified"] = True
        with self.assertRaises(ValueError):
            self.check(x)
        x = deepcopy(self.ledger)
        x["text_redistribution_authorized"] = True
        with self.assertRaises(ValueError):
            self.check(x)


if __name__ == "__main__":
    unittest.main()
