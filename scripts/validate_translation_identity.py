#!/usr/bin/env python3
"""Fail-closed identity/structure parity for translated TEI P5 dictionaries.

The canonical source is the corrected historical English master, not the
CrossWire intermediate and not a modern-English paraphrase. Translation may
change visible prose, but never the canonical entry keys/IDs, anchored
structure, reference targets, or source-language quotations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import zip_longest
from pathlib import Path
import xml.etree.ElementTree as ET

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_body(path):
    root = ET.parse(path).getroot()
    if root.tag != TEI + "TEI":
        raise ValueError("Expected a TEI P5 root")
    if root.find(TEI + "teiHeader") is None:
        raise ValueError("Missing TEI header")
    body = root.find("./" + TEI + "text/" + TEI + "body")
    if body is None:
        raise ValueError("Missing TEI text/body")
    return root, body


def entries(body):
    articles = list(body)
    if not articles:
        raise ValueError("Empty TEI dictionary")
    result = []
    for i, article in enumerate(articles):
        if article.tag != TEI + "div" or article.get("type") != "entry":
            raise ValueError(f"Unexpected top-level article element at {i}")
        article_id, source_key = article.get(XML_ID), article.get("n")
        if not article_id or not source_key:
            raise ValueError(f"Missing canonical article ID or source key at {i}")
        result.append((article_id, source_key))
    if len(set(result)) != len(result):
        raise ValueError("Duplicate canonical article identity")
    if len({a for a, _ in result}) != len(result):
        raise ValueError("Duplicate article xml:id")
    if len({k for _, k in result}) != len(result):
        raise ValueError("Duplicate canonical source key")
    return result


def node_stream(element):
    """Enumerate every source node and its location, not only indexed blocks."""
    stack = [(element, "body")]
    while stack:
        node, location = stack.pop()
        yield node, location
        stack.extend(
            (child, f"{location}/{index}")
            for index, child in reversed(list(enumerate(node)))
        )


def compare(source, translated, *, expected_source_sha256, expected_count,
            target_language):
    if not expected_source_sha256 or len(expected_source_sha256) != 64:
        raise ValueError("A pinned 64-character corrected-English SHA-256 is required")
    actual_source_hash = sha256(source)
    if actual_source_hash != expected_source_sha256:
        raise ValueError("Corrected historical source SHA-256 changed")
    if not target_language or target_language == "en":
        raise ValueError("Translation target must declare a non-English language")

    source_root, source_body = read_body(source)
    target_root, target_body = read_body(translated)
    if source_root.get(XML_LANG) != "en":
        raise ValueError("Canonical source root must declare xml:lang=en")
    if target_root.get(XML_LANG) != target_language:
        raise ValueError("Translation root language does not match target")

    original_index = entries(source_body)
    translated_index = entries(target_body)
    if len(original_index) != expected_count:
        raise ValueError(f"Unexpected corrected source count: {len(original_index)}")
    if translated_index != original_index:
        differing = next(
            (i for i, pair in enumerate(zip_longest(original_index, translated_index))
             if pair[0] != pair[1]), None)
        raise ValueError(f"Translated article ID/key index differs at position {differing}")

    original_ids = set()
    target_ids = set()
    original_nodes = node_stream(source_body)
    target_nodes = node_stream(target_body)
    node_count = 0
    ref_count = 0
    foreign_count = 0
    for original, target in zip_longest(original_nodes, target_nodes):
        if original is None or target is None:
            raise ValueError("Translated TEI structure has added/removed nodes")
        left, path = original
        right, target_path = target
        if path != target_path or left.tag != right.tag:
            raise ValueError(f"TEI element order/type changed at {path}")

        # The entire BODY attribute schema is source-owned: xml:id, n, type,
        # cRef, target, note/section markers and all reference provenance.
        # Only visible element text and tail content may be translated.
        if left.attrib != right.attrib:
            raise ValueError(f"TEI attributes or canonical IDs changed at {path}")

        left_id, right_id = left.get(XML_ID), right.get(XML_ID)
        if left_id:
            if left_id in original_ids:
                raise ValueError(f"Duplicate source xml:id: {left_id}")
            original_ids.add(left_id)
        if right_id:
            if right_id in target_ids:
                raise ValueError(f"Duplicate translated xml:id: {right_id}")
            target_ids.add(right_id)

        if left.tag == TEI + "ref":
            ref_count += 1
        if left.tag == TEI + "foreign":
            foreign_count += 1
            if "".join(left.itertext()) != "".join(right.itertext()):
                raise ValueError(f"Source-language foreign text changed at {path}")
        node_count += 1

    # As well as the structural position test, resolve original internal
    # reference IDs in both corpora. No translation may retarget or dangle one.
    for node, path in node_stream(target_body):
        if node.tag == TEI + "ref" and (node.get("target") or "").startswith("#"):
            if node.get("target")[1:] not in target_ids:
                raise ValueError(f"Dangling canonical internal reference at {path}")

    return {
        "schema_version": 1,
        "status": "cross_language_identity_verified_not_editorially_approved",
        "source_sha256": actual_source_hash,
        "translation_sha256": sha256(translated),
        "source_language": "en",
        "target_language": target_language,
        "article_count": len(original_index),
        "canonical_article_index_identical": True,
        "canonical_source_keys_identical": True,
        "stable_body_xml_ids": len(original_ids),
        "body_elements_compared": node_count,
        "source_references_compared": ref_count,
        "foreign_elements_retained": foreign_count,
        "source_structure_and_attributes_identical": True,
        "translation_editorially_reviewed": False,
        "publication_approved": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--translation", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--expected-count", required=True, type=int)
    parser.add_argument("--target-language", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    report = compare(
        args.source, args.translation,
        expected_source_sha256=args.expected_source_sha256,
        expected_count=args.expected_count,
        target_language=args.target_language)
    output = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
