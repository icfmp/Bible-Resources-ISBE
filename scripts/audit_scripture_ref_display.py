#!/usr/bin/env python3
"""Read-only, source-locked triage of explicit Scripture reference labels.

Checks only unambiguous, single-verse labels against single-verse cRef targets.
It does NOT compare the digital edition against the 1915 printed volumes;
matching metadata cannot certify the historical accuracy of either field.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
SINGLE_TARGET = re.compile(r"^Bible:[A-Za-z0-9]+\\.(\\d+)\\.(\\d+)$")
SINGLE_LABEL = re.compile(r"^\\s*[^\\d\\s][^\\d]*?\\s+(\\d+):(\\d+)\\s*$")


def scan(path):
    path = Path(path)
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    body = root.find(f"./{TEI}text/{TEI}body")
    if root.tag != TEI + "TEI" or body is None:
        raise ValueError("Expected TEI text/body")
    counts = Counter()
    cases = []
    article_count = 0
    for article in body:
        if article.tag != TEI + "div" or not article.get("n") or not article.get(XML_ID):
            raise ValueError("Article identity missing")
        article_count += 1
        for ref in article.iter(TEI + "ref"):
            cref = ref.get("cRef")
            if not cref:
                continue
            counts["references_with_cRef"] += 1
            target = SINGLE_TARGET.fullmatch(cref)
            label = "".join(ref.itertext())
            visible = SINGLE_LABEL.fullmatch(label)
            if not target or not visible:
                counts["unassessed_complex_or_implicit"] += 1
                continue
            counts["explicit_single_verse_assessed"] += 1
            if target.groups() != visible.groups():
                cases.append({
                    "article_key": article.get("n"),
                    "article_xml_id": article.get(XML_ID),
                    "ref_xml_id": ref.get(XML_ID),
                    "visible": label,
                    "cRef": cref,
                    "visible_chapter_verse": list(visible.groups()),
                    "target_chapter_verse": list(target.groups()),
                    "review_status": "candidate_only",
                    "approved_change": False
                })
    return {
        "input_sha256": sha256(raw).hexdigest(),
        "method": "read_only_explicit_single_verse_consistency",
        "scope_limitation": "Digital metadata consistency only; no 1915 print collation or historical certification",
        "articles_scanned": article_count,
        "counts": dict(sorted(counts.items())),
        "candidate_count": len(cases),
        "cases": cases
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("tei", type=Path)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--expected-sha256", default="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25")
    args = p.parse_args()
    result = scan(args.tei)
    if result["input_sha256"] != args.expected_sha256:
        raise SystemExit("Canonical source digest drift")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
