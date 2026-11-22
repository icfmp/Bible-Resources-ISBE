"""Unit tests for conservative OCR-only comparison of 1915 printed source."""
import unittest

from scripts.compare_1915_prose_ocr import concordance, latin_tokens


class PrintedProseOCRTests(unittest.TestCase):
    def test_matching_tokens_preserves_original_order(self):
        r = concordance("An ancestor of Ezra and Abishua.", "ABISSEI an ancestor of Ezra and Abishua.")
        self.assertEqual(r["ordered_token_recall"], 1)
        self.assertEqual(r["unmatched_candidate_tokens"], [])

    def test_order_mismatch_or_missing_words_not_silently_approved(self):
        r = concordance("Alpha beta gamma delta", "alpha gamma beta")
        self.assertLess(r["ordered_token_recall"], 1)
        self.assertIn("delta", r["unmatched_candidate_tokens"])

    def test_hebrew_is_not_incorrectly_ocr_certified(self):
        self.assertEqual(latin_tokens("שָׁלוֹם (shalom)"), ["shalom"])
        r = concordance("שָׁלוֹם (shalom)", "shalom")
        self.assertEqual(r["ordered_token_recall"], 1)
        # Deliberately does NOT mean the Hebrew glyphs were verified.
