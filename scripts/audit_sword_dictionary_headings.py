#!/usr/bin/env python3
"""Audit source title/headword identity without editing TEI or assuming GUI behavior.

A dictionary GUI may show the article key as a navigation heading *and* the
source's own TEI <head> as article content. Matching strings do not establish
duplicate source text. This tool only inventories direct source headings,
enforces title parity across the non-destructive SWORD adapter, and records
a few reproducible examples for visual inspection.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

TEI = "{http://www.tei-c.org/ns/1.0}"

def sha(path):
    h = sha256()
    with Path(path).open("rb") as inp:
        for part in iter(lambda: inp.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()

def entries(path, tag, require_type=None):
    root = ET.parse(path).getroot()
    body = root.find("./" + TEI + "text/" + TEI + "body")
    if body is None:
        raise ValueError("Missing TEI dictionary body")
    result = {}
    for index, entry in enumerate(body):
        key = entry.get("n")
        if entry.tag != TEI + tag or not key or key in result:
            raise ValueError(f"Wrong entry wrapper or duplicate/missing key at {index}")
        if require_type and entry.get("type") != require_type:
            raise ValueError(f"Unexpected entry type at {index}")
        result[key] = entry
    return result

def heads(entry):
    # Intentional direct children only: nested <head> elements describe
    # sections of an article, not its first-level dictionary title.
    return tuple("".join(node.itertext()) for node in entry if node.tag == TEI + "head")

def normalized(value):
    return " ".join(value.split())

def analyze(source_path, adapted_path, report_path, samples=("AARON", "GRACE", "AALAR")):
    source = entries(source_path, "div", "entry")
    adapted = entries(adapted_path, "entryFree")
    if source.keys() != adapted.keys():
        raise ValueError("Source/adapter article keys changed")
    result = {
        "schema_version": 1,
        "audit_scope": "dictionary key versus direct TEI head (not a GUI click or visual certification)",
        "source_sha256": sha(source_path),
        "adapted_sha256": sha(adapted_path),
        "article_count": len(source),
        "direct_heading_present_count": 0,
        "direct_heading_absent_count": 0,
        "multiple_direct_heading_count": 0,
        "first_direct_heading_equals_key_exact_count": 0,
        "first_direct_heading_equals_key_whitespace_normalized_count": 0,
        "direct_headings_changed_by_adapter_count": 0,
        "sample_articles": {},
        "original_source_modified": False,
        "editorial_corrections_applied": False,
        "gui_duplicate_title_verified": False,
        "requires_reader_visual_review": True,
        "interpretation": (
            "A source <head> equal to the dictionary entry key can appear twice "
            "when a reader displays its own key label plus the original heading; "
            "this is not evidence of duplicated source paragraphs and must not "
            "trigger automatic heading deletion."
        ),
    }
    for key, entry in source.items():
        a = heads(entry)
        b = heads(adapted[key])
        if a != b:
            raise ValueError(f"Direct heading changed by SWORD adapter: {key}")
        if a:
            result["direct_heading_present_count"] += 1
            if len(a) > 1:
                result["multiple_direct_heading_count"] += 1
            if a[0] == key:
                result["first_direct_heading_equals_key_exact_count"] += 1
            if normalized(a[0]) == normalized(key):
                result["first_direct_heading_equals_key_whitespace_normalized_count"] += 1
        else:
            result["direct_heading_absent_count"] += 1
        if key in samples:
            result["sample_articles"][key] = {
                "source_key": key,
                "direct_headings": list(a),
                "first_heading_matches_key_exact": bool(a and a[0] == key),
                "adapter_direct_heading_parity": True,
            }
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--adapted", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    result = analyze(args.source, args.adapted, args.report)
    print(json.dumps({k: v for k, v in result.items()
                      if k != "sample_articles"}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
