"""Exercise historical printed-page provenance checks for all 20 prose candidates."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.audit_1915_prose_evidence import audit

ROOT = Path(__file__).resolve().parents[1]


class ProseEvidenceAuditTests(unittest.TestCase):
    def test_20_prose_records_are_page_bound_and_not_editorially_certified(self):
        report = audit(ROOT)
        self.assertEqual(report["prose_articles"], 20)
        self.assertEqual(report["fully_certified_articles"], 0)
        self.assertFalse(report["rights_cleared"])
        records = report["records"]
        self.assertEqual(len({r["source_key"] for r in records}), 20)
        self.assertEqual(len({r["source_paragraph_xml_id"] for r in records}), 20)
        for row in records:
            with self.subTest(key=row["source_key"]):
                self.assertEqual(len(row["original_pdf_sha256"]), 64)
                self.assertEqual(len(row["rendered_page_jpeg_sha256"]), 64)
                self.assertEqual(len(row["candidate_text_sha256"]), 64)
                self.assertGreater(row["pdf_page_1_based"], 0)
                self.assertFalse(row["editorial_approval"])
                self.assertEqual(row["review_status"],
                                 "primary_print_page_visually_inspected__full_text_not_collated")
        self.assertEqual({r["printed_volume"] for r in records}, set("12345"))
        self.assertEqual(
            {(r["printed_volume"], r["printed_folio"]) for r in records
             if r["source_key"] in ("THOMEI", "THOCANUS")},
            {("5", 2973)},
        )

    def test_rejects_unearned_certification_or_page_sha_drift(self):
        original = json.loads((ROOT / "workspace/reviews/print-prose-candidate-v1.json")
                              .read_text(encoding="utf-8"))
        pages = json.loads((ROOT / "workspace/reviews/1915-visual-page-collation-v1.json")
                           .read_text(encoding="utf-8"))
        from scripts import audit_1915_prose_evidence as module
        actual_load = module.load

        tampered = copy.deepcopy(original)
        tampered["records"][0]["print_text_fully_certified"] = True

        def fake_load(path):
            if path.name == "print-prose-candidate-v1.json":
                return tampered
            return actual_load(path)

        with patch.object(module, "load", side_effect=fake_load):
            with self.assertRaisesRegex(ValueError, "Unexpected promotion"):
                audit(ROOT)

        tampered_pages = copy.deepcopy(pages)
        next(row for row in tampered_pages["records"] if row["source_key"] == "ABISSEI")["original_pdf_sha256"] = "0" * 64

        def fake_pages(path):
            if path.name == "1915-visual-page-collation-v1.json":
                return tampered_pages
            return actual_load(path)

        with patch.object(module, "load", side_effect=fake_pages):
            with self.assertRaisesRegex(ValueError, "PDF SHA mismatch"):
                audit(ROOT)


if __name__ == "__main__":
    unittest.main()
