#!/usr/bin/env python3
"""Rebuild source-locked, unpublished ISBE translation batches from text patches.

Accepts multiple batch or pilot patch files. Output may mix translated and
untranslated content, is ALWAYS clearly marked as a nonpublishable excerpt,
and is not a completed French SWORD/TEI edition.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.apply_translation_pilot import (
    preserve_immutable, script_groups, text_units,
)
from scripts.select_translation_pilot import (
    SOURCE_COUNT, SOURCE_SHA256, stable_xml_fingerprint,
)
from scripts.validate_translation_identity import (
    TEI, XML_ID, XML_LANG, entries, read_body, sha256,
)


def load_patches(paths: list[Path]) -> dict[str, dict]:
    if not paths:
        raise ValueError("At least one source-locked patch file is required")
    patches = {}
    for path in paths:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if (data.get("schema_version") != 1
                or data.get("source_sha256") != SOURCE_SHA256
                or data.get("language") != "fr"
                or data.get("status") != "unreviewed_drafts"
                or data.get("publication_permitted", False)):
            raise ValueError(f"Untrusted source, language or publication state: {path}")
        for article in data.get("articles", []):
            ident = article.get("article_id")
            if not ident or ident in patches:
                raise ValueError(f"Missing or duplicated article ID: {ident}")
            if not article.get("source_key") or not article.get("source_article_sha256"):
                raise ValueError("Article patch must identify original source key/hash")
            patches[ident] = article
    if not patches:
        raise ValueError("Patch set contains no articles")
    return patches


def apply(source: Path, patches: list[Path], *, output: Path,
          report_path: Path) -> dict:
    source = Path(source)
    if sha256(source) != SOURCE_SHA256:
        raise ValueError("Corrected historical English master hash mismatch")
    original_root, original_body = read_body(source)
    if original_root.get(XML_LANG) != "en":
        raise ValueError("Expected historical English master")
    original_index = entries(original_body)
    if len(original_index) != SOURCE_COUNT:
        raise ValueError("Unexpected number of canonical English articles")
    by_id = load_patches(patches)
    position_by_id = {ident: pos for pos, (ident, _) in enumerate(original_index)}
    extra = sorted(set(by_id) - set(position_by_id))
    if extra:
        raise ValueError(f"Unknown or fabricated canonical article IDs: {extra}")

    ids_in_master = set()
    for node in original_body.iter():
        ident = node.get(XML_ID)
        if ident:
            if ident in ids_in_master:
                raise ValueError("Duplicate original TEI xml:id")
            ids_in_master.add(ident)

    ET.register_namespace("", TEI[1:-1])
    result_root = ET.Element(TEI + "TEI", {XML_LANG: "mul"})
    header = ET.SubElement(result_root, TEI + "teiHeader")
    fd = ET.SubElement(header, TEI + "fileDesc")
    ts = ET.SubElement(fd, TEI + "titleStmt")
    ET.SubElement(ts, TEI + "title").text = "ISBE 1915 — brouillons de traduction, non publies"
    pub = ET.SubElement(fd, TEI + "publicationStmt")
    ET.SubElement(pub, TEI + "p").text = "Unreviewed incomplete excerpt; publication prohibited"
    sd = ET.SubElement(fd, TEI + "sourceDesc")
    ET.SubElement(sd, TEI + "p").text = (
        "Source: corrected historical English ISBE 1915; SHA-256 " + SOURCE_SHA256
    )
    body = ET.SubElement(ET.SubElement(result_root, TEI + "text"), TEI + "body")

    report_entries = []
    for ident in sorted(by_id, key=position_by_id.get):
        original = original_body[position_by_id[ident]]
        patch = by_id[ident]
        if patch["source_key"] != original.get("n"):
            raise ValueError("Canonical English key was translated or reassigned")
        if patch["source_article_sha256"] != stable_xml_fingerprint(original):
            raise ValueError(f"Canonical article fingerprint mismatch: {ident}")
        copy_article = copy.deepcopy(original)
        source_nodes = list(original.iter())
        translated_nodes = list(copy_article.iter())
        if len(source_nodes) != len(translated_nodes):
            raise ValueError("Unexpected article structure")
        unit_targets = {}
        for unit in patch.get("units", []):
            key = (unit.get("node"), unit.get("part"))
            if (not isinstance(key[0], int) or key[0] < 0
                    or key[1] not in ("text", "tail") or key in unit_targets):
                raise ValueError("Duplicated/malformed source node unit")
            if not isinstance(unit.get("source"), str) or not isinstance(unit.get("target"), str):
                raise ValueError("Text units need exact source and French strings")
            if not unit["target"].strip():
                raise ValueError("Translation must not erase a source text unit")
            unit_targets[key] = unit

        visited = set()
        eligible_count = 0
        for ordinal, node, part, source_text in text_units(original):
            key = (ordinal, part)
            if preserve_immutable(node, part):
                if key in unit_targets:
                    raise ValueError("Scripture locator or foreign text was altered")
                continue
            eligible_count += 1
            if key not in unit_targets:
                continue
            unit = unit_targets[key]
            if unit["source"] != source_text:
                raise ValueError(f"Source text mismatch for {ident} at {key}")
            if script_groups(unit["source"]) != script_groups(unit["target"]):
                raise ValueError("Original Greek/Hebrew script was altered")
            if unit.get("action") == "preserve":
                if unit["target"] != source_text or not unit.get("reason"):
                    raise ValueError("Preserved unit requires exact original and reason")
            elif unit.get("action") != "translate":
                raise ValueError("Text unit requires translate or preserve action")
            setattr(translated_nodes[ordinal], part, unit["target"])
            visited.add(key)
        if visited != set(unit_targets):
            raise ValueError(f"Unknown, duplicated or immutable source unit in {ident}")

        for left, right in zip(source_nodes, translated_nodes):
            if left.tag != right.tag or left.attrib != right.attrib:
                raise ValueError("Source element or canonical attributes changed")
            if left.tag == TEI + "foreign":
                if "".join(left.itertext()) != "".join(right.itertext()):
                    raise ValueError("Original-language foreign text changed")
            if right.tag == TEI + "ref":
                dest = right.get("target") or ""
                if dest.startswith("#") and dest[1:] not in ids_in_master:
                    raise ValueError(f"Unresolved original target {dest}")

        status = ("complete_unreviewed_draft"
                  if len(visited) == eligible_count else "partial_unreviewed_draft")
        body.append(copy_article)
        report_entries.append({
            "source_key": patch["source_key"],
            "article_id": ident,
            "source_article_sha256": patch["source_article_sha256"],
            "source_position": position_by_id[ident],
            "status": status,
            "translated_or_preserved_units": len(visited),
            "eligible_units": eligible_count,
            "human_reviewed": False,
        })

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(result_root).write(output, encoding="utf-8", xml_declaration=True)
    report = {
        "schema_version": 1,
        "status": "source_locked_draft_excerpt_not_for_publication",
        "source_sha256": SOURCE_SHA256,
        "master_entry_count": SOURCE_COUNT,
        "excerpt_entries": len(report_entries),
        "complete_unreviewed_drafts": sum(
            r["status"] == "complete_unreviewed_draft" for r in report_entries),
        "partial_unreviewed_drafts": sum(
            r["status"] == "partial_unreviewed_draft" for r in report_entries),
        "all_english_canonical_keys_and_ids_unchanged": True,
        "human_reviewed": 0,
        "publication_permitted": False,
        "excerpt_sha256": sha256(output),
        "articles": report_entries,
    }
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--patches", required=True, action="append", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    result = apply(args.source, args.patches, output=args.output,
                   report_path=args.report)
    print(json.dumps({k: v for k, v in result.items() if k != "articles"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
