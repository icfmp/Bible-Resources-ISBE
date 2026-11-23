"""Adversarial synthetic tests for selected 1915 OCR span evidence.

No original facsimile or historical prose is introduced into a unit test.
Candidate scores can guide image review; none can sign off print fidelity.
"""
import json
import unittest

from scripts.audit_1915_article_ocr_word_counts import latin_tokens
from scripts.diagnose_1915_ocr_candidate_spans import (
    diagnostic_category, dense_unique_fourgram_window,
    diagnose_candidates, multiset_recall, shatokens,
)


def specimen(source, ocr, initial_status):
    lines = [
        {"page": 1, "text": "ARROW", "column": "left", "y": 120},
        {"page": 1, "text": " ".join(ocr), "column": "left", "y": 140},
        {"page": 2, "text": "BANNER", "column": "left", "y": 100},
    ]
    entries = [
        {
            "key": "ARROW", "article_xml_id": "article-a",
            "tei_latin_tokens": len(source), "source_latin_tokens": source,
        },
        {
            "key": "BANNER", "article_xml_id": "article-b",
            "tei_latin_tokens": 0, "source_latin_tokens": [],
        }
    ]
    rows = [
        {
            "article_key": "ARROW", "article_xml_id": "article-a",
            "tei_latin_tokens": len(source),
            "ocr_latin_tokens": len(ocr),
            "source_fourgram_recall": multiset_recall(source, ocr, 4),
            "status": initial_status,
        },
        {
            "article_key": "BANNER", "article_xml_id": "article-b",
            "tei_latin_tokens": 0, "ocr_latin_tokens": None,
            "source_fourgram_recall": None,
            "status": "unresolved_print_boundaries",
        },
    ]
    return lines, entries, rows


class OCRContentEvidenceTests(unittest.TestCase):
    def test_similar_count_but_unrelated_100_word_spans_retain_ocr_only_status(self):
        source = [f"term{i:03d}" for i in range(100)]
        ocr = [f"other{i:03d}" for i in range(100)]
        lines, entries, rows = specimen(source, ocr, "ocr_count_near_source_candidate")
        diagnostics = diagnose_candidates(lines, entries, {0: 0, 1: 2}, rows, latin_tokens)
        self.assertEqual(len(diagnostics), 1)
        record = diagnostics[0]
        self.assertEqual(record["review_queue"], "similar_length_low_phrase_overlap")
        self.assertEqual(record["tei_token_unigram_recall"], 0)
        self.assertEqual(record["tei_token_fourgram_recall"], 0)
        shorthand = record["print_abbreviation_equivalence_research"]
        self.assertIsNotNone(shorthand)
        self.assertEqual(shorthand["derived_minus_raw_fourgram_recall"], 0)
        self.assertEqual(shorthand["raw_source_fourgram_recall"], 0)
        self.assertTrue(shorthand["original_tei_and_ocr_text_unchanged"])
        self.assertIsNone(record["unique_fourgram_overlap_footprint"])
        self.assertEqual(record["ocr_word_count_by_scan_page"], [
            {"scan_pdf_page_1_based": 1, "ocr_tokens_in_page_segment": 101}
        ])
        self.assertFalse(record["print_page_images_directly_compared"])
        self.assertFalse(record["textual_correction_authorized"])
        self.assertFalse(record["publication_permitted"])
        dumped = json.dumps(record)
        self.assertNotIn("term000", dumped)
        self.assertNotIn("other000", dumped)

    def test_ocr_excess_containing_source_prose_localizes_to_internal_window(self):
        source = [f"distinct{i:03d}" for i in range(100)]
        ocr = ([f"before{i:03d}" for i in range(50)] + source
               + [f"after{i:03d}" for i in range(100)])
        lines, entries, rows = specimen(source, ocr, "ocr_count_diff_over_10pct_candidate")
        diag, = diagnose_candidates(lines, entries, {0: 0, 1: 2}, rows, latin_tokens)
        self.assertEqual(diag["review_queue"], "long_ocr_span_source_phrases_present")
        self.assertEqual(diag["tei_token_unigram_recall"], 1)
        self.assertEqual(diag["tei_token_fourgram_recall"], 1)
        self.assertIsNone(diag["print_abbreviation_equivalence_research"])
        dense = diag["unique_fourgram_overlap_footprint"]
        self.assertIsNotNone(dense)
        self.assertEqual(dense["matched_unique_fourgrams"], 97)
        self.assertLess(dense["window_fraction_of_full_ocr_span"], 0.45)
        self.assertGreater(dense["window_first_ocr_token_offset"], 0)
        self.assertFalse(dense["source_print_fidelity_certified"])
        self.assertEqual(diag["source_tokens_sha256"], shatokens(source))
        self.assertEqual(diag["ocr_candidate_tokens_sha256"], shatokens(ocr))

    def test_short_source_never_flagged_as_big_content_discrepancy(self):
        self.assertIsNone(diagnostic_category({
            "tei_latin_tokens": 20, "ocr_latin_tokens": 300,
            "source_fourgram_recall": 0.9,
            "status": "ocr_count_diff_over_10pct_candidate",
        }))

    def test_long_candidate_without_source_overlap_is_not_confidently_localized(self):
        src = [f"word{i:03d}" for i in range(120)]
        observed = [f"other{i:03d}" for i in range(300)]
        pages = [1] * len(observed)
        self.assertIsNone(dense_unique_fourgram_window(src, observed, pages))

    def test_repeated_common_fourgrams_do_not_prove_localization(self):
        src = ["same"] * 120
        observed = ["same"] * 150
        pages = [1] * len(observed)
        self.assertIsNone(dense_unique_fourgram_window(src, observed, pages))

    def test_without_known_adjacent_headings_diagnostics_fail_closed(self):
        source = [f"term{i:03d}" for i in range(100)]
        ocr = [f"other{i:03d}" for i in range(100)]
        lines, entries, rows = specimen(source, ocr, "ocr_count_near_source_candidate")
        with self.assertRaises(ValueError):
            diagnose_candidates(lines, entries, {0: 0}, rows, latin_tokens)

    def test_source_id_or_lexical_baseline_drift_is_rejected(self):
        source = [f"term{i:03d}" for i in range(100)]
        ocr = [f"other{i:03d}" for i in range(100)]
        lines, entries, rows = specimen(source, ocr, "ocr_count_near_source_candidate")
        rows[0]["source_fourgram_recall"] = 0.2
        # It remains in the near-count/low-phrase-overlap queue,
        # so exact score parity must be checked, not faked.
        with self.assertRaises(ValueError):
            diagnose_candidates(lines, entries, {0: 0, 1: 2}, rows, latin_tokens)
        rows[0]["source_fourgram_recall"] = 0
        rows[0]["article_xml_id"] = "other"
        with self.assertRaises(ValueError):
            diagnose_candidates(lines, entries, {0: 0, 1: 2}, rows, latin_tokens)

    def test_gram_multiset_does_not_double_count_repeated_phrases(self):
        source = ["a", "b", "c", "d", "a", "b", "c", "d"]
        observed = ["a", "b", "c", "d"]
        self.assertEqual(multiset_recall(source, observed, 4), 0.2)


if __name__ == "__main__":
    unittest.main()
