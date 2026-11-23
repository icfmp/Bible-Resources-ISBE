"""Print-vs-digital headword order: artificial historical-layout controls.

The actual 1915 scan has cases in which printed title order differs
from CrossWire's normalized key index. These synthetic examples prevent
a falsely gigantic article from absorbing an intervening printed entry.
"""
from copy import deepcopy
import unittest

from scripts.guard_1915_print_headword_interleaving import (
    guard_interleaved_headings, strong_intervening_heading_candidates,
)


def entry(key, i):
    return {"key": key, "article_xml_id": f"article-{i}",
            "tei_latin_tokens": 200}


def source_row(e, *, measured=True):
    return {
        "article_key": e["key"], "article_xml_id": e["article_xml_id"],
        "tei_latin_tokens": e["tei_latin_tokens"],
        "ocr_latin_tokens": 500 if measured else None,
        "ocr_start_pdf_page": 1 if measured else None,
        "ocr_end_pdf_page": 3 if measured else None,
        "ocr_to_tei_ratio": 2.5 if measured else None,
        "source_fourgram_recall": 0.7 if measured else None,
        "ocr_fourgram_precision": 0.3 if measured else None,
        "status": ("ocr_count_diff_over_10pct_candidate"
                   if measured else "unresolved_print_boundaries"),
    }


def fixture():
    # The **digital** source order puts Gospel before Epistles; the
    # 1915 print page sequence does the opposite.
    entries = [
        entry("JOHN THE BAPTIST", 0),
        entry("JOHN, GOSPEL OF", 1),
        entry("JOHN, THE EPISTLES OF", 2),
    ]
    lines = [
        {"page": 346, "text": "JOHN THE BAPTIST", "column": "right"},
        {"page": 347, "text": "Original printed biography and sources."},
        {"page": 349, "text": "JOHN, THE EPISTLES OF:"},
        {"page": 349, "text": "Original printed epistles prose."},
        {"page": 358, "text": "JOHN, GOSPEL OF:"},
    ]
    rows = [source_row(entries[0]), source_row(entries[1], measured=False),
            source_row(entries[2], measured=False)]
    return lines, entries, rows


class OriginalPrintOrderSafetyTests(unittest.TestCase):
    def test_independent_out_of_order_heading_withdraws_invalid_wordcount(self):
        lines, entries, rows = fixture()
        original_entries = deepcopy(entries)
        guarded, number = guard_interleaved_headings(
            lines, entries, {0: 0, 1: 4}, rows
        )
        self.assertEqual(number, 1)
        self.assertEqual(guarded[0]["tei_latin_tokens"], 200)
        self.assertIsNone(guarded[0]["ocr_latin_tokens"])
        self.assertIsNone(guarded[0]["source_fourgram_recall"])
        self.assertEqual(guarded[0]["status"], "unresolved_intervening_print_heading")
        self.assertEqual(guarded[0]["intervening_print_heading_candidates"], [{
            "source_key": "JOHN, THE EPISTLES OF",
            "source_article_xml_id": "article-2",
            "scan_pdf_page_1_based": 349,
            "image_verified": False,
        }])
        self.assertEqual(guarded[0]["withheld_ocr_span_start_scan_pdf_page_1_based"], 346)
        self.assertEqual(guarded[0]["withheld_ocr_span_next_heading_scan_pdf_page_1_based"], 358)
        self.assertEqual(entries, original_entries)

    def test_print_heading_with_comma_and_prose_still_blocks_wrong_interval(self):
        keys = [
            "PHARAOH HOPHRA", "PHARAOH'S DAUGHTER", "PHARAOH-NECOH"
        ]
        entries = [entry(key, i) for i, key in enumerate(keys)]
        lines = [
            {"page": 271, "text": "PHARAOH HOPHRA"},
            {"page": 271, "text": "Egyptian original printed paragraph"},
            {"page": 272, "text": "PHARAOH-NECOH, ne'koh: Egyptian royal dynasty"},
            {"page": 272, "text": "Other prose starts here."},
            {"page": 273, "text": "PHARAOH'S DAUGHTER:"},
        ]
        # Source index is out of the physical title sequence.
        got, n = guard_interleaved_headings(
            lines, entries, {0: 0, 1: 4},
            [source_row(entries[0]),
             source_row(entries[1], measured=False),
             source_row(entries[2], measured=False)]
        )
        self.assertEqual(n, 1)
        self.assertEqual(
            got[0]["intervening_print_heading_candidates"][0]["source_key"],
            "PHARAOH-NECOH",
        )

    def test_uppercase_prose_without_title_delimiter_is_not_heading(self):
        lines, entries, rows = fixture()
        lines[2]["text"] = "JOHN, THE EPISTLES OF this sentence is not a title."
        _, count = guard_interleaved_headings(
            lines, entries, {0: 0, 1: 4}, rows
        )
        self.assertEqual(count, 0)
        self.assertEqual(rows[0]["ocr_latin_tokens"], 500)

    def test_unproven_duplicate_title_mentions_cannot_block(self):
        lines, entries, rows = fixture()
        lines.insert(3, {"page": 350, "text": "JOHN, THE EPISTLES OF:"})
        _, count = guard_interleaved_headings(
            lines, entries, {0: 0, 1: 5}, rows
        )
        self.assertEqual(count, 0)

    def test_unrelated_short_uppercase_words_cannot_block(self):
        lines, entries, rows = fixture()
        entries[2]["key"] = "A"
        rows[2]["article_key"] = "A"
        lines[2]["text"] = "A"
        _, count = guard_interleaved_headings(
            lines, entries, {0: 0, 1: 4}, rows
        )
        self.assertEqual(count, 0)

    def test_article_identity_mismatch_fails_closed(self):
        lines, entries, rows = fixture()
        rows[0]["article_xml_id"] = "wrong"
        with self.assertRaises(ValueError):
            guard_interleaved_headings(
                lines, entries, {0: 0, 1: 4}, rows
            )

    def test_known_boundary_itself_does_not_count_as_intervening(self):
        lines, entries, rows = fixture()
        lines[2]["text"] = "An ordinary line, not the article title."
        candidates = strong_intervening_heading_candidates(lines, entries)
        self.assertTrue(any(x["source_key"] == "JOHN, GOSPEL OF" for x in candidates))
        _, n = guard_interleaved_headings(
            lines, entries, {0: 0, 1: 4}, rows
        )
        self.assertEqual(n, 0)


if __name__ == "__main__":
    unittest.main()
