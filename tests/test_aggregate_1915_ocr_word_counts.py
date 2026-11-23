"""Negative controls for full-corpus OCR word-count report aggregation."""
import copy
import unittest
from unittest.mock import patch

from scripts.aggregate_1915_ocr_word_counts import aggregate, approved_recovery_map, SOURCE_LOCK


def sample():
    volumes = []
    reports = []
    for n in range(1, 6):
        vol = str(n)
        sha = str(n) * 64
        volumes.append({"volume": vol, "pdf_sha256": sha, "pages": 700})
        rows = []
        for j in range(1876):  # Exactly 9,380 articles, all with distinct keys.
            key = f"EXAMPLE-{n}-{j:04d}"
            rows.append({
                "article_key": key,
                "article_xml_id": f"article-{n}-{j:04d}",
                "tei_latin_tokens": 100,
                "ocr_latin_tokens": None,
                "ocr_start_pdf_page": None,
                "ocr_end_pdf_page": None,
                "ocr_to_tei_ratio": None,
                "status": "unresolved_print_boundaries",
                "source_fourgram_recall": None,
                "ocr_fourgram_precision": None,
                "intervening_print_heading_candidates": [],
                "withheld_ocr_span_start_scan_pdf_page_1_based": None,
                "withheld_ocr_span_next_heading_scan_pdf_page_1_based": None,
                "visually_verified": False,
                "full_print_text_certified": False,
            })
        # Keep one testable article in each scan and ensure the rest are
        # explicitly unresolved, NOT silently accepted.
        rows[0].update(
            ocr_latin_tokens=104, ocr_start_pdf_page=1,
            ocr_end_pdf_page=1, ocr_to_tei_ratio=1.04,
            status="ocr_count_near_source_candidate",
            source_fourgram_recall=0.8, ocr_fourgram_precision=0.8,
        )
        reports.append({
            "schema_version": 7, "volume": vol, "print_pdf_sha256": sha,
            "canonical_tei_sha256": SOURCE_LOCK,
            "pdf_pages": 700, "publication_permitted": False,
            "independent_print_order_does_not_imply_digital_source_order": True,
            "ocr_intervals_withdrawn_due_to_independent_intervening_print_headwords": 0,
            "ocr_not_original_print_certification": True,
            "articles_in_volume": len(rows),
            "article_count_sum": len(rows),
            "status_counts": {
                "ocr_count_near_source_candidate": 1,
                "unresolved_print_boundaries": 1875,
            },
            "heading_diagnostics": {"ordered_unique_heading_articles": 2},
            "content_candidate_diagnostic_count": 0,
            "content_candidate_diagnostics": [],
            "entries": rows,
        })
    manifest = {
        "canonical_tei_sha256": SOURCE_LOCK,
        "bibliographic_citation": "Synthetic source",
        "volumes": volumes,
    }
    return reports, manifest


def install_synthetic_candidate(report, *, low_recall=0.1):
    """Build exact allowlisted digest-only evidence for an original-source row.

    Synthetic source keys don't reference any historical article prose.
    """
    row, following = report["entries"][:2]
    row["source_fourgram_recall"] = low_recall
    from scripts.audit_1915_article_ocr_word_counts import latin_tokens
    case = {
        "source_key": row["article_key"],
        "article_xml_id": row["article_xml_id"],
        "review_queue": "similar_length_low_phrase_overlap",
        "source_latin_token_count": row["tei_latin_tokens"],
        "candidate_ocr_latin_token_count": row["ocr_latin_tokens"],
        "source_tokens_sha256": "a"*64,
        "ocr_candidate_tokens_sha256": "b"*64,
        "initial_heading_scan_pdf_page_1_based": 1,
        "next_known_heading_scan_pdf_page_1_based": 1,
        "next_source_article_key": following["article_key"],
        "span_pdf_page_count_inclusive": 1,
        "ocr_word_count_by_scan_page": [{
            "scan_pdf_page_1_based": 1,
            "ocr_tokens_in_page_segment": (
                row["ocr_latin_tokens"] + len(latin_tokens(row["article_key"]))
            ),
        }],
        "tei_token_unigram_recall": 0.4,
        "tei_token_bigram_recall": 0.2,
        "tei_token_trigram_recall": 0.15,
        "tei_token_fourgram_recall": low_recall,
        "unique_fourgram_overlap_footprint": None,
        "candidate_ocr_span_not_an_original_print_certification": True,
        "print_page_images_directly_compared": False,
        "textual_correction_authorized": False,
        "publication_permitted": False,
    }
    report["content_candidate_diagnostics"] = [case]
    report["content_candidate_diagnostic_count"] = 1
    return case


class OCRAggregateSafetyTests(unittest.TestCase):
    def run_synthetic(self, reports, manifest):
        # Separate validation of physical alphabetic assignment remains in
        # the integration pipeline; the synthetic keys are deliberately fake.
        with patch("scripts.aggregate_1915_ocr_word_counts.expected_volume",
                   side_effect=lambda key: key.split("-")[1]):
            return aggregate(reports, manifest)

    def test_source_empty_restoration_witness_matches_all_original_empty_keys(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1] / "workspace" / "reviews"
        approved = json.loads((root / "1915-second-pass-visual-approval-v1.json").read_text(encoding="utf-8"))
        empty = json.loads((root / "empty-article-recovery-ledger.json").read_text(encoding="utf-8"))
        result = approved_recovery_map(approved, empty)
        self.assertEqual(len(result), 31)
        self.assertEqual(result["ABISSEI"], "prose")

    def test_source_empty_restoration_provenance_guard(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1] / "workspace" / "reviews"
        approved = json.loads((root / "1915-second-pass-visual-approval-v1.json").read_text(encoding="utf-8"))
        empty = json.loads((root / "empty-article-recovery-ledger.json").read_text(encoding="utf-8"))
        approved["published"] = True
        with self.assertRaises(ValueError):
            approved_recovery_map(approved, empty)
        approved["published"] = False
        approved["records"][0]["approved_for_separate_editorial_tei"] = False
        with self.assertRaises(ValueError):
            approved_recovery_map(approved, empty)

    def test_full_corpus_coverage_only_five_real_sources(self):
        reports, manifest = sample()
        result = self.run_synthetic(reports, manifest)
        self.assertEqual(result["full_corpus_source_articles"], 9380)
        self.assertEqual(result["count_comparable_articles"], 5)
        self.assertEqual(result["unresolved_ocr_article_boundaries"], 9375)
        self.assertTrue(result["ocr_only_not_print_certified"])
        self.assertFalse(result["publication_permitted"])

    def test_similar_counts_with_low_phrase_overlap_are_flagged_not_certified(self):
        reports, manifest = sample()
        install_synthetic_candidate(reports[0])
        result = self.run_synthetic(reports, manifest)
        self.assertEqual(result["near_word_count_but_low_source_phrase_overlap"], 1)
        self.assertFalse(result["top_30_near_word_count_low_overlap"][0]["source_print_certified"])

    def test_all_queued_anomalies_require_evidence_even_if_count_summary_succeeds(self):
        reports, manifest = sample()
        reports[0]["entries"][0]["source_fourgram_recall"] = 0.1
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)

    def test_prohibited_original_ocr_prose_field_is_rejected(self):
        reports, manifest = sample()
        case = install_synthetic_candidate(reports[0])
        case["ocr_article_text"] = "Unapproved prose leakage"
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)

    def test_unsupported_print_image_approval_is_rejected(self):
        reports, manifest = sample()
        case = install_synthetic_candidate(reports[0])
        case["print_page_images_directly_compared"] = True
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)

    def test_wrong_source_next_heading_or_word_totals_are_rejected(self):
        reports, manifest = sample()
        case = install_synthetic_candidate(reports[0])
        case["next_source_article_key"] = "INVENTED"
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)
        case["next_source_article_key"] = reports[0]["entries"][1]["article_key"]
        case["ocr_word_count_by_scan_page"][0]["ocr_tokens_in_page_segment"] += 1
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)

    def test_missing_or_impossible_lexical_evidence_is_rejected(self):
        reports, manifest = sample()
        reports[0]["entries"][0]["source_fourgram_recall"] = None
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)
        reports[0]["entries"][0]["source_fourgram_recall"] = 1.5
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)

    def test_substantive_differences_are_ranked_separately_from_short_entries(self):
        reports, manifest = sample()
        source = reports[0]["entries"][0]
        source.update(
            tei_latin_tokens=300, ocr_latin_tokens=50,
            ocr_to_tei_ratio=0.1667, status="ocr_count_diff_over_10pct_candidate",
        )
        reports[0]["status_counts"] = {
            "ocr_count_diff_over_10pct_candidate": 1,
            "unresolved_print_boundaries": 1875,
        }
        result = self.run_synthetic(reports, manifest)
        self.assertEqual(result["difference_direction_counts"]["tei_longer"], 1)
        self.assertEqual(result["discrepancies_by_source_size"]["02_100_to_499_source_words"], 1)
        self.assertEqual(result["substantive_source_difference_candidates_count"], 1)
        self.assertEqual(result["top_50_substantive_source_abs_differences"][0][
            "absolute_latin_token_difference"], 250)
        self.assertFalse(result["top_50_substantive_source_abs_differences"][0]["source_print_certified"])

    def test_independent_print_headword_withdrawal_is_preserved_and_not_counted(self):
        reports, manifest = sample()
        row = reports[0]["entries"][0]
        row.update(
            ocr_latin_tokens=None, ocr_start_pdf_page=None,
            ocr_end_pdf_page=None, ocr_to_tei_ratio=None,
            source_fourgram_recall=None, ocr_fourgram_precision=None,
            status="unresolved_intervening_print_heading",
            withheld_ocr_span_start_scan_pdf_page_1_based=1,
            withheld_ocr_span_next_heading_scan_pdf_page_1_based=2,
            intervening_print_heading_candidates=[{
                "source_key": reports[0]["entries"][1]["article_key"],
                "source_article_xml_id": reports[0]["entries"][1]["article_xml_id"],
                "scan_pdf_page_1_based": 1,
                "image_verified": False,
            }]
        )
        reports[0]["status_counts"] = {
            "unresolved_intervening_print_heading": 1,
            "unresolved_print_boundaries": 1875,
        }
        reports[0][
            "ocr_intervals_withdrawn_due_to_independent_intervening_print_headwords"
        ] = 1
        result = self.run_synthetic(reports, manifest)
        self.assertEqual(result["count_comparable_articles"], 4)
        self.assertEqual(result["unresolved_ocr_article_boundaries"], 9376)
        self.assertEqual(result["withheld_due_to_detected_intervening_print_titles"], 1)
        self.assertEqual(result["possible_print_order_interleavings"][0][
            "candidate_independent_print_titles"][0]["image_verified"], False)

    def test_illegal_visual_proof_of_interleaving_rejected(self):
        reports, manifest = sample()
        row = reports[0]["entries"][0]
        row.update(
            ocr_latin_tokens=None, ocr_start_pdf_page=None,
            ocr_end_pdf_page=None, ocr_to_tei_ratio=None,
            source_fourgram_recall=None, ocr_fourgram_precision=None,
            status="unresolved_intervening_print_heading",
            withheld_ocr_span_start_scan_pdf_page_1_based=1,
            withheld_ocr_span_next_heading_scan_pdf_page_1_based=2,
            intervening_print_heading_candidates=[{
                "source_key": reports[0]["entries"][1]["article_key"],
                "source_article_xml_id": reports[0]["entries"][1]["article_xml_id"],
                "scan_pdf_page_1_based": 1,
                "image_verified": True,
            }]
        )
        reports[0]["status_counts"] = {
            "unresolved_intervening_print_heading": 1,
            "unresolved_print_boundaries": 1875,
        }
        reports[0][
            "ocr_intervals_withdrawn_due_to_independent_intervening_print_headwords"
        ] = 1
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)

    def test_missing_one_volume_is_rejected(self):
        reports, manifest = sample()
        with self.assertRaises(ValueError):
            self.run_synthetic(reports[:-1], manifest)

    def test_invented_ocr_measurement_is_rejected(self):
        reports, manifest = sample()
        reports[0]["entries"][1]["ocr_latin_tokens"] = 50
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)

    def test_unsupported_print_certification_is_rejected(self):
        reports, manifest = sample()
        reports[0]["entries"][0]["full_print_text_certified"] = True
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)

    def test_pdf_source_sha_mismatch_is_rejected(self):
        reports, manifest = sample()
        reports[1]["print_pdf_sha256"] = "x" * 64
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)

    def test_ocr_word_count_cannot_leak_into_unresolved_article(self):
        reports, manifest = sample()
        reports[2]["entries"][1]["ocr_start_pdf_page"] = 2
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)

    def test_duplicate_article_is_rejected(self):
        reports, manifest = sample()
        reports[1]["entries"][1]["article_xml_id"] = reports[0]["entries"][1]["article_xml_id"]
        with self.assertRaises(ValueError):
            self.run_synthetic(reports, manifest)


if __name__ == "__main__":
    unittest.main()
