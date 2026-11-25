#!/usr/bin/env python3
"""Compile naturally translated Markdown paragraphs into source-locked TEI patches.

No machine translation and no guessed alignment: original paragraph boundaries
and inline references are explicit, protected tokens derived from exact TEI
source maps. A missing/changed anchor blocks compilation, not publication.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts.apply_translation_pilot import preserve_immutable, script_groups, text_units
from scripts.select_translation_pilot import SOURCE_SHA256
from scripts.translation_markdown_layout import (
    MARK, build_blocks, load_article, metadata, read_draft, template,
)


def compile_draft(archive_path: Path, markdown: str, *,
                  expected_sha: str = SOURCE_SHA256) -> tuple[dict, dict]:
    head, rendered = read_draft(markdown)
    source_key = head.get("source_key")
    if not isinstance(source_key, str) or not source_key:
        raise ValueError("Missing canonical original SWORD article key")
    row, original_article = load_article(archive_path, source_key,
                                         expected_sha=expected_sha)
    expected = metadata(row, source_sha=expected_sha)
    reasons = head.get("preserve")
    if not isinstance(reasons, dict) or any(
        not isinstance(key, str) or not isinstance(reason, str) or not reason.strip()
        for key, reason in reasons.items()
    ):
        raise ValueError("Preservation reasons require explicit nonempty text")
    if {k: v for k, v in head.items() if k != "preserve"} != {
        k: v for k, v in expected.items() if k != "preserve"
    }:
        raise ValueError("Canonical article identity, source revision or editorial state changed")

    blocks = build_blocks(original_article)
    if [b["id"] for b in blocks] != [number for number, _ in rendered]:
        raise ValueError("Missing, duplicated or reordered original TEI paragraph")
    targets: dict[tuple[int, str], str] = {}
    for block, (_, paragraph) in zip(blocks, rendered):
        if not paragraph.startswith(block["prefix"]):
            raise ValueError(f"Changed heading marker for original paragraph {block['id']}")
        content = paragraph[len(block["prefix"]):]
        pieces = MARK.split(content)
        source_markers = [p[1] for p in block["parts"] if p[0] == "marker"]
        if pieces[1::2] != source_markers:
            raise ValueError(f"Lost, altered or reordered inline TEI anchor: paragraph {block['id']}")
        gaps: list[list[tuple[int, str, str]]] = [[]]
        for kind, value in block["parts"]:
            if kind == "marker":
                gaps.append([])
            else:
                gaps[-1].append(value)
        if len(gaps) != len(pieces[::2]):
            raise ValueError("Missing source-owned anchor/translation boundary")
        for possible, translated in zip(gaps, pieces[::2]):
            if not possible:
                if translated.strip():
                    raise ValueError(f"Inserted new TEI text without a source slot: {block['id']}")
                continue
            if len(possible) != 1:
                raise ValueError("Ambiguous TEI translation slot")
            ordinal, part, english = possible[0]
            if not translated.strip():
                raise ValueError(f"Missing full translation for {ordinal}:{part}")
            if script_groups(english) != script_groups(translated):
                raise ValueError(f"Original Hebrew or Greek script changed at {ordinal}:{part}")
            identity = (ordinal, part)
            if identity in targets:
                raise ValueError("Repeated TEI translation slot")
            targets[identity] = translated

    patch_units = []
    consumed_preserve = set()
    for ordinal, node, part, english in text_units(original_article):
        identity = (ordinal, part)
        if preserve_immutable(node, part):
            if identity in targets:
                raise ValueError("Protected Scripture or original language was edited")
            continue
        key = f"{ordinal}:{part}"
        if identity not in targets:
            raise ValueError(f"Original text node left unassigned: {key}")
        french = targets[identity]
        reason = reasons.get(key)
        if french == english:
            if not reason:
                raise ValueError(f"English text still present without a preservation reason: {key}")
            consumed_preserve.add(key)
            action = "preserve"
        elif reason:
            raise ValueError(f"Preserve annotation conflicts with translated text: {key}")
        else:
            action = "translate"
        item = {"node": ordinal, "part": part, "source": english,
                "target": french, "action": action}
        if action == "preserve":
            item["reason"] = reason
        patch_units.append(item)
    if set(reasons) != consumed_preserve:
        raise ValueError("Preservation reasons are unrecognized or unused")

    # Independently apply patches in-memory and verify the unchanged canonical
    # TEI structure, source-owned attributes, Scripture and foreign-language data.
    copied = copy.deepcopy(original_article)
    original_nodes = list(original_article.iter())
    new_nodes = list(copied.iter())
    for unit in patch_units:
        setattr(new_nodes[unit["node"]], unit["part"], unit["target"])
    for source_node, target_node in zip(original_nodes, new_nodes):
        if (source_node.tag != target_node.tag
                or source_node.attrib != target_node.attrib):
            raise ValueError("TEI attributes, original IDs or element structure changed")
        if preserve_immutable(source_node, "text") and source_node.text != target_node.text:
            raise ValueError("Source-owned text changed in TEI roundtrip")
    if len(original_nodes) != len(new_nodes):
        raise ValueError("TEI roundtrip lost source nodes")

    patch = {
        "schema_version": 1,
        "source_work": "ISBE 1915 — corrected historical English master",
        "source_sha256": expected_sha,
        "language": "fr",
        "status": "unreviewed_drafts",
        "publication_permitted": False,
        "articles": [{
            "source_key": row["source_key"],
            "article_id": row["article_id"],
            "source_article_sha256": row["source_article_sha256"],
            "editorial_status": "complete_unreviewed_draft",
            "units": patch_units,
        }],
    }
    report = {
        "schema_version": 1,
        "original_source_key": row["source_key"],
        "original_article_id": row["article_id"],
        "original_article_sha256": row["source_article_sha256"],
        "source_paragraphs": len(blocks),
        "source_mutable_text_units": len(patch_units),
        "translated_units": sum(x["action"] == "translate" for x in patch_units),
        "explicit_preserved_units": sum(x["action"] == "preserve" for x in patch_units),
        "original_tei_structure_unchanged": True,
        "human_editorial_approvals": 0,
        "publication_permitted": False,
    }
    return patch, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    mk = sub.add_parser("template", help="Produce editable original-language paragraph Markdown")
    mk.add_argument("--archive", required=True, type=Path)
    mk.add_argument("--key", required=True, help="Exact original SWORD article key")
    mk.add_argument("--output", required=True, type=Path)
    build = sub.add_parser("compile", help="Compile finished paragraphs into source-locked JSON")
    build.add_argument("--archive", required=True, type=Path)
    build.add_argument("--input", required=True, type=Path)
    build.add_argument("--output", required=True, type=Path)
    build.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if args.action == "template":
        markdown = template(args.archive, args.key)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(json.dumps({"original_key": args.key,
                          "template": str(args.output),
                          "translation_completed": False,
                          "publication_permitted": False}))
    else:
        patch, report = compile_draft(
            args.archive, args.input.read_text(encoding="utf-8"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(patch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
