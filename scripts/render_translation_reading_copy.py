#!/usr/bin/env python3
"""Readable Markdown proof of a fully drafted translated TEI article.

The TEI article and source markup remain the source of truth. This is only a
non-publishable *reading preview*; scripture destinations and original citation
labels are not silently altered or localized by the renderer.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.validate_translation_identity import TEI, XML_ID, entries, read_body

SPACE = re.compile(r"\s+")
ROMAN_HEADING = re.compile(r"^[IVX]+\.\s")


def inline_text(element: ET.Element) -> str:
    """Retain all original/translated inline content in actual document order."""
    return "".join(element.itertext())


def render_article(article: ET.Element, *, draft_status: str) -> str:
    if draft_status != "complete_unreviewed_draft":
        raise ValueError("An incomplete article cannot masquerade as a full French preview")
    lines = []
    title = article.get("n")
    first_head = article.find(TEI + "head")
    if first_head is not None and inline_text(first_head).strip():
        title = inline_text(first_head).strip()
    lines.append("# " + title)
    lines.append("")
    lines.append("*ISBE historique (1915) — traduction française intégrale, brouillon non relu*")
    lines.append("")
    is_first_paragraph = True

    def append_prose(raw: str) -> None:
        nonlocal is_first_paragraph
        prose = SPACE.sub(" ", raw).strip()
        if not prose:
            return
        if is_first_paragraph and len(prose) <= 80 and prose.endswith(":"):
            lines.extend(["*" + prose + "*", ""])
        elif (prose.startswith("I. ") and "VII. " in prose
              and prose.count("II.") >= 1):
            lines.extend(["*Sommaire original : " + prose + "*", ""])
        else:
            lines.extend([prose, ""])
        is_first_paragraph = False

    # Source paragraphs sometimes embed an indexed section <hi> at the END
    # of the preceding prose <p>. Split only *presentation*, never alter XML.
    # Detect semantic numbered headings generically, not by article identity.
    for node in article:
        if node.tag == TEI + "head":
            continue
        if node.tag != TEI + "p":
            raise ValueError("Unknown article block: cannot silently drop source content")
        buffer = node.text or ""
        for child in node:
            content = SPACE.sub(" ", inline_text(child)).strip()
            if (child.tag == TEI + "hi"
                    and (ROMAN_HEADING.match(content)
                         or re.match(r"^[0-9]+\\.\\s", content))):
                append_prose(buffer)
                level = "##" if ROMAN_HEADING.match(content) else "###"
                lines.extend([level + " " + content, ""])
                is_first_paragraph = False
                buffer = child.tail or ""
            else:
                buffer += inline_text(child) + (child.tail or "")
        append_prose(buffer)
    return "\n".join(lines).rstrip() + "\n"


def build(excerpt: Path, report: Path, *, source_key: str) -> str:
    meta = json.loads(Path(report).read_text(encoding="utf-8"))
    if meta.get("publication_permitted") is not False:
        raise ValueError("Reading preview requires a non-publishable source")
    rows = [r for r in meta["articles"] if r["source_key"] == source_key]
    if len(rows) != 1:
        raise ValueError("No unique reported canonical source entry")
    _, body = read_body(excerpt)
    matching = [a for a in body if a.get("n") == source_key]
    if len(matching) != 1 or matching[0].get(XML_ID) != rows[0]["article_id"]:
        raise ValueError("Translation identity changed or excerpt missing")
    return render_article(matching[0], draft_status=rows[0]["status"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--excerpt", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--key", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    text = build(args.excerpt, args.report, source_key=args.key)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(json.dumps({"source_key": args.key,
                      "preview_chars": len(text),
                      "full_article": True,
                      "editorially_reviewed": False,
                      "publication_permitted": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
