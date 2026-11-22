"""Offline controls for locating 1915 printed headword candidates."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.research_1915_print_pages import (
    analyze_pdf, candidate_heading, find_headings, normalize,
)

ROOT = Path(__file__).resolve().parents[1]


class PrintHeadingResearchTests(unittest.TestCase):
    def test_punctuation_and_composite_titles(self):
        self.assertEqual(normalize("ASTARTE; ASTORETH"), "ASTARTE ASTORETH")
        self.assertEqual(candidate_heading("ASTARTE; ASTORETH, a title", "ASTARTE; ASTORETH"), 3)
        self.assertEqual(candidate_heading("AMNON, am'-non", "AMNON"), 3)
        self.assertEqual(candidate_heading("AMNON", "AMNON"), 4)

    def test_no_prose_substring_or_running_header_claim(self):
        self.assertEqual(candidate_heading("The eldest son, Amnon, was ...", "AMNON"), 0)
        self.assertEqual(candidate_heading("AMNONITES", "AMNON"), 0)
        self.assertEqual(candidate_heading("PRONUNCIATIONS", "PROSTRATION"), 0)
        pages = [
            "The eldest son, Amnon, was ...\nAMNON, am'-non\nThe article begins.",
            "ASTARTE; ASTORETH, as-tar-te\nSee ASHTAROTH.",
        ]
        result = find_headings(pages, ["AMNON", "ASTARTE; ASTORETH"])
        self.assertEqual(result["AMNON"][0]["pdf_page_1_based"], 1)
        self.assertFalse(result["AMNON"][0]["page_image_inspected"])
        self.assertEqual(result["ASTARTE; ASTORETH"][0]["pdf_page_1_based"], 2)

    def test_report_is_source_locked_and_does_not_assert_visual_verification(self):
        page = "THE INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA\n1915\nAMNON, am'-non\nThe text"
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "source.pdf"
            pdf.write_bytes(b"%PDF-1.4\nfake-test-pdf")
            fake = subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout=page + "\f" + ("another ordinary page\f" * 100),
                stderr="",
            )
            with patch("scripts.research_1915_print_pages.subprocess.run", return_value=fake):
                result = analyze_pdf(
                    pdf, ROOT / "workspace/reviews/empty-article-recovery-ledger.json", "I"
                )
            self.assertEqual(result["total_checked_keys"], 31)
            self.assertFalse(result["claims_exact_print_verification"])
            self.assertTrue(next(
                row for row in result["cases"] if row["source_key"] == "AMNON"
            )["candidates"])


if __name__ == "__main__":
    unittest.main()
