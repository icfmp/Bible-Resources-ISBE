#!/usr/bin/env python3
"""Apply explicitly sourced French draft units to a 50-entry ISBE pilot.

The full corrected historical English master remains byte-immutable. The
output is a PARTIAL bilingual working excerpt, never a publishable encyclopedia.
Source IDs, original SWORD keys, all other TEI attributes and links survive.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.validate_translation_identity import (
    TEI, XML_ID, XML_LANG, read_body, sha256, entries,
)
from scripts.select_translation_pilot import (
    select, SOURCE_SHA256, SOURCE_COUNT, PILOT_COUNT,
)

# Includes Greek Extended and Hebrew presentation forms, not just basic Greek.
ORIGINAL_SCRIPT = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff\u0590-\u05ff\ufb1d-\ufb4f]+")
SOURCE_WORD = re.compile(r"[^\W\d_]", flags=re.UNICODE)


def script_groups(s):
    return ORIGINAL_SCRIPT.findall(s or "")


def text_units(article):
    """Identify exact UTF-8 text and tails with stable local node ordinals."""
    for number, node in enumerate(article.iter()):
        for part in ("text", "tail"):
            value = getattr(node, part)
            if value and SOURCE_WORD.search(value):
                yield number, node, part, value


def preserve_immutable(node, part):
    """Source-language spans and Scripture locator labels are source-owned."""
    if part != "text":
        return False
    if node.tag == TEI + "foreign":
        return True
    if node.tag == TEI + "ref" and node.get("type") == "scripture":
        return True
    return False


def load_roster(path, source):
    roster = json.loads(Path(path).read_text(encoding="utf-8"))
    if roster["source_sha256"] != SOURCE_SHA256 or roster["translation_language"] != "fr":
        raise ValueError("Pilot roster points to the wrong source or translation language")
    canonical = select(source)
    expected = [
        (row["source_key"], row["article_id"], row["text_chars"],
         row["selection_criterion"])
        for row in canonical["articles"]
    ]
    actual = [
        (row["source_key"], row["article_id"], row["source_text_chars"],
         row["selection_criterion"])
        for row in roster["articles"]
    ]
    if actual != expected or len(actual) != PILOT_COUNT:
        raise ValueError("Published pilot roster differs from selected canonical IDs")
    return roster, canonical


def apply(source, roster_path, patches_path, *, output, report_path):
    source = Path(source)
    roster, canonical = load_roster(roster_path, source)
    patches = json.loads(Path(patches_path).read_text(encoding="utf-8"))
    if patches.get("schema_version") != 1 or patches.get("source_sha256") != SOURCE_SHA256:
        raise ValueError("Translation patches are not pinned to corrected English")
    if patches.get("language") != "fr" or patches.get("status") != "unreviewed_drafts":
        raise ValueError("Translation patch status/language is invalid")
    patch_articles = patches.get("articles", [])
    if len(patch_articles) != len({p["article_id"] for p in patch_articles}):
        raise ValueError("Duplicate translated article ID")

    original_root, original_body = read_body(source)
    if original_root.get(XML_LANG) != "en":
        raise ValueError("Original canonical source must declare English")
    full_index = entries(original_body)
    if len(full_index) != SOURCE_COUNT:
        raise ValueError("Canonical English article count changed")
    full_ids = set()
    for node in original_body.iter():
        identifier = node.get(XML_ID)
        if identifier:
            if identifier in full_ids:
                raise ValueError("Duplicate canonical source XML ID")
            full_ids.add(identifier)

    by_id = {row["article_id"]: row for row in canonical["articles"]}
    for patch in patch_articles:
        if patch["article_id"] not in by_id:
            raise ValueError("Translation patch targets article outside the frozen pilot")
        source_record = by_id[patch["article_id"]]
        if (patch["source_key"] != source_record["source_key"] or
                patch["source_article_sha256"] != source_record["source_article_sha256"]):
            raise ValueError("Translation source article key/hash mismatch")

    ET.register_namespace("", TEI[1:-1])
    root = ET.Element(TEI + "TEI", {XML_LANG: "mul"})  # Draft mixes EN pending with FR drafts
    header = ET.SubElement(root, TEI + "teiHeader")
    fd = ET.SubElement(header, TEI + "fileDesc")
    ts = ET.SubElement(fd, TEI + "titleStmt")
    ET.SubElement(ts, TEI + "title").text = "ISBE 1915 — pilote français partiel non relu"
    ps = ET.SubElement(fd, TEI + "publicationStmt")
    ET.SubElement(ps, TEI + "p").text = "Working bilingual excerpt; not for publication"
    sd = ET.SubElement(fd, TEI + "sourceDesc")
    ET.SubElement(sd, TEI + "p").text = "Corrected historical English ISBE 1915; SHA-256 " + SOURCE_SHA256
    body = ET.SubElement(ET.SubElement(root, TEI + "text"), TEI + "body")

    patches_by_id = {x["article_id"]: x for x in patch_articles}
    article_report = []
    for record in canonical["articles"]:
        original = original_body[record["source_position"]]
        draft = copy.deepcopy(original)
        patch = patches_by_id.get(record["article_id"], {"units": []})
        targets = {}
        for unit in patch.get("units", []):
            ordinal = unit.get("node")
            part = unit.get("part")
            if not isinstance(ordinal, int) or ordinal < 0 or part not in ("text", "tail"):
                raise ValueError("Translation unit requires source node ordinal and text/tail")
            key = (ordinal, part)
            if key in targets:
                raise ValueError("Duplicate translation unit")
            if not isinstance(unit.get("source"), str) or not isinstance(unit.get("target"), str):
                raise ValueError("Translation source and target must be strings")
            if not unit["target"].strip():
                raise ValueError("Translation cannot erase nonempty source text")
            targets[key] = unit

        eligible = 0
        applied = 0
        visited = set()
        for node_index, node, part, source_text in text_units(original):
            translated_node = list(draft.iter())[node_index]
            if preserve_immutable(node, part):
                if (node_index, part) in targets:
                    raise ValueError("Scripture reference or source-language text must not be patched")
                continue
            eligible += 1
            key = (node_index, part)
            if key not in targets:
                continue
            unit = targets[key]
            if unit["source"] != source_text:
                raise ValueError(f"Source text mismatch in {record['source_key']} at {key}")
            if script_groups(source_text) != script_groups(unit["target"]):
                raise ValueError("Original Greek/Hebrew script spans were changed")
            if unit.get("action") == "preserve":
                if unit["target"] != source_text or not unit.get("reason"):
                    raise ValueError("Preserved source units need an exact copy and reason")
            elif unit.get("action") != "translate":
                raise ValueError("Translation unit action must be translate or preserve")
            setattr(translated_node, part, unit["target"])
            visited.add(key)
            applied += 1

        if len(visited) != len(targets):
            raise ValueError(f"Unknown/nontranslatable translation unit in {record['source_key']}")

        for old, new in zip(original.iter(), draft.iter()):
            if old.tag != new.tag or old.attrib != new.attrib:
                raise ValueError("Translation damaged canonical TEI structure/attributes")
            if old.tag == TEI + "foreign" and "".join(old.itertext()) != "".join(new.itertext()):
                raise ValueError("Historical source-language element was changed")
            ref = new if new.tag == TEI + "ref" else None
            if ref is not None and (ref.get("target") or "").startswith("#"):
                if ref.get("target")[1:] not in full_ids:
                    raise ValueError("Unresolved canonical link in translated pilot")
        if len(list(original.iter())) != len(list(draft.iter())):
            raise ValueError("Translation lost source nodes")

        if not patch.get("units"):
            status = "pending"
        elif applied != eligible:
            status = "partial_unreviewed_draft"
        else:
            status = "complete_unreviewed_draft"
        body.append(draft)
        article_report.append({
            "source_key": record["source_key"],
            "article_id": record["article_id"],
            "source_article_sha256": record["source_article_sha256"],
            "translation_status": status,
            "translated_units": applied,
            "eligible_units": eligible,
            "reviewed_by_human": False,
        })

    output = Path(output)
    report_path = Path(report_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)
    complete_drafts = all(
        record["translation_status"] == "complete_unreviewed_draft"
        for record in article_report
    )
    result = {
        "schema_version": 1,
        "status": ("all_pilot_drafts_complete_unreviewed_not_for_publication"
                   if complete_drafts else "partial_bilingual_pilot_not_for_publication"),
        "source_sha256": SOURCE_SHA256,
        "draft_tei_sha256": sha256(output),
        "pilot_article_count": PILOT_COUNT,
        "canonical_article_index_preserved": True,
        "unreviewed_drafts": sum(x["translation_status"].endswith("_draft") for x in article_report),
        "pending": sum(x["translation_status"] == "pending" for x in article_report),
        "human_reviewed": 0,
        "publication_permitted": False,
        "articles": article_report,
    }
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--roster", required=True)
    parser.add_argument("--patches", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    result = apply(args.source, args.roster, args.patches,
                   output=args.output, report_path=args.report)
    print(json.dumps({k: v for k, v in result.items() if k != "articles"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
