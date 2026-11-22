#!/usr/bin/env python3
"""Inventory source-derived empty ISBE paragraphs without editing canonical TEI.

This is an editorial triage tool, not a print-witness comparison or permission
to discard source material. Its report is deterministically ordered and bound
to the exact input bytes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def excerpt(element, limit=180):
    if element is None:
        return None
    value = "".join(element.itertext()).strip()
    return value[:limit] + ("…" if len(value) > limit else "")


def inventory(path):
    path = Path(path)
    data = path.read_bytes()
    root = ET.fromstring(data)
    body = root.find(f"./{TEI}text/{TEI}body")
    if root.tag != f"{TEI}TEI" or body is None:
        raise ValueError("Expected a namespaced TEI/text/body document")

    cases = []
    for article in body:
        if article.tag != f"{TEI}div" or article.get("type") != "entry":
            raise ValueError("Unexpected top-level TEI article")
        key = article.get("n")
        article_id = article.get(XML_ID)
        if not key or not article_id:
            raise ValueError("Article lacks source key or stable ID")
        # Nested bibliography divisions have paragraphs too: traverse all
        # descendants, but use their document order and preserve stable IDs.
        elements = list(article.iter())
        for position, node in enumerate(elements):
            if node.tag != f"{TEI}p":
                continue
            if node.text is not None and node.text.strip():
                continue
            if len(node):
                continue  # no claim about mixed-content paragraphs
            if node.get(XML_ID) is None:
                raise ValueError(f"Empty paragraph lacks stable ID in {key}")
            previous = next(
                (candidate for candidate in reversed(elements[:position])
                 if candidate.tag in {f"{TEI}p", f"{TEI}head"}), None
            )
            following = next(
                (candidate for candidate in elements[position + 1:]
                 if candidate.tag in {f"{TEI}p", f"{TEI}head"}), None
            )
            cases.append({
                "article_key": key,
                "article_xml_id": article_id,
                "paragraph_xml_id": node.get(XML_ID),
                "article_node_position": position,
                "raw_text": node.text,
                "attributes": {k: v for k, v in node.attrib.items() if k != XML_ID},
                "previous_xml_id": previous.get(XML_ID) if previous is not None else None,
                "previous_text_excerpt": excerpt(previous),
                "next_xml_id": following.get(XML_ID) if following is not None else None,
                "next_text_excerpt": excerpt(following),
                "review_status": "unreviewed_source_empty",
                "print_witness": None,
                "editorial_decision": None,
            })
    return {
        "input": str(path),
        "source_xml_sha256": hashlib.sha256(data).hexdigest(),
        "definition": "TEI p without children and without non-whitespace p.text",
        "count": len(cases),
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tei", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, default=31)
    args = parser.parse_args()
    report = inventory(args.tei)
    if report["count"] != args.expected_count:
        raise SystemExit(
            f"Empty paragraph count changed: {report['count']} != {args.expected_count}"
        )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Documented {report['count']} untouched source-derived empty paragraphs")
    for case in report["cases"]:
        print(f"  {case['article_key']!r}: {case['paragraph_xml_id']}")
        print(f"    BEFORE: {case['previous_text_excerpt']!r}")
        print(f"    AFTER:  {case['next_text_excerpt']!r}")


if __name__ == "__main__":
    main()
