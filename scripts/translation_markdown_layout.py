#!/usr/bin/env python3
"""Deterministic source-attested Markdown layout for a canonical TEI article.

Use the existing ISBE 1915 archive's English Markdown and lossless TEI maps.
Paragraphs stay readable; original inline references/markup become protected
markers so they cannot be dropped by a translator.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.apply_translation_pilot import preserve_immutable
from scripts.export_tei_markdown_corpus import reassemble_nodes
from scripts.select_translation_pilot import SOURCE_SHA256, stable_xml_fingerprint
from scripts.validate_translation_identity import TEI, XML_ID

HEADER = "<!-- ISBE-TRANSLATION-V1 "
HEADER_END = " -->\n\n"
BLOCK_START = "<!-- ISBE-BLOCK:"
BLOCK_END = "<!-- ISBE-END:"
MARK = re.compile(r"(⟦ISBE:[^⟦⟧]*⟧)")
BLOCK = re.compile(
    r"<!-- ISBE-BLOCK:([0-9]+) -->\n(.*?)\n<!-- ISBE-END:\\1 -->\n",
    flags=re.DOTALL,
)
SOURCE_WORD = re.compile(r"[^\W\d_]", re.UNICODE)
CONTAINERS = {"div", "list", "lg"}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def readable_label(node: ET.Element) -> str:
    content = " ".join("".join(node.itertext()).split())
    if not content or "⟦" in content or "⟧" in content or "\n" in content:
        return ""
    return content if len(content) <= 64 else content[:61] + "…"


def load_article(archive_path: Path, source_key: str, *,
                 expected_sha: str = SOURCE_SHA256) -> tuple[dict, ET.Element]:
    """Reject changed Markdown, source maps, canonical identities and SHA."""
    with zipfile.ZipFile(archive_path) as archive:
        manifest = json.loads(archive.read("MANIFEST.json"))
        if (manifest.get("schema_version") != 1
                or manifest.get("kind") != "reusable_source_locked_isbe_markdown_workspace"
                or manifest.get("source_sha256") != expected_sha
                or manifest.get("source_language") != "en"
                or manifest.get("publication_permitted") is not False):
            raise ValueError("Untrusted archive or canonical English source revision")
        matches = [r for r in manifest.get("articles", [])
                   if r.get("source_key") == source_key]
        if len(matches) != 1:
            raise ValueError("No unique source key in the Markdown archive")
        row = matches[0]
        ident = row["article_id"]
        if (row.get("markdown") != f"en/articles/{ident}.md"
                or row.get("source_map") != f"en/maps/{ident}.json"):
            raise ValueError("Unexpected canonical article archive filename")
        raw_md = archive.read(row["markdown"])
        raw_map = archive.read(row["source_map"])
        if (digest(raw_md) != row["markdown_sha256"]
                or digest(raw_map) != row["source_map_sha256"]):
            raise ValueError("English Markdown or source map checksum mismatch")
        mapping = json.loads(raw_map)
    if (mapping.get("schema_version") != 1
            or mapping.get("kind") != "lossless_original_tei_article_source_map"
            or mapping.get("source_sha256") != expected_sha
            or mapping.get("source_key") != source_key
            or mapping.get("article_id") != ident
            or mapping.get("source_position") != row["source_position"]
            or mapping.get("source_article_sha256") != row["source_article_sha256"]):
        raise ValueError("Canonical source map metadata does not match the archive")
    article = reassemble_nodes(mapping["nodes"])
    if (article.tag != TEI + "div"
            or article.get("type") != "entry"
            or article.get(XML_ID) != ident
            or article.get("n") != source_key
            or stable_xml_fingerprint(article) != row["source_article_sha256"]):
        raise ValueError("Altered TEI source map, canonical ID or article fingerprint")
    return row, article


def build_blocks(article: ET.Element) -> list[dict]:
    """Produce paragraph-sized units with exact TEI inline boundary markers."""
    order = {id(node): number for number, node in enumerate(article.iter())}
    blocks: list[dict] = []

    def part(node: ET.Element, field: str,
             output: list[tuple[str, object]]) -> None:
        value = getattr(node, field)
        if not value:
            return
        ordinal = order[id(node)]
        if SOURCE_WORD.search(value) and not preserve_immutable(node, field):
            output.append(("slot", (ordinal, field, value)))
        elif value.strip():
            # Punctuation-only text is not editable in the current patch schema.
            output.append(("marker", f"⟦ISBE:FIX:{ordinal}:{field}⟧"))

    def inline(node: ET.Element, output: list[tuple[str, object]]) -> None:
        part(node, "text", output)
        for child in node:
            ordinal = order[id(child)]
            if preserve_immutable(child, "text"):
                if len(child):
                    raise ValueError("Nested immutable source text needs manual mapping")
                output.append(("marker", f"⟦ISBE:KEEP:{ordinal}:{readable_label(child)}⟧"))
            else:
                output.append(("marker", f"⟦ISBE:OPEN:{ordinal}⟧"))
                inline(child, output)
                output.append(("marker", f"⟦ISBE:CLOSE:{ordinal}⟧"))
            part(child, "tail", output)

    def walk(node: ET.Element, *, root: bool = False) -> None:
        tag = node.tag.removeprefix(TEI)
        if root or tag in CONTAINERS:
            if (node.text or "").strip():
                raise ValueError("Unexpected prose inside structural TEI container")
            for child in node:
                walk(child)
                if (child.tail or "").strip():
                    raise ValueError("Unexpected prose after structural TEI child")
            return
        parts: list[tuple[str, object]] = []
        inline(node, parts)
        for left, right in zip(parts, parts[1:]):
            if left[0] == right[0] == "slot":
                raise ValueError("Adjacent source text units have ambiguous boundaries")
        prefix = ("# " if node is article.find(TEI + "head")
                  else "## " if tag == "head" else "")
        body = prefix + "".join(
            value[2] if kind == "slot" else value
            for kind, value in parts
        )
        blocks.append({
            "id": order[id(node)],
            "tag": tag,
            "prefix": prefix,
            "parts": parts,
            "source": body,
        })

    walk(article, root=True)
    if not blocks:
        raise ValueError("No original TEI blocks available for translation")
    return blocks


def metadata(row: dict, *, source_sha: str = SOURCE_SHA256) -> dict:
    return {
        "schema_version": 1,
        "source_key": row["source_key"],
        "article_id": row["article_id"],
        "source_sha256": source_sha,
        "source_article_sha256": row["source_article_sha256"],
        "language": "fr",
        "status": "unreviewed_drafts",
        "publication_permitted": False,
        "preserve": {},
    }


def template(archive_path: Path, source_key: str, *,
             expected_sha: str = SOURCE_SHA256) -> str:
    row, article = load_article(archive_path, source_key, expected_sha=expected_sha)
    header = metadata(row, source_sha=expected_sha)
    result = [HEADER + json.dumps(header, ensure_ascii=False, sort_keys=True)
              + HEADER_END]
    for block in build_blocks(article):
        result.extend([
            f"{BLOCK_START}{block['id']} -->\n",
            block["source"],
            f"\n{BLOCK_END}{block['id']} -->\n\n",
        ])
    return "".join(result)


def read_draft(markdown: str) -> tuple[dict, list[tuple[int, str]]]:
    if not markdown.startswith(HEADER):
        raise ValueError("Missing original article translation metadata")
    end = markdown.find(HEADER_END)
    if end < 0:
        raise ValueError("Malformed translation metadata")
    try:
        head = json.loads(markdown[len(HEADER):end])
    except json.JSONDecodeError as exc:
        raise ValueError("Malformed source identity JSON") from exc
    content = markdown[end + len(HEADER_END):]
    position = 0
    blocks = []
    for match in BLOCK.finditer(content):
        if content[position:match.start()].strip():
            raise ValueError("Unexpected content outside original TEI block")
        blocks.append((int(match.group(1)), match.group(2)))
        position = match.end()
    if content[position:].strip():
        raise ValueError("Unrecognized, missing or truncated TEI block marker")
    return head, blocks
