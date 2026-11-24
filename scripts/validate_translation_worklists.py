#!/usr/bin/env python3
"""Validate canonical-index worklists for a staged multilingual TEI translation.

Worklists are immutable *assignments*, not approval records. A checkbox may only
be marked after a complete article is drafted, source-collated, reviewed and
committed; draft coverage and editorial sign-off remain separate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.select_translation_pilot import SOURCE_COUNT, SOURCE_SHA256
from scripts.validate_translation_identity import entries, read_body, sha256

WORKLIST_KIND = "source_locked_translation_worklist"


def load_worklist(path: Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "schema_version": 1,
        "kind": WORKLIST_KIND,
        "source_sha256": SOURCE_SHA256,
        "source_article_count": SOURCE_COUNT,
        "publication_permitted": False,
        "status": "queued_requires_verified_full_article",
    }
    for field, expected in required.items():
        if data.get(field) != expected:
            raise ValueError(f"{path}: invalid worklist {field}")
    language = data.get("translation_language")
    if not isinstance(language, str) or not language or language == "en":
        raise ValueError(f"{path}: expected non-English target language")
    first, last, count = data.get("start"), data.get("end"), data.get("article_count")
    if not all(isinstance(x, int) for x in (first, last, count)):
        raise ValueError(f"{path}: invalid numeric source index range")
    if first < 1 or last > SOURCE_COUNT or last < first or last - first + 1 != count:
        raise ValueError(f"{path}: invalid contiguous source range")
    if count < 1 or count > 1000:
        raise ValueError(f"{path}: an individual ticket may not exceed 1000 entries")
    if len(data.get("entries", [])) != count:
        raise ValueError(f"{path}: source index inventory length mismatch")
    return data


def validate(source: Path, worklists: list[Path], *, expected_start=1,
             expected_entries=None) -> dict:
    if sha256(source) != SOURCE_SHA256:
        raise ValueError("Corrected historical English master hash mismatch")
    _, body = read_body(source)
    canonical = entries(body)
    if len(canonical) != SOURCE_COUNT:
        raise ValueError("Canonical source entry count mismatch")
    if not worklists:
        raise ValueError("No worklists supplied")
    rosters = sorted((load_worklist(path) for path in worklists),
                     key=lambda p: p["start"])
    expected_position = expected_start
    seen_keys = set()
    seen_ids = set()
    result = []
    for roster in rosters:
        if roster["start"] != expected_position:
            raise ValueError(f"Worklist gap/overlap before index {roster['start']}")
        if roster["translation_language"] != rosters[0]["translation_language"]:
            raise ValueError("Mixed translation languages in one worklist wave")
        if roster.get("wave") != rosters[0].get("wave"):
            raise ValueError("Mixed worklist waves")
        for slot, row in enumerate(roster["entries"], start=roster["start"]):
            if set(row) != {"index", "source_key", "article_id"}:
                raise ValueError(f"Unexpected canonical worklist fields at {slot}")
            if row["index"] != slot:
                raise ValueError(f"Out-of-order source index at {slot}")
            original_id, original_key = canonical[slot - 1]
            if (row["article_id"], row["source_key"]) != (
                    original_id, original_key):
                raise ValueError(f"Original TEI ID/SWORD key mismatch at {slot}")
            if original_id in seen_ids or original_key in seen_keys:
                raise ValueError(f"Duplicate canonical source index at {slot}")
            seen_ids.add(original_id)
            seen_keys.add(original_key)
        expected_position = roster["end"] + 1
        result.append({
            "wave": roster["wave"], "lot": roster["lot"],
            "start": roster["start"], "end": roster["end"],
            "entry_count": roster["article_count"],
            "first_key": roster["entries"][0]["source_key"],
            "last_key": roster["entries"][-1]["source_key"],
        })
    if expected_entries is not None and len(seen_ids) != expected_entries:
        raise ValueError("Requested wave coverage count mismatch")
    return {
        "schema_version": 1,
        "status": "canonical_source_worklist_verified_not_translated",
        "source_sha256": SOURCE_SHA256,
        "canonical_article_count": SOURCE_COUNT,
        "target_language": rosters[0]["translation_language"],
        "wave": rosters[0]["wave"],
        "assigned_count": len(seen_ids),
        "start": expected_start,
        "end": expected_position - 1,
        "published": False,
        "editorial_approval_implied": False,
        "lots": result,
    }


def render_ticket(roster: dict, *, parent_issue=103) -> str:
    """One GitHub issue with exactly one *unchecked* task per source entry."""
    first, last = roster["start"], roster["end"]
    lines = [
        f"## ISBE 1915 French — wave {roster['wave']}, lot {roster['lot']}",
        "",
        f"**Canonical source entries:** {first}–{last} inclusive "
        f"({roster['article_count']} articles).",
        "**Source of truth:** corrected original English ISBE 1915 TEI, "
        f"SHA-256 `{SOURCE_SHA256}`. Never derive translation from "
        "the original CrossWire intermediate or a modern-English paraphrase.",
        f"**Master plan:** #{parent_issue}. "
        "The full index is 9,380 entries; this ticket is one contiguous slice.",
        "",
        "## MHCC-derived per-article process",
        "",
        "1. Read the complete original TEI article, including its "
        "sections, references, notes and historical assertions.",
        "2. Translate the **entire** article in natural, accurate French; "
        "keep the original author's arguments, historical viewpoints and "
        "uncertainties. Do not modernize content or silently repair corruptions.",
        "3. Preserve the original canonical English `@n` SWORD key, "
        "`xml:id`, source order, source-language spans and link targets. "
        "Localize *visible labels* only; BRSI shares one canonical index.",
        "4. Reconstruct a full **readable article** from source-locked patches "
        "and compare it carefully against the English, paragraph by paragraph: "
        "meaning, omitted material, theology, proper names, references, "
        "headings and bibliography.",
        "5. Run source-parity, TEI and content tests, record review findings, "
        "commit the validated individual article or small group, and "
        "**only then tick that article**. If interrupted, resume from the "
        "committed patch and report, not merely from the checkbox.",
        "6. Record exceptions and uncertainties in review flags instead of "
        "editing the immutable original. **A checkbox does not authorize "
        "SWORD publication**: that has separate whole-corpus/editorial/reader "
        "acceptance gates.",
        "",
        "**At issue creation:** all tasks are unchecked, including source-locked "
        "first drafts that have not yet passed editorial collation. "
        "Drafted ≠ reviewed ≠ published.",
        "",
        "## Article checklist (canonical English source keys)",
        "",
    ]
    for entry in roster["entries"]:
        title = entry["source_key"]
        if "\n" in title or "`" in title:
            raise ValueError("Unsafe canonical label for Markdown checklist")
        lines.append(f"- [ ] {entry['index']:04d} `{title}`")
    lines.extend([
        "",
        "## Completion gate",
        "",
        "Close only when **all 1,000** checkboxes have individually verified "
        "source-fidelity reports and linked commits, with no unresolved "
        "content/structure defect in the covered articles. "
        "Do not interpret this issue closing as authorization to publish a module.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--worklist", action="append", type=Path, required=True)
    parser.add_argument("--expected-start", type=int, default=1)
    parser.add_argument("--expected-entries", type=int)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--issues-dir", type=Path,
                        help="Optionally render reproducible GitHub task-list bodies")
    args = parser.parse_args()
    report = validate(args.source, args.worklist,
                      expected_start=args.expected_start,
                      expected_entries=args.expected_entries)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    if args.issues_dir:
        args.issues_dir.mkdir(parents=True, exist_ok=True)
        for worklist in args.worklist:
            roster = load_worklist(worklist)
            filename = f"wave-{roster['wave']:02d}-lot-{roster['lot']:02d}.md"
            (args.issues_dir / filename).write_text(render_ticket(roster),
                                                     encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
