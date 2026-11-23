"""Adversarial provenance checks for image-attested 1915 prose spot-checks."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from scripts.audit_1915_article_ocr_word_counts import LOCK, digest
from scripts.validate_1915_low_overlap_prose_spotchecks import validate

ROOT = Path(__file__).resolve().parents[1]


class PrintedProseSpotcheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((ROOT / "workspace/reviews/1915-low-overlap-prose-image-spotchecks-v2.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "sources/print/1915-volume-witnesses.json").read_text(encoding="utf-8"))
        cls.tei_file = ROOT / "cleaned/en/ISBE.xml"
        cls.root = ET.parse(cls.tei_file).getroot()
        cls.digest = digest(cls.tei_file)

    def check(self, ledger):
        return validate(ledger, self.manifest, self.root, self.digest)

    def test_source_locked_bounded_case_inventory(self):
        result = self.check(self.ledger)
        self.assertEqual(self.digest, LOCK)
        self.assertEqual(result["source_articles_checked"], 13)
        self.assertEqual(result["bounded_differences_checked"], 15)
        self.assertFalse(result["full_historical_articles_collated"])
        self.assertFalse(result["textual_corrections_approved"])

    def test_unearned_approval_and_publication_are_rejected(self):
        for field in ("full_article_collation_completed",
                      "editorial_corrections_approved",
                      "redistribution_authorized",
                      "original_crosswire_or_canonical_tei_modified"):
            bad = deepcopy(self.ledger)
            bad[field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check(bad)
        for field in ("full_article_prose_verified",
                      "correction_authorized", "publication_permitted"):
            bad = deepcopy(self.ledger)
            bad["entries"][0][field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check(bad)

    def test_identity_witness_and_digest_are_required(self):
        for field, replacement in (
            ("source_article_xml_id", "isbe-invented"),
            ("original_pdf_sha256", "f" * 64),
            ("research_jpeg_sha256", "not-an-image-sha"),
            ("volume", "5"),
            ("pdf_page_1_based", 9999),
        ):
            bad = deepcopy(self.ledger)
            bad["entries"][0][field] = replacement
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check(bad)
        bad = deepcopy(self.ledger)
        bad["canonical_tei_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            self.check(bad)

    def test_no_source_correction_by_fabricated_fragment(self):
        bad = deepcopy(self.ledger)
        bad["entries"][0]["fragments"][0]["digital_source_exact"] = "an entirely imaginary 1915 editorial source reading"
        with self.assertRaises(ValueError):
            self.check(bad)
        bad = deepcopy(self.ledger)
        bad["entries"][0]["fragments"].append(deepcopy(bad["entries"][0]["fragments"][0]))
        with self.assertRaises(ValueError):
            self.check(bad)

    def test_bad_classifications_and_unsupported_extra_fields(self):
        bad = deepcopy(self.ledger)
        bad["entries"][0]["fragments"][0]["classification"] = "historical_error_fixed"
        with self.assertRaises(ValueError):
            self.check(bad)
        bad = deepcopy(self.ledger)
        bad["entries"][0]["fragments"][0]["text_rewritten"] = True
        with self.assertRaises(ValueError):
            self.check(bad)
        bad = deepcopy(self.ledger)
        bad["entries"][0]["source_text_changed"] = True
        with self.assertRaises(ValueError):
            self.check(bad)
        bad = deepcopy(self.ledger)
        bad["entries"].append(deepcopy(bad["entries"][0]))
        with self.assertRaises(ValueError):
            self.check(bad)


if __name__ == "__main__":
    unittest.main()
