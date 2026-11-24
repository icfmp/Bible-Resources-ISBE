#!/usr/bin/env python3
"""Export bounded, source-attested TEI translation units using canonical IDs.

This is a read-only, reusable editorial extraction tool. It never changes the
English master, writes translations, or confers publication/review approval.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.apply_translation_pilot import text_units, preserve_immutable
from scripts.select_translation_pilot import (
    SOURCE_COUNT, SOURCE_SHA256, stable_xml_fingerprint,
)
from scripts.validate_translation_identity import (
    TEI, XML_ID, entries, read_body, sha256,
)


def extract(source: Path, keys: list[str], *, start: int = 0, limit: int = 100,
            expected_sha: str = SOURCE_SHA256) -> list[dict]:
    if sha256(source) != expected_sha:
        raise ValueError("Corrected historical English master hash mismatch")
    _, body = read_body(source)
    index = entries(body)
    if len(index) != SOURCE_COUNT:
        raise ValueError("Unexpected original English entry count")
    if not keys or len(set(keys)) != len(keys):
        raise ValueError("Unique source keys are required")
    if start < 0 or limit <= 0 or limit > 200:
        raise ValueError("Invalid bounded source unit window")
    by_key = {article.get("n"): (i, article) for i, article in enumerate(body)}
    unknown = sorted(set(keys) - set(by_key))
    if unknown:
        raise ValueError("Unknown original canonical keys: " + repr(unknown))
    rows = []
    for key in keys:
        source_position, article = by_key[key]
        units = list(text_units(article))
        rows.append({
            "source_key": key,
            "article_id": article.get(XML_ID),
            "source_article_sha256": stable_xml_fingerprint(article),
            "source_position": source_position,
            "source_text_chars": len("".join(article.itertext())),
            "unit_count": len(units),
            "start": start,
            "limit": limit,
            "units": [{
                "node": ordinal,
                "part": part,
                "tag": node.tag.removeprefix(TEI),
                "source": value,
                "immutable": preserve_immutable(node, part),
                "xml_id": node.get(XML_ID),
            } for ordinal, node, part, value in units[start:start + limit]],
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--key", action="append", dest="keys", required=True,
                        help="Exact original English @n; repeat as needed")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", type=Path,
                        help="Write UTF-8 JSON instead of log lines")
    args = parser.parse_args()
    rows = extract(args.source, args.keys, start=args.start, limit=args.limit)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    else:
        for row in rows:
            meta = {k: v for k, v in row.items() if k != "units"}
            print("ISBE_SOURCE_ARTICLE=" + json.dumps(meta, ensure_ascii=False))
            for unit in row["units"]:
                print("ISBE_SOURCE_UNIT=" + json.dumps(
                    {"source_key": row["source_key"], **unit}, ensure_ascii=False))


if __name__ == "__main__":
    main()
