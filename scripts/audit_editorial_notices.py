#!/usr/bin/env python3
"""Read-only triage of non-content editorial notices in canonical ISBE TEI.

Patterns locate candidates for human/source-backed classification; they do NOT
authorize deletion. Corpus traversal preserves article and paragraph identity.
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


def scan(path):
    path = Path(path)
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    body = root.find(f"./{T}text/{T}body")
    if root.tag != T + "TEI" or body is None:
        raise ValueError("Expected TEI root and text/body")
    matches = []
    totals = Counter()
    for article in body:
        key, aid = article.get("n"), article.get(ID)
        if article.tag != T + "div" or not key or not aid:
            raise ValueError("Article identity missing")
        for node in article.iter():
            if node.tag not in {T+"p",T+"head",T+"note"}:
                continue
            value = "".join(node.itertext())
            spans = []
            for category, pattern in PATTERNS.items():
                for m in pattern.finditer(value):
                    spans.append({"category":category,"matched_text":m.group(),
                                  "start":m.start(),"end":m.end()})
                    totals[category] += 1
            if not spans:
                continue
            # Entire paragraph is included only as evidence, never to imply
            # that the whole paragraph is a removal candidate.
            matches.append({
                "article_key":key,"article_xml_id":aid,
                "unit_xml_id":node.get(ID),
                "unit_tag":node.tag[len(T):],
                "text_sha256":sha256(value.encode("utf-8")).hexdigest(),
                "text":value,
                "matches":spans,
                "disposition":"unreviewed",
                "remove":False,
            })
    return {
        "input_sha256":sha256(raw).hexdigest(),
        "scan_scope":"TEI article paragraphs, headings and notes (nested included)",
        "method":"candidate-only; no automatic deletions",
        "categories":dict(totals),
        "matching_units":len(matches),
        "cases":matches,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("tei",type=Path)
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--expected-sha256",default="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25")
    a=p.parse_args()
    result=scan(a.tei)
    if result["input_sha256"] != a.expected_sha256:
        raise SystemExit("Unapproved canonical source digest change")
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Matched units:",result["matching_units"])
    print("Matched categories:",json.dumps(result["categories"],sort_keys=True))
    for case in result["cases"]:
        highlights=", ".join(m["matched_text"] for m in case["matches"])
        print(f"  {case['article_key']!r} [{case['unit_xml_id']}]: {highlights}")


if __name__=="__main__":
    main()
