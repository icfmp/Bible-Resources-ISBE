"""Guardrails for conservative 1915 OCR article word-count triage.

Synthetic two-column pages ensure counting never silently includes a later
article or presents OCR concordance as historical print certification.
"""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts.audit_1915_article_ocr_word_counts import (
    assess, bbox_lines, compare_bbox, latin_tokens, unique_print_headings,
)


def page_xml(lines, width=600, height=800):
    fragments = []
    for text, x, y in lines:
        words = []
        for word in text.split():
            # The box centers classify each word strictly in its physical
            # left or right printed column.
            words.append(
                f'<word xMin="{x}" yMin="{y}" xMax="{x + 14}" yMax="{y + 8}">'
                f'{word}</word>'
            )
            x += 24
        fragments.append('<flow><block><line>' + "".join(words) + '</line></block></flow>')
    return (
        '<html xmlns="http://www.w3.org/1999/xhtml"><body><doc>'
        f'<page width="{width}" height="{height}">' + "".join(fragments) +
        '</page></doc></body></html>'
    )


def entries(*pairs):
    return [
        {"key": key, "article_xml_id": "id-" + str(i),
         "tei_latin_tokens": count}
        for i, (key, count) in enumerate(pairs)
    ]


def example():
    # Physical order is page-left top-to-bottom THEN right top-to-bottom,
    # not all y=70 left/right interwoven.
    return [
        ("AARON", 60, 70),
        ("one two three", 60, 88),
        ("AARON'S ROD", 60, 160),
        ("four five", 60, 178),
        ("ABASE", 350, 70),
        ("six seven eight", 350, 88),
        ("ABBOT", 350, 160),
        ("nine ten", 350, 178),
    ]


class OriginalPrintedWordCountTests(unittest.TestCase):
    def get_lines(self, raw, pages=1):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bbox.xhtml"
            path.write_text(raw, encoding="utf-8")
            return bbox_lines(path, pages)

    def test_count_columns_in_print_reading_order(self):
        lines = self.get_lines(page_xml(example()))
        self.assertEqual([line["column"] for line in lines[:4]], ["left"] * 4)
        self.assertEqual([line["column"] for line in lines[4:]], ["right"] * 4)
        a = entries(("AARON", 3), ("AARON'S ROD", 2), ("ABASE", 3), ("ABBOT", 2))
        accepted, stats = unique_print_headings(lines, a)
        self.assertEqual(len(accepted), 4)
        out, statuses = assess(lines, a, accepted)
        self.assertEqual([x["ocr_latin_tokens"] for x in out], [3, 2, 3, None])
        self.assertEqual(out[0]["status"], "ocr_count_near_source_candidate")
        self.assertEqual(out[2]["ocr_start_pdf_page"], 1)
        self.assertIsNone(out[3]["ocr_to_tei_ratio"])
        self.assertTrue(all(x["full_print_text_certified"] is False for x in out))

    def test_unknown_intermediate_article_forbids_count(self):
        lines = self.get_lines(page_xml(example()))
        a = entries(("AARON", 3), ("AARON'S ROD", 2),
                    ("AARONSON", 10), ("ABASE", 3), ("ABBOT", 2))
        accepted, _ = unique_print_headings(lines, a)
        out, _ = assess(lines, a, accepted)
        self.assertIsNone(out[1]["ocr_latin_tokens"])
        self.assertIsNone(out[2]["ocr_latin_tokens"])
        self.assertEqual(out[3]["ocr_latin_tokens"], 3)  # ABASE -> ABBOT remain consecutive

    def test_repeated_heading_does_not_make_false_boundary(self):
        src = example()
        src.append(("AARON", 80, 210))
        lines = self.get_lines(page_xml(src))
        a = entries(("AARON", 3), ("AARON'S ROD", 2), ("ABASE", 3), ("ABBOT", 2))
        accepted, diagnostic = unique_print_headings(lines, a)
        self.assertNotIn(0, accepted)
        self.assertGreater(diagnostic["ambiguous_multiple_heading_articles"], 0)
        out, _ = assess(lines, a, accepted)
        self.assertIsNone(out[0]["ocr_latin_tokens"])

    def test_bracketed_duplicate_heading_rescued_without_weakening_unique_titles(self):
        src = example()
        # A second "AARON'S ROD" appears after an independently anchored
        # ABBOT; only the first occurrence is between AARON and ABASE.
        src.append(("AARON'S ROD", 350, 240))
        lines = self.get_lines(page_xml(src))
        a = entries(("AARON", 3), ("AARON'S ROD", 2),
                    ("ABASE", 3), ("ABBOT", 2))
        accepted, stats = unique_print_headings(lines, a)
        self.assertEqual(stats["strict_ordered_unique_heading_articles"], 3)
        self.assertEqual(stats["bracketed_duplicate_heading_rescues"], 1)
        self.assertEqual(len(accepted), 4)
        out, _ = assess(lines, a, accepted)
        self.assertEqual(out[1]["ocr_latin_tokens"], 2)

    def test_multiple_duplicate_titles_inside_anchor_bracket_rejected(self):
        src = example()
        src.append(("AARON'S ROD", 60, 126))
        lines = self.get_lines(page_xml(src))
        a = entries(("AARON", 3), ("AARON'S ROD", 2),
                    ("ABASE", 3), ("ABBOT", 2))
        accepted, stats = unique_print_headings(lines, a)
        self.assertEqual(stats["bracketed_duplicate_heading_rescues"], 0)
        self.assertNotIn(1, accepted)

    def test_nonstandalone_duplicate_without_opening_proof_not_promoted(self):
        src = example()
        src[2] = ("AARON'S ROD: extra content", 60, 160)
        src.append(("AARON'S ROD", 350, 240))
        lines = self.get_lines(page_xml(src))
        a = entries(("AARON", 3), ("AARON'S ROD", 2),
                    ("ABASE", 3), ("ABBOT", 2))
        accepted, stats = unique_print_headings(lines, a)
        self.assertEqual(stats["bracketed_duplicate_heading_rescues"], 0)
        self.assertNotIn(1, accepted)

    def test_bracketed_duplicate_with_source_opening_proof_accepted(self):
        src = example()
        src[2] = ("AARON'S ROD: beginning", 60, 160)
        src[3] = ("uncommon ancient biography within three", 60, 178)
        src.append(("AARON'S ROD", 350, 240))
        lines = self.get_lines(page_xml(src))
        a = entries(("AARON", 3), ("AARON'S ROD", 2),
                    ("ABASE", 3), ("ABBOT", 2))
        a[1]["opening_latin_tokens"] = [
            "uncommon", "ancient", "biography", "within", "three", "other"
        ]
        accepted, stats = unique_print_headings(lines, a)
        self.assertEqual(stats["bracketed_duplicate_heading_rescues"], 1)
        self.assertIn(1, accepted)

    def test_weak_heading_requires_independent_nearby_source_prose(self):
        src = example()
        src[2] = ("Aaron's Rod", 60, 160)
        src[3] = ("uncommon ancient biography within three", 60, 178)
        lines = self.get_lines(page_xml(src))
        a = entries(("AARON", 3), ("AARON'S ROD", 5),
                    ("ABASE", 3), ("ABBOT", 2))
        a[1]["opening_latin_tokens"] = [
            "uncommon", "ancient", "biography", "within", "three", "other"
        ]
        accepted, stats = unique_print_headings(lines, a)
        self.assertEqual(stats["weak_bracketed_context_rescues"], 1)
        self.assertIn(1, accepted)
        self.assertEqual(stats["strict_ordered_unique_heading_articles"], 3)

    def test_weak_heading_without_source_opening_cannot_inflate_coverage(self):
        src = example()
        src[2] = ("Aaron's Rod", 60, 160)
        lines = self.get_lines(page_xml(src))
        a = entries(("AARON", 3), ("AARON'S ROD", 0),
                    ("ABASE", 3), ("ABBOT", 2))
        accepted, stats = unique_print_headings(lines, a)
        self.assertEqual(stats["weak_bracketed_context_rescues"], 0)
        self.assertNotIn(1, accepted)

    def test_weak_heading_without_two_strong_neighbors_is_not_rescued(self):
        src = example()
        src[0] = ("Aaron", 60, 70)
        src[1] = ("uncommon ancient biography within three", 60, 88)
        lines = self.get_lines(page_xml(src))
        a = entries(("AARON", 5), ("AARON'S ROD", 2),
                    ("ABASE", 3), ("ABBOT", 2))
        a[0]["opening_latin_tokens"] = [
            "uncommon", "ancient", "biography", "within", "three"
        ]
        accepted, stats = unique_print_headings(lines, a)
        self.assertEqual(stats["weak_bracketed_context_rescues"], 0)
        self.assertNotIn(0, accepted)

    def test_printed_body_crop_and_page_count_guard(self):
        lines = self.get_lines(page_xml([
            ("INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA", 60, 20),
            ("AARON", 60, 90),
            ("alpha", 60, 110),
            ("footer", 60, 770),
        ]))
        self.assertEqual([l["text"] for l in lines], ["AARON", "alpha"])
        with self.assertRaises(ValueError):
            self.get_lines(page_xml(example()), pages=2)

    def test_discrepancy_marks_candidate_not_certification(self):
        lines = self.get_lines(page_xml(example()))
        a = entries(("AARON", 100), ("AARON'S ROD", 2), ("ABASE", 3), ("ABBOT", 2))
        accepted, _ = unique_print_headings(lines, a)
        out, statuses = assess(lines, a, accepted)
        self.assertEqual(out[0]["ocr_latin_tokens"], 3)
        self.assertEqual(out[0]["status"], "ocr_count_diff_over_10pct_candidate")
        self.assertEqual(statuses["ocr_count_diff_over_10pct_candidate"], 1)

    def test_blank_digital_entry_flags_candidate(self):
        lines = self.get_lines(page_xml(example()))
        a = entries(("AARON", 0), ("AARON'S ROD", 2), ("ABASE", 3), ("ABBOT", 2))
        accepted, _ = unique_print_headings(lines, a)
        out, _ = assess(lines, a, accepted)
        self.assertEqual(out[0]["status"], "source_empty_print_ocr_nonempty")

    def test_comparison_fails_closed_on_pdf_digest(self):
        raw = page_xml(example())
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bbox.xhtml"
            path.write_text(raw)
            manifest = {"bibliographic_citation": "Synthetic print test",
                        "volumes": [{"volume": "1", "pdf_sha256": "a"*64, "pages": 1}]}
            with self.assertRaises(ValueError):
                compare_bbox(path, "b"*64, "c"*64, "1", manifest,
                             entries(("AARON", 3), ("AARON'S ROD", 2)))

    def test_normalization_is_not_nonlatin_text_certification(self):
        self.assertEqual(latin_tokens("שָׁלוֹם (shalom); Jésus – 42"),
                         ["shalom", "jesus", "42"])
        self.assertEqual(latin_tokens("Ἰησοῦς"), [])

if __name__ == "__main__":
    unittest.main()
