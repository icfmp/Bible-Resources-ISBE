#!/usr/bin/env python3
"""Generate readable, source-backed editorial proofs for translated TEI articles.

This is a generic source-fidelity review aid. It never changes original text,
approves drafts, updates GitHub checkboxes, or authorizes a SWORD release.
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

from scripts.apply_translation_batches import apply, load_patches
from scripts.render_translation_reading_copy import render_article
from scripts.select_translation_pilot import SOURCE_SHA256
from scripts.validate_translation_identity import XML_ID, read_body

SUSPICIOUS_MARKERS = ("@@", "\ufffd", "[source corrupted]", "[texte corrompu]")


def build(source: Path, patch_files: list[Path], preview_dir: Path,
          report_file: Path, flags_file: Path | None = None) -> dict:
    source = Path(source)
    patch_files = [Path(p) for p in patch_files]
    patches = load_patches(patch_files)
    preview_dir.mkdir(parents=True, exist_ok=True)
    flags = []
    if flags_file is not None:
        flagged = json.loads(Path(flags_file).read_text(encoding="utf-8"))
        if flagged.get("original_english_tei_sha256") != SOURCE_SHA256:
            raise ValueError("Source-review flags refer to a different English master")
        flags = flagged.get("items", [])
        for item in flags:
            if item["source_key"] not in {x["source_key"] for x in patches.values()}:
                raise ValueError("Source anomaly refers to an article outside review scope")
    flags_by_key = {}
    for flag in flags:
        flags_by_key.setdefault(flag["source_key"], []).append(flag)

    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        excerpt, raw_report = temp / "bilingual.xml", temp / "report.json"
        result = apply(source, patch_files, output=excerpt, report_path=raw_report)
        _, body = read_body(excerpt)
        report_by_id = {r["article_id"]: r for r in result["articles"]}
        articles = []
        used_paths = set()
        for article in body:
            article_id = article.get(XML_ID)
            original_key = article.get("n")
            record = report_by_id[article_id]
            if record["status"] != "complete_unreviewed_draft":
                raise ValueError(f"Cannot render incomplete source article: {original_key}")
            if (patches[article_id]["source_key"] != original_key or
                    patches[article_id]["article_id"] != article_id):
                raise ValueError("Canonical article ID/SWORD key mismatch")
            markdown = render_article(article, draft_status=record["status"])
            filename = article_id + ".md"
            if filename in used_paths:
                raise ValueError("Duplicate preview path")
            used_paths.add(filename)
            (preview_dir / filename).write_text(markdown, encoding="utf-8")
            patch = patches[article_id]
            target_units = patch["units"]
            preserved_count = sum(u["action"] == "preserve" for u in target_units)
            suspicious = sorted({m for u in target_units for m in SUSPICIOUS_MARKERS
                                 if m in u["target"]})
            articles.append({
                "source_key": original_key,
                "article_id": article_id,
                "title_fr": article.findtext(
                    "{http://www.tei-c.org/ns/1.0}head") or original_key,
                "preview": filename,
                "preview_chars": len(markdown),
                "text_units": len(target_units),
                "preserved_source_units": preserved_count,
                "draft_complete": True,
                "source_review_flags": len(flags_by_key.get(original_key, [])),
                "possible_source_corruption_markers_in_french": suspicious,
                "style_and_editorial_review": "pending",
                "independent_bilingual_collation": False,
                "publication_permitted": False,
            })
        if len(articles) != len(patches):
            raise ValueError("Draft/preview count mismatch")

    index_lines = [
        "# ISBE 1915 — French review copies",
        "",
        "**Working source-locked drafts, not editorially approved.** "
        "Each file is generated from historical English TEI and French patches. "
        "No article checkbox may be checked solely from this preview.",
        "",
        "| Original canonical key | French display title | Text units | Source flags | Review |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in articles:
        title = row["title_fr"].replace("|", "\\|")
        key = row["source_key"].replace("|", "\\|")
        index_lines.append(
            f"| [{key}]({row['preview']}) | {title} | {row['text_units']} | "
            f"{row['source_review_flags']} | pending |")
    (preview_dir / "INDEX.md").write_text("\n".join(index_lines) + "\n",
                                            encoding="utf-8")

    report = {
        "schema_version": 1,
        "status": "all_selected_drafts_readable_unreviewed_not_for_publication",
        "source_sha256": SOURCE_SHA256,
        "source_article_count": 9380,
        "selected_complete_unreviewed_drafts": len(articles),
        "pilot_drafts_count": sum(
            x["source_key"] != "ABRAHAM" for x in articles),
        "human_editorially_approved": 0,
        "source_flags_pending_witness_review": len(flags),
        "source_flag_affected_articles": len(flags_by_key),
        "markdown_previews_generated": len(articles),
        "article_checkboxes_marked_complete": 0,
        "publication_permitted": False,
        "articles": articles,
    }
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--patches", action="append", required=True, type=Path)
    parser.add_argument("--previews-dir", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--flags", type=Path)
    args = parser.parse_args()
    report = build(args.source, args.patches, args.previews_dir, args.report,
                   flags_file=args.flags)
    print(json.dumps({k: v for k, v in report.items() if k != "articles"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
