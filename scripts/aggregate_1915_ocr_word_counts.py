#!/usr/bin/env python3
"""Aggregate five 1915 volume OCR count candidates, not print certifications."""
import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.research_1915_print_pages import expected_volume

SOURCE_LOCK = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
VOLUMES = {"1", "2", "3", "4", "5"}
STATUSES = {
    "unresolved_print_boundaries", "source_empty_print_ocr_nonempty",
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


def aggregate(reports, manifest, recovery_map=None):
    source = {v["volume"]: v for v in manifest["volumes"]}
    if set(source) != VOLUMES or manifest.get("canonical_tei_sha256") != SOURCE_LOCK:
        raise ValueError("Unexpected original 1915 five-volume witness manifest")
    if len(reports) != 5 or {r["volume"] for r in reports} != VOLUMES:
        raise ValueError("Expected exactly one result for each of five original volumes")
    by_volume, rows = {}, []
    keys, ids = set(), set()
    statuses = Counter()
    for report in sorted(reports, key=lambda r: r["volume"]):
        vol = report["volume"]
        if (report.get("schema_version") != 4
                or report.get("print_pdf_sha256") != source[vol]["pdf_sha256"]
                or report.get("canonical_tei_sha256") != SOURCE_LOCK
                or report.get("pdf_pages") != source[vol]["pages"]
                or report.get("publication_permitted") is not False
                or report.get("ocr_not_original_print_certification") is not True
                or report.get("articles_in_volume") != len(report.get("entries", []))
                or report.get("article_count_sum") != len(report["entries"])):
            raise ValueError("Source-locked OCR report incomplete or overclaims evidence")
        vstatus = Counter()
        checked = 0
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
            if nocr is None:
                if (status != "unresolved_print_boundaries"
                        or row.get("ocr_to_tei_ratio") is not None
                        or row.get("ocr_start_pdf_page") is not None):
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
            if nocr is not None:
                rows.append({**row, "volume": vol})
        if dict(sorted(vstatus.items())) != report["status_counts"]:
            raise ValueError("Raw entry status counts and volume summary disagree")
        by_volume[vol] = {
            "source_articles": len(report["entries"]),
            "count_comparable_articles": checked,
            "unresolved_boundaries": vstatus["unresolved_print_boundaries"],
            "status_counts": dict(sorted(vstatus.items())),
            "ocr_extraction_seconds": report.get("ocr_extraction_seconds"),
            "heading_diagnostics": report["heading_diagnostics"],
            "print_pdf_sha256": report["print_pdf_sha256"],
        }
    if len(keys) != 9380:
        raise ValueError(f"Incomplete source article coverage: {len(keys)} / 9380")
    if not rows:
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
        "schema_version": 4,
        "source": manifest["bibliographic_citation"],
        "canonical_tei_sha256": SOURCE_LOCK,
        "full_corpus_source_articles": len(keys),
        "original_pdf_sha256_by_volume": {v: source[v]["pdf_sha256"] for v in sorted(VOLUMES)},
        "five_source_pdfs_verified": True,
        "count_comparable_articles": len(rows),
        "unresolved_ocr_article_boundaries": statuses["unresolved_print_boundaries"],
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
        "status_counts": result["status_counts"],
        "difference_direction_counts": result["difference_direction_counts"],
        "discrepancies_by_source_size": result["discrepancies_by_source_size"],
        "substantive_source_difference_candidates": result[
            "substantive_source_difference_candidates_count"
        ],
        "near_word_count_but_low_source_phrase_overlap": result[
            "near_word_count_but_low_source_phrase_overlap"
        ],
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
