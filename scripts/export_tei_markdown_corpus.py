#!/usr/bin/env python3
"""Archive every canonical TEI article as readable Markdown plus lossless source maps.

This is a reusable editorial workspace, NOT a new canonical translation format.
The corrected TEI remains authoritative. French reading copies are optional
source-locked, unreviewed derivatives of the existing patches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.apply_translation_batches import apply
from scripts.render_translation_reading_copy import render_article
from scripts.select_translation_pilot import (
    SOURCE_COUNT, SOURCE_SHA256, stable_xml_fingerprint,
)
from scripts.validate_translation_identity import (
    TEI, XML_ID, XML_LANG, entries, read_body, sha256,
)

SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")
SPACE = re.compile(r"\\s+")
ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def compact(text: str) -> str:
    return SPACE.sub(" ", text).strip()


def original_nodes(article: ET.Element) -> list[dict]:
    """Lossless, ordered per-node inventory: tag, attrs, text AND tail."""
    result: list[dict] = []

    def walk(node: ET.Element, parent: int | None) -> None:
        number = len(result)
        result.append({
            "ordinal": number,
            "parent": parent,
            "tag": node.tag,
            "attributes": dict(node.attrib),
            "text": node.text,
            "tail": node.tail,
        })
        for child in node:
            walk(child, number)

    walk(article, None)
    return result


def reassemble_nodes(nodes: list[dict]) -> ET.Element:
    """Recreate the exact ElementTree content without guessing structure."""
    made: list[ET.Element] = []
    for i, record in enumerate(nodes):
        if record["ordinal"] != i:
            raise ValueError("Node ordinals are not contiguous")
        node = ET.Element(record["tag"], record["attributes"])
        node.text, node.tail = record["text"], record["tail"]
        parent = record["parent"]
        if parent is None:
            if i != 0:
                raise ValueError("Multiple roots in source map")
        elif not isinstance(parent, int) or not (0 <= parent < i):
            raise ValueError("Invalid source-node parent")
        else:
            made[parent].append(node)
        made.append(node)
    if not made:
        raise ValueError("Empty article source map")
    return made[0]


def original_markdown(article: ET.Element, *, source_digest: str) -> str:
    """Readable English presentation; every structural detail is in JSON."""
    first_head = article.find(TEI + "head")
    title = compact("".join(first_head.itertext())) if first_head is not None else article.get("n")
    lines = [
        "# " + (title or article.get("n") or "Untitled"),
        "",
        "<!-- Historical English source, not a translation. -->",
        "<!-- Canonical SWORD key and identifiers are in the paired JSON map. -->",
        "<!-- Source article SHA-256: " + source_digest + " -->",
        "",
    ]

    def add(value: str, prefix: str = "") -> None:
        value = compact(value)
        if value:
            lines.extend([prefix + value, ""])

    def render_blocks(node: ET.Element, depth: int) -> None:
        if node.text and node.text.strip():
            add(node.text)
        for child in node:
            name = child.tag.removeprefix(TEI)
            if child is first_head:
                continue
            if name == "div":
                render_blocks(child, depth + 1)
            elif name == "head":
                add("".join(child.itertext()), "#" * min(6, depth + 2) + " ")
            elif name == "list":
                if child.text and child.text.strip():
                    add(child.text)
                for item in child:
                    if item.tag == TEI + "item":
                        add("".join(item.itertext()), "- ")
                    else:
                        add("".join(item.itertext()))
                    if item.tail and item.tail.strip():
                        add(item.tail)
            elif name == "lg":
                for line in child:
                    if line.tag == TEI + "l":
                        add("".join(line.itertext()), "    ")
                    else:
                        add("".join(line.itertext()))
            elif name == "quote":
                add("".join(child.itertext()), "> ")
            else:
                # Fallback is *visible*, never silently discard unknown blocks.
                add("".join(child.itertext()))
            if child.tail and child.tail.strip():
                add(child.tail)

    render_blocks(article, 0)
    return "\n".join(lines).rstrip() + "\n"


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def store(archive: zipfile.ZipFile, path: str, payload: bytes | str) -> str:
    raw = payload.encode("utf-8") if isinstance(payload, str) else payload
    info = zipfile.ZipInfo(path, date_time=ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, raw)
    return digest(raw)


def export(source: Path, output: Path, *, report: Path,
           patches: list[Path] | None = None,
           expected_sha: str = SOURCE_SHA256,
           expected_count: int = SOURCE_COUNT) -> dict:
    """Create deterministic reusable EN source corpus + optional FR draft previews."""
    source, output, report = Path(source), Path(output), Path(report)
    if sha256(source) != expected_sha:
        raise ValueError("Refusing an unpinned or modified TEI source")
    root, body = read_body(source)
    if root.get(XML_LANG) != "en":
        raise ValueError("Expected an English canonical source")
    canonical = entries(body)
    if len(canonical) != expected_count:
        raise ValueError("Canonical article count mismatch")
    all_ids: set[str] = set()
    for node in body.iter():
        identifier = node.get(XML_ID)
        if identifier:
            if identifier in all_ids:
                raise ValueError("Duplicate TEI xml:id: " + identifier)
            all_ids.add(identifier)

    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    english_rows: list[dict] = []
    french_rows: list[dict] = []

    with tempfile.TemporaryDirectory() as scratch:
        staging = Path(scratch)
        archive_path = staging / "workspace.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=8, allowZip64=True) as archive:
            store(archive, "README.md", (
                "# ISBE 1915 — multilingual editorial Markdown workspace\n\n"
                "English files under `en/articles/` are **read-only derived views** "
                "of the corrected historical TEI. Each `en/maps/` JSON sidecar "
                "retains the COMPLETE source element tree, attributes, text and tails "
                "with stable preorder node ordinals. Markdown is not a replacement for "
                "TEI, and Markdown edits alone cannot be reimported safely.\n\n"
                "Always make translations through source-locked exact-unit patches "
                "and validate reconstruction against the immutable English TEI. "
                "The original SWORD keys, xml:id values, Hebrew/Greek, references, "
                "citation targets and notes must never be silently altered.\n\n"
                "Optional `fr/unreviewed/` files are generated reading proofs "
                "from existing French patches: **not independently editorially "
                "approved, not a complete French edition, not for publication**.\n\n"
                "See MANIFEST.json for exact SHA-256, source-index order, "
                "article checksums and completeness counts.\n"
            ))
            index_lines = [
                "# ISBE 1915 — English article index", "",
                "Derived readable views; original English TEI remains authoritative.", "",
                "| Original position | Canonical key | Stable ID |",
                "| ---: | --- | --- |",
            ]
            for position, article in enumerate(body):
                identifier, key = canonical[position]
                if not SAFE_ID.fullmatch(identifier):
                    raise ValueError("Unsafe canonical xml:id filename: " + identifier)
                fingerprint = stable_xml_fingerprint(article)
                nodes = original_nodes(article)
                if stable_xml_fingerprint(reassemble_nodes(nodes)) != fingerprint:
                    raise ValueError("Lossy TEI source map: " + key)
                base = "en/articles/" + identifier + ".md"
                map_path = "en/maps/" + identifier + ".json"
                text = original_markdown(article, source_digest=fingerprint)
                map_data = {
                    "schema_version": 1,
                    "kind": "lossless_original_tei_article_source_map",
                    "source_sha256": expected_sha,
                    "source_key": key,
                    "article_id": identifier,
                    "source_position": position,
                    "source_article_sha256": fingerprint,
                    "translation_status": "original_english_only",
                    "nodes": nodes,
                }
                md_hash = store(archive, base, text)
                map_hash = store(archive, map_path, json_bytes(map_data))
                english_rows.append({
                    "source_position": position,
                    "source_key": key,
                    "article_id": identifier,
                    "source_article_sha256": fingerprint,
                    "markdown": base,
                    "markdown_sha256": md_hash,
                    "source_map": map_path,
                    "source_map_sha256": map_hash,
                    "source_nodes": len(nodes),
                })
                index_lines.append(
                    f"| {position + 1} | [{key.replace('|', '&#124;')}]({base}) "
                    f"| `{identifier}` |"
                )
            store(archive, "en/INDEX.md", "\n".join(index_lines) + "\n")

            if patches:
                excerpt, excerpt_report = staging / "fr.xml", staging / "fr-report.json"
                result = apply(source, list(patches), output=excerpt,
                               report_path=excerpt_report)
                if (result["partial_unreviewed_drafts"] != 0
                        or result["complete_unreviewed_drafts"] != result["excerpt_entries"]
                        or result["publication_permitted"] is not False):
                    raise ValueError("French source-locked drafts are incomplete or publishable")
                by_id = {r["article_id"]: r for r in result["articles"]}
                _, fr_body = read_body(excerpt)
                fr_index = [
                    "# ISBE 1915 — French draft reading copies", "",
                    "Generated from source-locked patches. Editorial approval: **none**.", "",
                ]
                for article in fr_body:
                    identifier = article.get(XML_ID)
                    row = by_id[identifier]
                    md_path = "fr/unreviewed/" + identifier + ".md"
                    md = render_article(article, draft_status=row["status"])
                    md_hash = store(archive, md_path, md)
                    french_rows.append({
                        "article_id": identifier,
                        "source_key": row["source_key"],
                        "source_article_sha256": row["source_article_sha256"],
                        "status": row["status"],
                        "editorially_approved": False,
                        "markdown": md_path,
                        "markdown_sha256": md_hash,
                    })
                    fr_index.append(f"- [{row['source_key']}]({md_path})")
                if len(french_rows) != len(by_id):
                    raise ValueError("French draft count differs from validated reconstruction")
                store(archive, "fr/INDEX.md", "\n".join(fr_index) + "\n")

            manifest = {
                "schema_version": 1,
                "kind": "reusable_source_locked_isbe_markdown_workspace",
                "canonical_source": "sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml",
                "source_sha256": expected_sha,
                "source_language": "en",
                "canonical_article_count": len(english_rows),
                "source_maps_lossless": True,
                "translation_source_of_truth": "original_pinned_english_tei",
                "french_unreviewed_draft_count": len(french_rows),
                "human_editorial_approvals": 0,
                "publication_permitted": False,
                "articles": english_rows,
                "french_drafts": french_rows,
            }
            store(archive, "MANIFEST.json", json_bytes(manifest))
        output.write_bytes(archive_path.read_bytes())
    summary = {
        "source_sha256": expected_sha,
        "canonical_article_count": len(english_rows),
        "lossless_source_maps": len(english_rows),
        "french_unreviewed_drafts": len(french_rows),
        "human_editorial_approvals": 0,
        "publication_permitted": False,
        "archive_sha256": sha256(output),
        "archive_bytes": output.stat().st_size,
    }
    report.write_bytes(json_bytes(summary))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--patches", type=Path, action="append", default=[])
    parser.add_argument("--expected-sha", default=SOURCE_SHA256)
    parser.add_argument("--expected-count", type=int, default=SOURCE_COUNT)
    args = parser.parse_args()
    print(json.dumps(export(args.source, args.output, report=args.report,
                            patches=args.patches, expected_sha=args.expected_sha,
                            expected_count=args.expected_count),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
