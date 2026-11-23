"""Regressions: printed 1915 abbreviations vs expanded CrossWire source.

Research-only comparison; no original edition is rewritten or certified.
"""
import unittest

from scripts.diagnose_1915_print_abbreviation_equivalence import (
    EXPLICIT_SOURCE_TO_PRINT,
    research_abbreviation_effect,
    research_fold_digital_expansions,
)
from scripts.diagnose_1915_ocr_candidate_spans import multiset_recall


class PrintedAbbreviationDiagnosticsTests(unittest.TestCase):
    def test_av_ot_nt_equivalences_require_actual_printed_ocr_tokens(self):
        original = ("the king james version of the old testament was used "
                    "in the new testament").split()
        ocr = "av of the ot was used in the nt".split()
        frozen = original.copy()
        revised, counts = research_fold_digital_expansions(original, ocr)
        self.assertEqual(original, frozen)
        self.assertEqual(revised, ocr)
        self.assertEqual(counts, {"av": 1, "nt": 1, "ot": 1})
        raw = multiset_recall(original, ocr, 4)
        evidence = research_abbreviation_effect(original, ocr, raw, multiset_recall)
        self.assertEqual(evidence["raw_source_fourgram_recall"], raw)
        self.assertEqual(evidence["derived_abbreviation_equivalence_fourgram_recall"], 1)
        self.assertFalse(evidence["publication_permitted"])
        self.assertTrue(evidence["original_tei_and_ocr_text_unchanged"])
        self.assertTrue(evidence["printed_abbreviation_matches_are_not_image_certifications"])

    def test_no_printed_abbreviation_no_derived_substitution(self):
        source = "the revised version british and american is used in english".split()
        printed = "the revised version british and american is used in english".split()
        derived, changed = research_fold_digital_expansions(source, printed)
        self.assertEqual(source, derived)
        self.assertEqual(changed, {})
        raw = multiset_recall(source, printed, 4)
        effect = research_abbreviation_effect(source, printed, raw, multiset_recall)
        self.assertEqual(effect["derived_minus_raw_fourgram_recall"], 0)

    def test_printed_oe_heb_gr_and_revised_version_margin(self):
        source = ("old english old testament hebrew greek "
                  "the revised version british and american margin").split()
        ocr = "oe ot heb gr rvm".split()
        derived, changes = research_fold_digital_expansions(source, ocr)
        self.assertEqual(derived, ocr)
        self.assertEqual(changes, {
            "gr": 1, "heb": 1, "oe": 1, "ot": 1, "rvm": 1
        })

    def test_partial_source_phrases_are_never_guessed(self):
        source = "the king james old version was used here".split()
        ocr = "av was used here".split()
        out, changes = research_fold_digital_expansions(source, ocr)
        self.assertEqual(out, source)
        self.assertEqual(changes, {})

    def test_normalization_is_diagnostic_not_authoritative_text_edit(self):
        source = "the revised version british and american the king james version".split()
        original = source.copy()
        ocr = "rv av".split()
        derived, changes = research_fold_digital_expansions(source, ocr)
        self.assertEqual(derived, ["rv", "av"])
        self.assertEqual(changes, {"av": 1, "rv": 1})
        self.assertEqual(source, original)

    def test_short_or_unmatched_sources_cannot_gain_unearned_certification(self):
        source = "old testament".split()
        printed = "ot".split()
        self.assertIsNone(
            research_abbreviation_effect(source, printed, None, multiset_recall)
        )
        self.assertLessEqual(
            len({abbrev for _, abbrev in EXPLICIT_SOURCE_TO_PRINT}), 9
        )


if __name__ == "__main__":
    unittest.main()
