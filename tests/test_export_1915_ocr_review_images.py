"""Tests for source-locked, ephemeral 1915 facsimile review-image selection."""
import copy
import tempfile
from pathlib import Path
import json
import unittest

from scripts.export_1915_ocr_review_images import (
    export_research_images, selected_pages
)
from scripts.audit_1915_article_ocr_word_counts import LOCK


def scan_case(key, start, stop, *, category="similar_length_low_phrase_overlap",
              matched=None):
    return {
        "source_key": key,
        "article_xml_id": "id-" + key,
        "review_queue": category,
        "candidate_ocr_span_not_an_original_print_certification": True,
        "print_page_images_directly_compared": False,
        "publication_permitted": False,
        "initial_heading_scan_pdf_page_1_based": start,
        "next_known_heading_scan_pdf_page_1_based": stop,
        "unique_fourgram_overlap_footprint": matched,
    }


def witness():
    return {"volume": "3", "pdf_sha256": "a" * 64, "pages": 756}


def report(cases):
    return {
        "schema_version": 5,
        "canonical_tei_sha256": LOCK,
        "print_pdf_sha256": "a" * 64,
        "volume": "3",
        "ocr_not_original_print_certification": True,
        "publication_permitted": False,
        "content_candidate_diagnostics": cases,
        "content_candidate_diagnostic_count": len(cases),
    }


class ResearchPDFPageSelectionTests(unittest.TestCase):
    def test_single_page_near_size_case_renders_only_its_source_page(self):
        selected = selected_pages(report([
            scan_case("MEADOW", 657, 657)
        ]), witness())
        self.assertEqual(list(selected), [657])
        self.assertEqual(selected[657][0]["source_key"], "MEADOW")
        self.assertTrue(selected[657][0]["still_requires_human_image_collation"])

    def test_long_case_renders_heading_both_unique_boundaries_and_next_heading(self):
        window = {
            "window_first_scan_pdf_page_1_based": 347,
            "window_last_scan_pdf_page_1_based": 349,
        }
        selected = selected_pages(report([
            scan_case("JOHN THE BAPTIST", 346, 358,
                      category="long_ocr_span_source_phrases_present",
                      matched=window),
        ]), witness())
        self.assertEqual(list(selected), [346, 347, 349, 358])
        self.assertEqual(selected[358][0]["evidence_role"], "following_heading")

    def test_shared_page_rendered_once_with_both_research_cases(self):
        selected = selected_pages(report([
            scan_case("ONE", 180, 181),
            scan_case("TWO", 180, 181),
        ]), witness())
        self.assertEqual(len(selected), 1)
        self.assertEqual(len(selected[180]), 2)

    def test_forged_visual_certification_is_rejected(self):
        r = report([scan_case("MEADOW", 657, 657)])
        r["content_candidate_diagnostics"][0]["print_page_images_directly_compared"] = True
        with self.assertRaises(ValueError):
            selected_pages(r, witness())

    def test_scan_page_outside_actual_original_volume_is_rejected(self):
        with self.assertRaises(ValueError):
            selected_pages(report([scan_case("MEADOW", 757, 760)]), witness())

    def test_page_window_outside_anchored_article_is_rejected(self):
        r = report([scan_case(
            "JOHN THE BAPTIST", 346, 358,
            category="long_ocr_span_source_phrases_present",
            matched={
                "window_first_scan_pdf_page_1_based": 344,
                "window_last_scan_pdf_page_1_based": 349,
            }
        )])
        with self.assertRaises(ValueError):
            selected_pages(r, witness())

    def test_duplicate_articles_and_large_page_requests_are_rejected(self):
        r = report([
            scan_case("MEADOW", 657, 657), scan_case("MEADOW", 657, 657)
        ])
        with self.assertRaises(ValueError):
            selected_pages(r, witness())
        r = report([scan_case(str(n), n, n) for n in range(1, 10)])
        with self.assertRaises(ValueError):
            selected_pages(r, witness(), limit=8)

    def test_source_pdf_digest_rejected_before_subprocess_rendering(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            original = path / "fake.pdf"
            original.write_bytes(b"%PDF-only test, not historical original")
            evidence = path / "report.json"
            evidence.write_text(json.dumps(report([scan_case("MEADOW", 657, 657)])))
            manifest = path / "manifest.json"
            manifest.write_text(json.dumps({
                "canonical_tei_sha256": LOCK,
                "volumes": [witness()],
            }))
            with self.assertRaises(ValueError):
                export_research_images(original, manifest, evidence, path / "output")


if __name__ == "__main__":
    unittest.main()
