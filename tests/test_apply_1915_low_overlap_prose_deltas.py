"""Fail-closed tests for the separate original-1915 prose delta layer."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from scripts.apply_1915_low_overlap_prose_deltas import (
    apply_operations, entries, validate_decisions,
)

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "workspace/reviews/1915-approved-low-overlap-prose-deltas-v1.json"
EVIDENCE = ROOT / "workspace/reviews/1915-low-overlap-prose-image-spotchecks-v2.json"
MANIFEST = ROOT / "sources/print/1915-volume-witnesses.json"
SOURCE = ROOT / "cleaned/en/ISBE.xml"
ID = "{http://www.w3.org/XML/1998/namespace}id"


class OriginalPrintProseDeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def decisions(self, spec=None):
        return validate_decisions(
            self.spec if spec is None else spec,
            self.evidence, self.manifest)

    def test_eight_individually_attested_edits(self):
        decisions = self.decisions()
        self.assertEqual(len(decisions), 8)
        self.assertEqual(len({r["source_unit_xml_id"] for r in decisions}), 8)
        self.assertFalse(self.spec["full_article_collation_certified"])
        self.assertFalse(self.spec["publication_permitted"])

    def test_exact_source_article_paragraph_and_slot_edits(self):
        root = ET.parse(SOURCE).getroot()
        original = entries(root)
        before = {key: ET.tostring(entry, encoding="utf-8")
                  for key, entry in original.items()}
        original_ids = [node.get(ID) for entry in original.values()
                        for node in entry.iter() if node.get(ID)]
        changed, report = apply_operations(root, self.decisions())
        self.assertEqual(len(changed), 8)
        self.assertEqual(len(report), 8)
        self.assertEqual(
            [node.get(ID) for entry in original.values()
             for node in entry.iter() if node.get(ID)], original_ids)
        for key, entry in original.items():
            if key in changed:
                self.assertNotEqual(ET.tostring(entry, encoding="utf-8"),
                                    before[key])
            else:
                self.assertEqual(ET.tostring(entry, encoding="utf-8"),
                                 before[key])
        self.assertTrue(all(item["reversible"] for item in report))

    def test_cannot_claim_publication_or_complete_collation(self):
        for field in ("publication_permitted", "full_article_collation_certified",
                      "independent_human_peer_review",
                      "source_faithful_canonical_modified"):
            bad = deepcopy(self.spec)
            bad[field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.decisions(bad)

    def test_reject_unreviewed_or_modified_print_evidence(self):
        edits = [
            ("approved_for_separate_1915_tei", False),
            ("source_unit_xml_id", "invented-unit"),
            ("source_article_xml_id", "invented-article"),
            ("original_pdf_sha256", "0" * 64),
            ("research_jpeg_sha256", "f" * 64),
            ("pdf_page_1_based", 777),
            ("printed_folio", 123),
            ("original_visible", "a fabricated digital reading"),
            ("corrected_visible", "a fabricated print reading"),
            ("review_classification", "invented_classification"),
        ]
        for field, value in edits:
            bad = deepcopy(self.spec)
            bad["decisions"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.decisions(bad)

    def test_no_duplicate_or_unapproved_delta(self):
        for change in ("duplicated", "removed"):
            bad = deepcopy(self.spec)
            if change == "duplicated":
                bad["decisions"][1] = deepcopy(bad["decisions"][0])
            else:
                bad["decisions"].pop()
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.decisions(bad)


if __name__ == "__main__":
    unittest.main()
