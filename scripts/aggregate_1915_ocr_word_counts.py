#!/usr/bin/env python3
"""Aggregate five 1915 volume OCR count candidates, not print certifications."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts.research_1915_print_pages import expected_volume
from scripts.diagnose_1915_ocr_candidate_spans import diagnostic_category
from scripts.diagnose_1915_print_abbreviation_equivalence import EXPLICIT_SOURCE_TO_PRINT
from scripts.audit_1915_article_ocr_word_counts import latin_tokens

SOURCE_LOCK = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
VOLUMES = {"1", "2", "3", "4", "5"}
STATUSES = {
    "unresolved_print_boundaries", "unresolved_intervening_print_heading",
    "source_empty_print_ocr_nonempty",
    "both_zero_candidate", "ocr_count_near_source_candidate",
    "ocr_count_diff_over_10pct_candidate",
}


def approved_recovery_map(recovery, source_empty_ledger):
    """Cross-check known historical restorations without using them as OCR proof."""
    if (recovery.get("canonical_source_sha256") != SOURCE_LOCK
            or recovery.get("source_empty_entries_recovered") != 31
            or recovery.get("legal_redistribution_clearance") is not False
            or recovery.get("published") is not False
            or source_empty_ledger.get("baseline_canonical_tei_sha256") != SOURCE_LOCK):
        raise ValueError("Unexpected historical source-empty restoration provenance")
    source_keys = [r["source_key"] for r in source_empty_ledger["cases"]]
    rows = recovery.get("records", [])
    result = {}
    for row in rows:
        key = row.get("source_key")
        if (not key or key in result or row.get("kind") not in {"redirect", "prose"}
                or row.get("approved_for_separate_editorial_tei") is not True):
            raise ValueError("Invalid approved historical restoration record")
        result[key] = row["kind"]
    if (len(source_keys) != 31 or len(set(source_keys)) != 31
            or len(rows) != 31 or set(source_keys) != set(result)):
        raise ValueError("Exactly 31 original source-empty restorations must be matched")
    return result


ALLOWED_CANDIDATE_EVIDENCE_FIELDS = {
    "source_key", "article_xml_id", "review_queue",
    "source_latin_token_count", "candidate_ocr_latin_token_count",
    "source_tokens_sha256", "ocr_candidate_tokens_sha256",
    "initial_heading_scan_pdf_page_1_based",
    "next_known_heading_scan_pdf_page_1_based",
    "next_source_article_key", "span_pdf_page_count_inclusive",
    "ocr_word_count_by_scan_page", "tei_token_unigram_recall",
    "tei_token_bigram_recall", "tei_token_trigram_recall",
    "tei_token_fourgram_recall", "unique_fourgram_overlap_footprint",
    "print_abbreviation_equivalence_research",
    "candidate_ocr_span_not_an_original_print_certification",
    "print_page_images_directly_compared",
    "textual_correction_authorized", "publication_permitted",
}


def verify_target_evidence(report):
    """Fail closed for every v4 queue entry, no invented visual print review.

    Because source prose must never appear in an artifact, allow only
    explicitly known numerical/digest/location/provenance fields.
    """
    rows = report["entries"]
    source = {r["article_key"]: (i, r) for i, r in enumerate(rows)}
    expected = {
        row["article_key"]: diagnostic_category(row)
        for row in rows if diagnostic_category(row) is not None
    }
    supplied = report.get("content_candidate_diagnostics")
    if (not isinstance(supplied, list)
            or report.get("content_candidate_diagnostic_count") != len(supplied)):
        raise ValueError("OCR evidence row inventory missing")
    seen = set()
    for evidence in supplied:
        if not isinstance(evidence, dict) or set(evidence) != ALLOWED_CANDIDATE_EVIDENCE_FIELDS:
            raise ValueError("Unexpected OCR evidence fields or prohibited text leak")
        key = evidence["source_key"]
        if key in seen or key not in expected:
            raise ValueError("Duplicate or invented OCR research case")
        seen.add(key)
        i, row = source[key]
        if i + 1 >= len(rows):
            raise ValueError("OCR case has no next real TEI article")
        if (
            evidence["article_xml_id"] != row["article_xml_id"]
            or evidence["review_queue"] != expected[key]
            or evidence["source_latin_token_count"] != row["tei_latin_tokens"]
            or evidence["candidate_ocr_latin_token_count"] != row["ocr_latin_tokens"]
            or evidence["tei_token_fourgram_recall"] != row["source_fourgram_recall"]
            or evidence["initial_heading_scan_pdf_page_1_based"] != row["ocr_start_pdf_page"]
            or evidence["next_known_heading_scan_pdf_page_1_based"] != row["ocr_end_pdf_page"]
            or evidence["next_source_article_key"] != rows[i+1]["article_key"]
            or evidence["span_pdf_page_count_inclusive"] != (
                row["ocr_end_pdf_page"] - row["ocr_start_pdf_page"] + 1
            )
            or evidence["candidate_ocr_span_not_an_original_print_certification"] is not True
            or evidence["print_page_images_directly_compared"] is not False
            or evidence["textual_correction_authorized"] is not False
            or evidence["publication_permitted"] is not False
        ):
            raise ValueError("OCR research evidence contradicts source-locked article")
        if any(not re.fullmatch(r"[0-9a-f]{64}", evidence[d]) for d in (
            "source_tokens_sha256", "ocr_candidate_tokens_sha256"
        )):
            raise ValueError("Missing reproducible normalized-text SHA-256 fingerprints")
        scores = [evidence[s] for s in (
            "tei_token_unigram_recall", "tei_token_bigram_recall",
            "tei_token_trigram_recall", "tei_token_fourgram_recall"
        )]
        if any(not isinstance(score, (float, int)) or not 0 <= score <= 1
               for score in scores):
            raise ValueError("OCR token-overlap evidence outside possible bounds")
        variant = evidence["print_abbreviation_equivalence_research"]
        if evidence["review_queue"] == "similar_length_low_phrase_overlap":
            required_variant_fields = {
                "raw_source_fourgram_recall",
                "derived_abbreviation_equivalence_fourgram_recall",
                "derived_minus_raw_fourgram_recall",
                "source_expressions_compacted_by_print_abbreviation",
                "diagnostic_source_derived_token_count",
                "original_tei_and_ocr_text_unchanged",
                "printed_abbreviation_matches_are_not_image_certifications",
                "publication_permitted",
            }
            if (not isinstance(variant, dict)
                    or set(variant) != required_variant_fields
                    or variant["raw_source_fourgram_recall"] != row["source_fourgram_recall"]
                    or variant["original_tei_and_ocr_text_unchanged"] is not True
                    or variant["printed_abbreviation_matches_are_not_image_certifications"] is not True
                    or variant["publication_permitted"] is not False):
                raise ValueError("Unknown or overstated historical abbreviation research")
            folded = variant["derived_abbreviation_equivalence_fourgram_recall"]
            diff = variant["derived_minus_raw_fourgram_recall"]
            counts = variant["source_expressions_compacted_by_print_abbreviation"]
            nfolded = variant["diagnostic_source_derived_token_count"]
            allowed = {abbr for _, abbr in EXPLICIT_SOURCE_TO_PRINT}
            if (not isinstance(folded, (float, int)) or not 0 <= folded <= 1
                    or not isinstance(diff, (float, int))
                    or diff != round(folded - row["source_fourgram_recall"], 4)
                    or not isinstance(nfolded, int) or not 4 <= nfolded <= row["tei_latin_tokens"]
                    or not isinstance(counts, dict)
                    or any(label not in allowed or not isinstance(n, int) or n <= 0
                           for label, n in counts.items())):
                raise ValueError("Source-only abbreviation equivalence score is invalid")
        elif variant is not None:
            raise ValueError("Long-span cases must not claim shorthand reconciliation")
        page_counts = evidence["ocr_word_count_by_scan_page"]
        if not page_counts or not isinstance(page_counts, list):
            raise ValueError("No original scan page distribution for OCR evidence")
        encountered = []
        total = 0
        for page in page_counts:
            if not isinstance(page, dict) or set(page) != {
                "scan_pdf_page_1_based", "ocr_tokens_in_page_segment"
            }:
                raise ValueError("Malformed OCR page distribution")
            n, count = page["scan_pdf_page_1_based"], page["ocr_tokens_in_page_segment"]
            if not isinstance(n, int) or not isinstance(count, int) or count < 0:
                raise ValueError("Impossible OCR page/token counter")
            if not (row["ocr_start_pdf_page"] <= n <= row["ocr_end_pdf_page"]):
                raise ValueError("OCR evidence page lies outside two heading anchors")
            encountered.append(n)
            total += count
        if (encountered != sorted(set(encountered))
                or encountered[0] != row["ocr_start_pdf_page"]
                or total != row["ocr_latin_tokens"] + len(latin_tokens(key))):
            raise ValueError("OCR page distribution differs from recorded article span")
        matched = evidence["unique_fourgram_overlap_footprint"]
        if matched is not None:
            required = {
                "matched_unique_fourgrams", "window_80pct_matched_fourgrams",
                "window_first_ocr_token_offset", "window_last_ocr_token_offset",
                "window_length_latin_tokens", "window_fraction_of_full_ocr_span",
                "window_first_scan_pdf_page_1_based",
                "window_last_scan_pdf_page_1_based",
                "source_print_fidelity_certified",
            }
            if not isinstance(matched, dict) or set(matched) != required:
                raise ValueError("Malformed high-specificity OCR localization")
            if matched["source_print_fidelity_certified"] is not False:
                raise ValueError("Automated 4-gram location is not page-image certification")
            if not (
                12 <= matched["window_80pct_matched_fourgrams"]
                <= matched["matched_unique_fourgrams"]
                and 0 <= matched["window_first_ocr_token_offset"]
                <= matched["window_last_ocr_token_offset"] < row["ocr_latin_tokens"]
                and matched["window_length_latin_tokens"] == (
                    matched["window_last_ocr_token_offset"]
                    - matched["window_first_ocr_token_offset"] + 1
                )
                and 0 < matched["window_fraction_of_full_ocr_span"] <= 1
                and row["ocr_start_pdf_page"]
                <= matched["window_first_scan_pdf_page_1_based"]
                <= matched["window_last_scan_pdf_page_1_based"]
                <= row["ocr_end_pdf_page"]
            ):
                raise ValueError("OCR source-match region not in original article span")
    if seen != set(expected):
        raise ValueError("Inconsistent or missing v4 candidate diagnostics")
    return supplied


def aggregate(reports, manifest, recovery_map=None):
    source = {v["volume"]: v for v in manifest["volumes"]}
    if set(source) != VOLUMES or manifest.get("canonical_tei_sha256") != SOURCE_LOCK:
        raise ValueError("Unexpected original 1915 five-volume witness manifest")
    if len(reports) != 5 or {r["volume"] for r in reports} != VOLUMES:
        raise ValueError("Expected exactly one result for each of five original volumes")
    by_volume, rows = {}, []
    content_target_evidence = []
    keys, ids = set(), set()
    statuses = Counter()
    for report in sorted(reports, key=lambda r: r["volume"]):
        vol = report["volume"]
        if (report.get("schema_version") != 8
                or report.get("print_pdf_sha256") != source[vol]["pdf_sha256"]
                or report.get("canonical_tei_sha256") != SOURCE_LOCK
                or report.get("pdf_pages") != source[vol]["pages"]
                or report.get("independent_print_order_does_not_imply_digital_source_order") is not True
                or report.get("publication_permitted") is not False
                or report.get("ocr_not_original_print_certification") is not True
                or report.get("articles_in_volume") != len(report.get("entries", []))
                or report.get("article_count_sum") != len(report["entries"])):
            raise ValueError("Source-locked OCR report incomplete or overclaims evidence")
        vstatus = Counter()
        checked = 0
        by_source_key = {r["article_key"]: r for r in report["entries"]}
        if len(by_source_key) != len(report["entries"]):
            raise ValueError("Duplicate canonical article identifiers within a volume")
        for row in report["entries"]:
            key, aid, status = row["article_key"], row["article_xml_id"], row["status"]
            nsource, nocr = row["tei_latin_tokens"], row["ocr_latin_tokens"]
            if (key in keys or aid in ids or expected_volume(key) != vol
                    or not isinstance(nsource, int) or nsource < 0
                    or status not in STATUSES
                    or row.get("visually_verified") is not False
                    or row.get("full_print_text_certified") is not False):
                raise ValueError("Duplicate, invalid or falsely certified article")
            keys.add(key)
            ids.add(aid)
            candidate_print_titles = row.get("intervening_print_heading_candidates")
            withheld_start = row.get("withheld_ocr_span_start_scan_pdf_page_1_based")
            withheld_end = row.get("withheld_ocr_span_next_heading_scan_pdf_page_1_based")
            if not isinstance(candidate_print_titles, list):
                raise ValueError("Missing original print-order research metadata")
            if status == "unresolved_intervening_print_heading":
                if (not candidate_print_titles
                        or not isinstance(withheld_start, int)
                        or not isinstance(withheld_end, int)
                        or not (1 <= withheld_start <= withheld_end <= source[vol]["pages"])):
                    raise ValueError("Suspicious printed-order conflict has no source-page witnesses")
                for title in candidate_print_titles:
                    if set(title) != {
                        "source_key", "source_article_xml_id",
                        "scan_pdf_page_1_based", "image_verified"
                    }:
                        raise ValueError("Unexpected or textual raw print-order data")
                    other = by_source_key.get(title["source_key"])
                    if (other is None or title["source_key"] == key
                            or title["source_article_xml_id"] != other["article_xml_id"]
                            or title["image_verified"] is not False
                            or not (withheld_start <= title["scan_pdf_page_1_based"]
                                    <= withheld_end)):
                        raise ValueError("Invented printed title, location or visual proof")
            elif candidate_print_titles or withheld_start is not None or withheld_end is not None:
                raise ValueError("Unflagged OCR row contains unreviewed interleaving")
            if nocr is None:
                if (status not in {
                        "unresolved_print_boundaries", "unresolved_intervening_print_heading"
                    }
                        or row.get("ocr_to_tei_ratio") is not None
                        or row.get("ocr_start_pdf_page") is not None
                        or row.get("ocr_end_pdf_page") is not None):
                    raise ValueError("Unresolved article contains invented OCR measurement")
            else:
                checked += 1
                if (not isinstance(nocr, int) or nocr < 0
                        or status == "unresolved_print_boundaries"
                        or not isinstance(row.get("ocr_start_pdf_page"), int)
                        or not isinstance(row.get("ocr_end_pdf_page"), int)
                        or not (1 <= row["ocr_start_pdf_page"] <= row["ocr_end_pdf_page"] <= source[vol]["pages"])):
                    raise ValueError("Impossible OCR boundary or word count")
                if nsource == 0:
                    if status not in {"source_empty_print_ocr_nonempty", "both_zero_candidate"}:
                        raise ValueError("Zero-source article has invalid OCR disposition")
                elif status not in {"ocr_count_near_source_candidate", "ocr_count_diff_over_10pct_candidate"}:
                    raise ValueError("Nonempty article has invalid OCR comparison disposition")
            recall = row.get("source_fourgram_recall")
            precision = row.get("ocr_fourgram_precision")
            if nocr is None or nsource < 4 or nocr < 4:
                if recall is not None or precision is not None:
                    raise ValueError("Cannot claim phrase overlap without two real text spans")
            elif (not isinstance(recall, (float, int))
                  or not isinstance(precision, (float, int))
                  or not 0 <= recall <= 1
                  or not 0 <= precision <= 1):
                raise ValueError("Missing normalized lexical overlap evidence")
            vstatus[status] += 1
            statuses[status] += 1
            rows.append({**row, "volume": vol})
        if dict(sorted(vstatus.items())) != report["status_counts"]:
            raise ValueError("Raw entry status counts and volume summary disagree")
        if vstatus["unresolved_intervening_print_heading"] != report.get(
                "ocr_intervals_withdrawn_due_to_independent_intervening_print_headwords"):
            raise ValueError("Intervening printed headword guard not reconciled")
        content_target_evidence.extend(
            {**evidence, "original_print_volume": vol}
            for evidence in verify_target_evidence(report)
        )
        by_volume[vol] = {
            "source_articles": len(report["entries"]),
            "count_comparable_articles": checked,
            "unresolved_boundaries": (
                vstatus["unresolved_print_boundaries"]
                + vstatus["unresolved_intervening_print_heading"]
            ),
            "intervening_print_heading_cases": vstatus["unresolved_intervening_print_heading"],
            "status_counts": dict(sorted(vstatus.items())),
            "ocr_extraction_seconds": report.get("ocr_extraction_seconds"),
            "heading_diagnostics": report["heading_diagnostics"],
            "print_pdf_sha256": report["print_pdf_sha256"],
        }
    if len(keys) != 9380:
        raise ValueError(f"Incomplete source article coverage: {len(keys)} / 9380")
    if not any(r["ocr_latin_tokens"] is not None for r in rows):
        raise ValueError("No adjacent article OCR boundaries could be aligned")
    empty_ocr = sorted(
        [r for r in rows if r["status"] == "source_empty_print_ocr_nonempty"],
        key=lambda r: r["article_key"],
    )
    recovered = [
        {"source_key": r["article_key"], "volume": r["volume"],
         "ocr_latin_tokens": r["ocr_latin_tokens"],
         "already_restored_in_separate_1915_tei": r["article_key"] in recovery_map,
         "approved_recovery_kind": recovery_map.get(r["article_key"])}
        for r in empty_ocr
    ] if recovery_map is not None else []
    discrepant = [
        r for r in rows if r["status"] == "ocr_count_diff_over_10pct_candidate"
    ]
    # Relative gap measures attention priority, NOT editorial confidence.
    discrepant.sort(
        key=lambda r: (
            -abs(r["ocr_latin_tokens"] - r["tei_latin_tokens"])
            / max(1, r["tei_latin_tokens"]),
            -abs(r["ocr_latin_tokens"] - r["tei_latin_tokens"]),
            r["article_key"],
        )
    )
    # A similar length can hide unrelated text. Neither word counts nor
    # machine OCR four-gram agreement are publication/certification gates.
    count_near_low_overlap = sorted(
        [r for r in rows
         if (r["status"] == "ocr_count_near_source_candidate"
             and r["tei_latin_tokens"] >= 100
             and r["source_fourgram_recall"] is not None
             and r["source_fourgram_recall"] < 0.25)],
        key=lambda r: (r["source_fourgram_recall"], -r["tei_latin_tokens"], r["article_key"]),
    )
    # High source phrase recovery but much more OCR prose may indicate an
    # edition difference, a longer printed article, or poor OCR boundaries.
    ocr_excess_source_present = sorted(
        [r for r in discrepant
         if (r["tei_latin_tokens"] >= 100
             and r["ocr_latin_tokens"] >= 2 * r["tei_latin_tokens"]
             and r["source_fourgram_recall"] is not None
             and r["source_fourgram_recall"] >= 0.6)],
        key=lambda r: (
            -(r["ocr_latin_tokens"] - r["tei_latin_tokens"]),
            r["article_key"],
        ),
    )
    # Independent whole-corpus queue calculation must match all detailed
    # dossiers exactly; never pass a test by accepting missing candidates.
    actual_diagnostic_kinds = Counter(
        evidence["review_queue"] for evidence in content_target_evidence
    )
    expected_diagnostic_kinds = Counter({
        "similar_length_low_phrase_overlap": len(count_near_low_overlap),
        "long_ocr_span_source_phrases_present": len(ocr_excess_source_present),
    })
    if actual_diagnostic_kinds != +expected_diagnostic_kinds:
        raise ValueError("Candidate evidence coverage does not match independent full-corpus queues")

    low_abbreviation_evidence = sorted(
        (
            e for e in content_target_evidence
            if e["review_queue"] == "similar_length_low_phrase_overlap"
        ),
        key=lambda e: (
            -e["print_abbreviation_equivalence_research"]["derived_minus_raw_fourgram_recall"],
            e["source_key"],
        ),
    )
    shorthand_material_gain = sum(
        e["print_abbreviation_equivalence_research"]["derived_minus_raw_fourgram_recall"] >= 0.10
        for e in low_abbreviation_evidence
    )
    shorthand_at_least25 = sum(
        e["print_abbreviation_equivalence_research"][
            "derived_abbreviation_equivalence_fourgram_recall"
        ] >= 0.25
        for e in low_abbreviation_evidence
    )
    shorthand_counts = Counter()
    for e in low_abbreviation_evidence:
        shorthand_counts.update(
            e["print_abbreviation_equivalence_research"][
                "source_expressions_compacted_by_print_abbreviation"
            ]
        )
    def word_count_band(n):
        if n < 20:
            return "00_0_to_19_source_words"
        if n < 100:
            return "01_20_to_99_source_words"
        if n < 500:
            return "02_100_to_499_source_words"
        return "03_500_plus_source_words"

    discrepant_by_source_size = Counter(
        word_count_band(r["tei_latin_tokens"]) for r in discrepant
    )
    discrepancy_directions = Counter(
        "ocr_longer" if r["ocr_latin_tokens"] > r["tei_latin_tokens"] else "tei_longer"
        for r in discrepant
    )
    # Rank substantive source articles separately. Relative ratios of very
    # short redirects are useful flags but would otherwise monopolize the
    # highest-priority list without proving missing printed prose.
    substantive = sorted(
        (
            r for r in discrepant
            if r["tei_latin_tokens"] >= 100
            and abs(r["ocr_latin_tokens"] - r["tei_latin_tokens"]) >= 50
        ),
        key=lambda r: (
            -abs(r["ocr_latin_tokens"] - r["tei_latin_tokens"]),
            r["article_key"],
        ),
    )
    def brief(r):
        return {
            "source_key": r["article_key"],
            "article_xml_id": r["article_xml_id"],
            "volume": r["volume"],
            "ocr_start_pdf_page": r["ocr_start_pdf_page"],
            "tei_latin_tokens": r["tei_latin_tokens"],
            "ocr_latin_tokens": r["ocr_latin_tokens"],
            "ocr_to_tei_ratio": r["ocr_to_tei_ratio"],
            "absolute_latin_token_difference": abs(
                r["ocr_latin_tokens"] - r["tei_latin_tokens"]
            ),
            "status": r["status"],
            "source_print_certified": False,
            "source_fourgram_recall": r["source_fourgram_recall"],
            "ocr_fourgram_precision": r["ocr_fourgram_precision"],
        }
    return {
        "schema_version": 8,
        "source": manifest["bibliographic_citation"],
        "canonical_tei_sha256": SOURCE_LOCK,
        "full_corpus_source_articles": len(keys),
        "original_pdf_sha256_by_volume": {v: source[v]["pdf_sha256"] for v in sorted(VOLUMES)},
        "five_source_pdfs_verified": True,
        "count_comparable_articles": sum(
            r["ocr_latin_tokens"] is not None for r in rows
        ),
        "unresolved_ocr_article_boundaries": (
            statuses["unresolved_print_boundaries"]
            + statuses["unresolved_intervening_print_heading"]
        ),
        "withheld_due_to_detected_intervening_print_titles": statuses[
            "unresolved_intervening_print_heading"
        ],
        "possible_print_order_interleavings": [
            {
                "source_key": r["article_key"], "source_article_xml_id": r["article_xml_id"],
                "volume": r["volume"],
                "withheld_ocr_span_start_pdf_page": r[
                    "withheld_ocr_span_start_scan_pdf_page_1_based"
                ],
                "withheld_ocr_span_end_pdf_page": r[
                    "withheld_ocr_span_next_heading_scan_pdf_page_1_based"
                ],
                "candidate_independent_print_titles": r["intervening_print_heading_candidates"],
                "original_print_image_verified": False,
            }
            for r in sorted(
                (r for r in rows if r["status"] == "unresolved_intervening_print_heading"),
                key=lambda r: (r["volume"], r["article_key"])
            )
        ],
        "status_counts": dict(sorted(statuses.items())),
        "volume_summaries": by_volume,
        "ocr_only_not_print_certified": True,
        "no_editorial_changes_approved": True,
        "source_empty_candidates_in_ocr": len(empty_ocr),
        "source_empty_crosscheck_performed": recovery_map is not None,
        "already_separately_restored_source_empty_candidates": (
            sum(r["already_restored_in_separate_1915_tei"] for r in recovered)
            if recovery_map is not None else None
        ),
        "new_unreviewed_source_empty_candidates": (
            sum(not r["already_restored_in_separate_1915_tei"] for r in recovered)
            if recovery_map is not None else None
        ),
        "source_empty_candidates": recovered,
        "content_candidate_diagnostics": sorted(
            content_target_evidence,
            key=lambda r: (r["review_queue"], r["original_print_volume"], r["source_key"])
        ),
        "content_candidate_diagnostic_count": len(content_target_evidence),
        "abbreviation_research_low_overlap_cases": len(low_abbreviation_evidence),
        "abbreviation_research_gain_at_least_10pct_points": shorthand_material_gain,
        "abbreviation_research_derived_overlap_at_least_25pct": shorthand_at_least25,
        "abbreviation_research_source_expression_counts": dict(sorted(shorthand_counts.items())),
        "abbreviation_research_ranked_candidates": [
            {
                "source_key": e["source_key"],
                "volume": e["original_print_volume"],
                "source_fourgram_recall_raw": e["tei_token_fourgram_recall"],
                "diagnostic_folded_fourgram_recall": e[
                    "print_abbreviation_equivalence_research"
                ]["derived_abbreviation_equivalence_fourgram_recall"],
                "diagnostic_gain": e["print_abbreviation_equivalence_research"][
                    "derived_minus_raw_fourgram_recall"
                ],
                "image_article_prose_certified": False,
            }
            for e in low_abbreviation_evidence
        ],
        "content_candidate_diagnostics_by_queue": dict(sorted(Counter(
            e["review_queue"] for e in content_target_evidence
        ).items())),
        "difference_direction_counts": dict(sorted(discrepancy_directions.items())),
        "discrepancies_by_source_size": dict(sorted(discrepant_by_source_size.items())),
        "substantive_source_difference_candidates_count": len(substantive),
        "near_word_count_but_low_source_phrase_overlap": len(count_near_low_overlap),
        "top_30_near_word_count_low_overlap": [
            brief(r) for r in count_near_low_overlap[:30]
        ],
        "large_ocr_excess_with_source_phrase_overlap": len(ocr_excess_source_present),
        "top_30_ocr_excess_with_source_phrase_overlap": [
            brief(r) for r in ocr_excess_source_present[:30]
        ],
        "top_50_substantive_source_abs_differences": [
            brief(r) for r in substantive[:50]
        ],
        "publication_permitted": False,
        "counting_limitation": "Normalized Latin tokens only; exact article boundaries, multilingual words, punctuation, diagrams and OCR quality cannot be historically certified from this report",
        "top_50_discrepancy_candidates": [
            brief(r) for r in discrepant[:50]
        ],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reports-dir", type=Path, required=True)
    p.add_argument("--manifest", type=Path,
                   default=Path("sources/print/1915-volume-witnesses.json"))
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--approved-recovery-ledger", type=Path)
    p.add_argument("--original-empty-source-ledger", type=Path)
    args = p.parse_args()
    if bool(args.approved_recovery_ledger) != bool(args.original_empty_source_ledger):
        p.error("Both original and approved recovery ledgers are required together")
    recovery = approved_recovery_map(
        json.loads(args.approved_recovery_ledger.read_text(encoding="utf-8")),
        json.loads(args.original_empty_source_ledger.read_text(encoding="utf-8")),
    ) if args.approved_recovery_ledger else None
    paths = sorted(args.reports_dir.glob("volume-*.json"))
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = aggregate(reports, manifest, recovery_map=recovery)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "full_corpus_source_articles": result["full_corpus_source_articles"],
        "count_comparable_articles": result["count_comparable_articles"],
        "unresolved_ocr_article_boundaries": result["unresolved_ocr_article_boundaries"],
        "withheld_due_to_intervening_print_titles": result[
            "withheld_due_to_detected_intervening_print_titles"
        ],
        "possible_print_order_interleavings": result["possible_print_order_interleavings"][:12],
        "status_counts": result["status_counts"],
        "difference_direction_counts": result["difference_direction_counts"],
        "discrepancies_by_source_size": result["discrepancies_by_source_size"],
        "substantive_source_difference_candidates": result[
            "substantive_source_difference_candidates_count"
        ],
        "near_word_count_but_low_source_phrase_overlap": result[
            "near_word_count_but_low_source_phrase_overlap"
        ],
        "target_evidence_cases": result["content_candidate_diagnostic_count"],
        "target_evidence_by_queue": result["content_candidate_diagnostics_by_queue"],
        "abbreviation_research_cases": result["abbreviation_research_low_overlap_cases"],
        "abbreviation_research_gain_10pct_points": result[
            "abbreviation_research_gain_at_least_10pct_points"
        ],
        "abbreviation_research_derived_recall_at_least_25pct": result[
            "abbreviation_research_derived_overlap_at_least_25pct"
        ],
        "abbreviation_research_counts": result[
            "abbreviation_research_source_expression_counts"
        ],
        "top_10_abbreviation_research": result[
            "abbreviation_research_ranked_candidates"
        ][:10],
        "first_10_target_evidence": result["content_candidate_diagnostics"][:10],
        "large_ocr_excess_with_source_phrase_overlap": result[
            "large_ocr_excess_with_source_phrase_overlap"
        ],
        "top_5_near_count_low_overlap": result["top_30_near_word_count_low_overlap"][:5],
        "top_5_substantive_source_abs_differences": result[
            "top_50_substantive_source_abs_differences"
        ][:5],
        "source_empty_ocr_candidates": result["source_empty_candidates_in_ocr"],
        "source_empty_already_restored_in_separate_edition": result[
            "already_separately_restored_source_empty_candidates"
        ],
        "source_empty_new_unreviewed": result["new_unreviewed_source_empty_candidates"],
        "by_volume": {
            k: {
                "source_articles": r["source_articles"],
                "count_comparable_articles": r["count_comparable_articles"],
                "ocr_extraction_seconds": r["ocr_extraction_seconds"],
            }
            for k, r in result["volume_summaries"].items()
        },
        "top_10_discrepancy_candidates": result["top_50_discrepancy_candidates"][:10],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
