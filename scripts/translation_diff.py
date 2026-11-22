#!/usr/bin/env python3
"""Compare two modern-English article trees at stable segment granularity.

Input: one JSON file per article; each document contains id and segments
(with unique ids and text fields). Output is deterministic JSON. This
compares immutable snapshots and never changes source files.
"""
import argparse
import hashlib
import json
from pathlib import Path


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_tree(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    articles = {}
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        article_id = data["id"]
        if not isinstance(article_id, str) or not article_id:
            raise ValueError(f"Invalid article id in {path}")
        if article_id in articles:
            raise ValueError(f"Duplicate article id: {article_id}")
        segments = {}
        for seg in data["segments"]:
            sid, txt = seg["id"], seg["text"]
            if not isinstance(sid, str) or not sid or not isinstance(txt, str):
                raise ValueError(f"Invalid segment in {path}")
            if sid in segments:
                raise ValueError(f"Duplicate segment id {article_id}/{sid}")
            segments[sid] = digest(txt)
        articles[article_id] = segments
    return articles


def compare(old, new):
    changes = []
    totals = {k: 0 for k in ("added", "removed", "changed", "unchanged")}
    for article_id in sorted(set(old) | set(new)):
        before, after = old.get(article_id, {}), new.get(article_id, {})
        for sid in sorted(set(before) | set(after)):
            previous, current = before.get(sid), after.get(sid)
            if previous is None:
                status = "added"
            elif current is None:
                status = "removed"
            elif previous != current:
                status = "changed"
            else:
                status = "unchanged"
            totals[status] += 1
            changes.append({"article_id": article_id, "segment_id": sid,
                            "status": status, "old_hash": previous,
                            "new_hash": current})
    return {"schema_version": 1, "totals": totals, "segments": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", required=True, help="Old modern-English snapshot")
    parser.add_argument("--new", required=True, help="New modern-English snapshot")
    parser.add_argument("--output", required=True, help="Report JSON path")
    args = parser.parse_args()
    report = compare(read_tree(args.old), read_tree(args.new))
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(f"Compared segments: {report['totals']}")


if __name__ == "__main__":
    main()
