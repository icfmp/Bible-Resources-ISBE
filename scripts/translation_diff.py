#!/usr/bin/env python3
"""Compare two indexed TEI revisions; report changed translation source units.

The comparison uses stable XML IDs and canonical XML bytes for each text block,
so changes to wording, formatting, reference targets or annotations invalidate
only the affected translation units.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "http://www.tei-c.org/ns/1.0"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
BLOCKS = {f"{{{NS}}}{name}" for name in ("p", "head", "ab", "item", "l", "note")}


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def read_tei(path):
    path = Path(path)
    root = ET.parse(path).getroot()
    entries = {}
    for article in root.findall(f".//{{{NS}}}div[@type='entry']"):
        article_id = article.get(XMLID)
        if not article_id or article_id in entries:
            raise ValueError(f"Missing or duplicate article xml:id: {article_id}")
        blocks = {}
        def walk(element):
            if element.tag in BLOCKS:
                sid = element.get(XMLID)
                if not sid or sid in blocks:
                    raise ValueError(f"Missing or duplicate block xml:id: {article_id}/{sid}")
                blocks[sid] = digest(ET.tostring(element, encoding="utf-8"))
                return
            for child in element:
                walk(child)
        for child in article:
            walk(child)
        entries[article_id] = blocks
    if not entries:
        raise ValueError("No indexed TEI entries found")
    return entries


def compare(old, new):
    changes = []
    totals = {k: 0 for k in ("added", "removed", "changed", "unchanged")}
    for article_id in sorted(set(old) | set(new)):
        before, after = old.get(article_id, {}), new.get(article_id, {})
        for sid in sorted(set(before) | set(after)):
            previous, current = before.get(sid), after.get(sid)
            status = ("added" if previous is None else
                      "removed" if current is None else
                      "changed" if previous != current else "unchanged")
            totals[status] += 1
            changes.append({"article_id": article_id, "segment_id": sid,
                            "status": status, "old_hash": previous,
                            "new_hash": current})
    return {"schema_version": 2, "format": "TEI", "totals": totals, "segments": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", required=True, help="Previous modern-English TEI XML file")
    parser.add_argument("--new", required=True, help="New modern-English TEI XML file")
    parser.add_argument("--output", required=True, help="Machine-readable diff report")
    args = parser.parse_args()
    result = compare(read_tei(args.old), read_tei(args.new))
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result["totals"])


if __name__ == "__main__":
    main()
