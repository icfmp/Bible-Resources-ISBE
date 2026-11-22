#!/usr/bin/env python3
"""Classify unresolved ISBE cross-reference targets without guessing links.

Produces a review queue; no source XML or article content is modified.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def stem(key):
    # Only for finding review candidates. Never use this as a direct link ID.
    return re.sub(r"\s+\(\d+\)$", "", key.strip(), flags=re.I).casefold()


def classify(target, keys_by_stem):
    stripped = target.strip()
    base = stem(stripped)
    candidates = keys_by_stem.get(base, ())
    if len(candidates) > 1:
        return "multiple_numbered_entries", list(candidates)
    if len(candidates) == 1:
        # A single entry is not always semantically equivalent: human review.
        return "single_numbered_entry_candidate", list(candidates)
    if stripped.casefold().rstrip(".") in ("literature",):
        return "article_section_label", []
    if re.match(r"^(?:[IVXLCDM]+\.\s+|\d+\.\s+)", stripped, flags=re.I):
        return "article_section_label", []
    if re.match(r"^[A-Z0-9,'; ().-]+(?:\s+(?:I|II|III|IV|V|VI|VII|VIII|IX|X))?$", stripped):
        return "unmatched_heading_or_alias", []
    return "unmatched_other", []


def audit(index, report):
    index_keys = [item["key"] for item in index]
    index_set = set(index_keys)
    stems = defaultdict(list)
    for key in index_keys:
        stems[stem(key)].append(key)
    records = []
    totals = Counter()
    for target, count in sorted(report["unresolved_isbe_links"].items()):
        if target in index_set:
            raise ValueError(f"Report says existing key is unresolved: {target}")
        status, suggestions = classify(target, stems)
        records.append({"source_target": target, "occurrences": count,
                        "category": status, "review_candidates": suggestions,
                        "status": "needs_review",
                        "navigation_status": "unlinked_not_clickable"})
        totals[status] += count
    if ("unlinked_source_reference_occurrences" in report
            and report["unlinked_source_reference_occurrences"]
            != report["unresolved_link_occurrences"]):
        raise ValueError("Unlinked source reference count differs from unresolved count")
    if sum(totals.values()) != report["unresolved_link_occurrences"]:
        raise ValueError("Cross-reference occurrence totals mismatch")
    return {"schema_version": 1, "purpose": "editorial_review_only",
            "navigation_status": "unlinked_not_clickable",
            "unresolved_occurrences": sum(totals.values()),
            "unresolved_distinct_targets": len(records),
            "categories_by_occurrence": dict(sorted(totals.items())),
            "review_queue": records}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--index", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    data = audit(json.loads(args.index.read_text(encoding="utf-8")),
                 json.loads(args.report.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({k: v for k, v in data.items() if k != "review_queue"}, indent=2))


if __name__ == "__main__":
    main()
