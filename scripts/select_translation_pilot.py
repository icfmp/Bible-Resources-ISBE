#!/usr/bin/env python3
"""Source-pinned, deterministic, multilingual ISBE translation pilot roster.

Selections are based on the *corrected historical English* TEI, never on
translated headwords. The output is an audit/translation ledger, not a translated
edition or a distributable SWORD module.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.validate_translation_identity import (
    TEI, XML_ID, read_body, sha256, entries
)

SOURCE_SHA256 = "5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c"
SOURCE_COUNT = 9380
PILOT_COUNT = 50
ANCHORS = (
    "AARON", "ABIDE", "AMNON", "ARK", "ARK OF BULRUSHES",
    "CHORBE", "ELKOSHITE", "GAINSAY", "GRACE", "ZEBIDAH",
)
SLOTS = (("short", 15), ("medium", 10), ("long", 8),
         ("linked", 4), ("structured", 3))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def stable_xml_fingerprint(element):
    """Semantic source-XML fingerprint, independent of serializer prefix choices."""
    def tree(node):
        return [node.tag, sorted(node.attrib.items()), node.text,
                [tree(child) for child in node], node.tail]
    payload = json.dumps(tree(element), ensure_ascii=False,
                         separators=(",", ":")).encode("utf-8")
    return digest(payload)


def greek_or_hebrew(value):
    return any(0x370 <= ord(c) <= 0x3FF for c in value), any(
        0x590 <= ord(c) <= 0x5FF for c in value)


def record_for(article, position):
    key = article.get("n")
    chars = "".join(article.itertext())
    greek, hebrew = greek_or_hebrew(chars)
    ref_nodes = list(article.iter(TEI + "ref"))
    return {
        "source_position": position,
        "source_key": key,
        "article_id": article.get(XML_ID),
        "source_article_sha256": stable_xml_fingerprint(article),
        "text_chars": len(chars),
        "refs": len(ref_nodes),
        "internal_refs": sum(1 for ref in ref_nodes
                             if (ref.get("target") or "").startswith("#")),
        "has_greek": greek,
        "has_hebrew": hebrew,
        "has_nested_div": any(n is not article and n.tag == TEI + "div"
                              for n in article.iter()),
        "has_note": any(n.tag == TEI + "note" for n in article.iter()),
    }


def qualifies(item, bucket):
    length = item["text_chars"]
    return {
        "short": length <= 450,
        "medium": 450 < length <= 2500,
        "long": 2500 < length <= 12000,
        "linked": length <= 6000 and (item["internal_refs"] >= 1 or item["refs"] >= 3),
        "structured": length <= 12000 and (item["has_nested_div"] or item["has_note"]),
    }[bucket]


def select(source, *, expected_sha=SOURCE_SHA256, expected_count=SOURCE_COUNT):
    if sha256(source) != expected_sha:
        raise ValueError("Unexpected historical English source revision")
    root, body = read_body(source)
    source_index = entries(body)
    if len(source_index) != expected_count:
        raise ValueError("Canonical corpus article count changed")
    items = [record_for(article, i) for i, article in enumerate(body)]
    by_key = {row["source_key"]: row for row in items}
    if len(by_key) != len(items):
        raise ValueError("Duplicate article source key")
    missing = sorted(set(ANCHORS) - set(by_key))
    if missing:
        raise ValueError("Attested pilot anchor keys are missing: " + ", ".join(missing))

    chosen = {}
    letters = Counter()

    def add(item, criterion):
        key = item["source_key"]
        if key in chosen:
            return
        selected = dict(item, selection_criterion=criterion,
                        translation_status="pending",
                        editorial_review_status="not_started")
        chosen[key] = selected
        letters[key[:1].upper()] += 1

    for key in ANCHORS:
        add(by_key[key], "source_attested_anchor")

    for bucket, count in SLOTS:
        available = [row for row in items
                     if row["source_key"] not in chosen and qualifies(row, bucket)]
        if len(available) < count:
            raise ValueError(f"Not enough eligible articles in {bucket}")
        for _ in range(count):
            selected = min(
                available,
                key=lambda item: (
                    letters[item["source_key"][:1].upper()],
                    digest((bucket + "|" + item["source_key"]).encode("utf-8")),
                    item["source_key"]))
            add(selected, bucket)
            available.remove(selected)

    if len(chosen) != PILOT_COUNT:
        raise ValueError(f"Unexpected pilot selection count: {len(chosen)}")
    selected = sorted(chosen.values(), key=lambda item: item["source_position"])
    if [(r["article_id"], r["source_key"]) for r in selected] != [
        source_index[r["source_position"]] for r in selected
    ]:
        raise ValueError("Pilot index no longer matches English canonical source")

    return {
        "schema_version": 1,
        "kind": "source_pinned_isbe_translation_pilot",
        "source": "sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml",
        "source_sha256": expected_sha,
        "source_article_count": expected_count,
        "source_work": "ISBE 1915, corrected historical English edition",
        "article_fingerprint_method": "expanded_xml_names_and_complete_tree_v1",
        "translation_language": "fr",
        "pilot_article_count": PILOT_COUNT,
        "index_policy": "original_xml_ids_and_sword_source_keys_shared_by_all_languages",
        "selection_strategy": "attested_examples_and_deterministic_stratified_diversity_v1",
        "status": "selection_only_not_translated",
        "published": False,
        "articles": selected,
        "summary": {
            "article_count": len(selected),
            "selection_criteria": dict(Counter(x["selection_criterion"] for x in selected)),
            "greek_articles": sum(x["has_greek"] for x in selected),
            "hebrew_articles": sum(x["has_hebrew"] for x in selected),
            "internal_link_articles": sum(x["internal_refs"] > 0 for x in selected),
            "structured_articles": sum(x["has_nested_div"] or x["has_note"] for x in selected),
            "pending": len(selected),
            "translated": 0,
            "human_reviewed": 0,
        },
    }


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--print-samples", type=int, default=0,
                        help="Print full text and element nodes of N short selected records for translation drafting")
    args = parser.parse_args()
    result = select(args.source)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(json.dumps({
        "source_sha256": result["source_sha256"],
        "summary": result["summary"],
        "selected": [[r["source_key"], r["article_id"], r["text_chars"],
                      r["selection_criterion"]] for r in result["articles"]],
    }, ensure_ascii=False, indent=2))
    if args.print_samples:
        _, body = read_body(args.source)
        printed = 0
        for selected in result["articles"]:
            if selected["text_chars"] > 450 or printed >= args.print_samples:
                continue
            article = body[selected["source_position"]]
            nodes = []
            for n, element in enumerate(article.iter()):
                if element.text and element.text.strip():
                    nodes.append({"node": n, "tag": element.tag.removeprefix(TEI),
                                  "part": "text", "value": element.text})
                if element.tail and element.tail.strip():
                    nodes.append({"node": n, "tag": element.tag.removeprefix(TEI),
                                  "part": "tail", "value": element.tail})
            print("PILOT_SOURCE_SAMPLE=" + json.dumps({
                "source_key": selected["source_key"],
                "article_id": selected["article_id"],
                "source_article_sha256": selected["source_article_sha256"],
                "nodes": nodes
            }, ensure_ascii=False))
            printed += 1


if __name__ == "__main__":
    run()
