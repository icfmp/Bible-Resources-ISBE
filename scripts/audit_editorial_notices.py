#!/usr/bin/env python3
"""Read-only, source-locked triage of possible non-content ISBE notices.

The lexical profile preserves the reviewed 2026-11-22 scan. The complementary
paratext profile searches for distinctive digital notices and navigation, even
when no general OCR vocabulary is present. A match is only a review candidate:
neither profile authorizes removal or edits the input TEI.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

T = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"

PATTERNS = {
    "digitization_process": re.compile(
        r"(?i)\b(?:scann?ed|digitiz(?:ed|ation)|electronic edition|"
        r"electronic text|OCR|optical character recognition|transcrib(?:ed|er|ers)|"
        r"proofread(?:ing)?|encoded by|markup by)\b"
    ),
    "distribution_or_maintenance": re.compile(
        r"(?i)\b(?:CrossWire|SWORD module|e-?sword|public domain|"
        r"web(?:site|page)|download|copyright notice|"
        r"correction (?:to|of) (?:the )?(?:electronic|digital) (?:text|edition))\b"
    ),
    "editorial_intervention": re.compile(
        r"(?i)(?:\[(?:ed\.|editor(?:'s)? note|transcriber(?:'s)? note)\]|"
        r"\b(?:editor(?:'s)? note|transcriber(?:'s)? note|"
        r"note (?:from|by) (?:the )?(?:editor|transcriber))\b)"
    ),
}

# Target distinctive, independently reviewable site/digital apparatus. These
# patterns never imply that a hit is non-historical, or that its text can go.
PARATEXT_PATTERNS = {
    "web_navigation": re.compile(
        r"(?i)\b(?:popular articles|share tweet save|privacy policy|"
        r"click here|skip to content|"
        r"return to (?:index|homepage)|browse (?:more|all) articles)\b"
    ),
    "digitization_credit": re.compile(
        r"(?i)\b(?:digitized (?:by|for)|scanned (?:by|from)|"
        r"transcribed (?:by|for) (?:this|the) (?:online|digital|electronic)|"
        r"prepared for (?:the )?(?:online|digital) edition|"
        r"OCR (?:performed|corrected)|"
        r"electronic (?:edition|text) (?:prepared|provided) by)\b"
    ),
    "digital_distribution": re.compile(
        r"(?i)\b(?:CrossWire Bible Society|SWORD module|Bible Study Tools|"
        r"copyright statement|transcription copyright|all rights reserved|"
        r"license (?:information|notice)|copy freely|"
        r"permission is granted to copy|last updated)\b"
    ),
    "web_address": re.compile(r"(?i)(?:https?://|www\.)[^\s<>]+"),
}

PROFILES = {
    "lexical": (PATTERNS, {"p", "head", "note"}),
    "paratext": (PARATEXT_PATTERNS, {"p", "head", "note", "item", "ab", "l", "cell", "label"}),
}


def _excerpt(value, limit=160):
    """Compact context only; the full exact source unit is in the JSON report."""
    return " ".join(value.split())[:limit]


def scan(path, profile="lexical"):
    if profile not in PROFILES:
        raise ValueError("Unknown scan profile")
    patterns, tag_names = PROFILES[profile]
    path = Path(path)
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    body = root.find(f"./{T}text/{T}body")
    if root.tag != T + "TEI" or body is None:
        raise ValueError("Expected TEI root and text/body")
    matches = []
    totals = Counter()
    scanned_units = 0
    articles = 0
    for article in body:
        key, aid = article.get("n"), article.get(ID)
        if article.tag != T + "div" or not key or not aid:
            raise ValueError("Article identity missing")
        articles += 1
        units = [node for node in article.iter()
                 if node.tag.startswith(T) and node.tag[len(T):] in tag_names]
        values = ["".join(node.itertext()) for node in units]
        scanned_units += len(units)
        for index, (node, value) in enumerate(zip(units, values)):
            spans = []
            for category, pattern in patterns.items():
                for match in pattern.finditer(value):
                    spans.append({
                        "category": category, "matched_text": match.group(),
                        "start": match.start(), "end": match.end()
                    })
                    totals[category] += 1
            if not spans:
                continue
            row = {
                "article_key": key,
                "article_xml_id": aid,
                "unit_xml_id": node.get(ID),
                "unit_tag": node.tag[len(T):],
                "text_sha256": sha256(value.encode("utf-8")).hexdigest(),
                "text": value,
                "matches": spans,
                "disposition": "unreviewed",
                "remove": False,
            }
            if profile == "paratext":
                # Preserve position and nearby context so a reviewer can tell
                # historical source prose from unrelated digital page furniture.
                row.update({
                    "unit_position_zero_based": index,
                    "unit_count": len(units),
                    "previous_unit_excerpt": _excerpt(values[index-1]) if index else None,
                    "next_unit_excerpt": _excerpt(values[index+1])
                    if index + 1 < len(units) else None,
                })
            matches.append(row)
    return {
        "input_sha256": sha256(raw).hexdigest(),
        "profile": profile,
        "scan_scope": "TEI article text units; lexical profile keeps original p/head/note scope",
        "articles_scanned": articles,
        "units_scanned": scanned_units,
        "method": "candidate-only; no automatic deletions",
        "categories": dict(totals),
        "matching_units": len(matches),
        "cases": matches,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tei", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--profile", choices=sorted(PROFILES), default="lexical")
    parser.add_argument("--print-limit", type=int, default=40)
    parser.add_argument("--expected-sha256",
                        default="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25")
    args = parser.parse_args()
    result = scan(args.tei, args.profile)
    if result["input_sha256"] != args.expected_sha256:
        raise SystemExit("Unapproved canonical source digest change")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print("Profile:", result["profile"])
    print("Scanned articles:", result["articles_scanned"])
    print("Scanned text units:", result["units_scanned"])
    print("Matched units:", result["matching_units"])
    print("Matched categories:", json.dumps(result["categories"], sort_keys=True))
    for case in result["cases"][:max(0, args.print_limit)]:
        highlights = ", ".join(m["matched_text"] for m in case["matches"])
        print(f"  {case['article_key']!r} [{case['unit_xml_id']}]: {highlights}")
        first = case["matches"][0]
        start = max(0, first["start"] - 110)
        stop = min(len(case["text"]), first["end"] + 110)
        print(f"    CONTEXT: {_excerpt(case['text'][start:stop], limit=260)}")
    if result["matching_units"] > args.print_limit:
        print(f"... {result['matching_units'] - max(0, args.print_limit)} additional matches in JSON")


if __name__ == "__main__":
    main()
