#!/usr/bin/env python3
"""Keep the next five unreviewed ISBE translation templates accessible as files.

The corrected English TEI stays authoritative; this is an editorial queue,
not a publication or an approval. Candidates follow the existing frozen
wave-01 shortlist and shortest-original-text rule.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.apply_translation_batches import load_patches
from scripts.apply_translation_pilot import text_units
from scripts.markdown_translation_bridge import template
from scripts.select_translation_pilot import SOURCE_COUNT, SOURCE_SHA256
from scripts.validate_translation_identity import entries, read_body, sha256


def prepare(*, archive: Path, source: Path, roster: Path,
            patches: list[Path], output: Path, limit: int = 5) -> dict:
    if not 1 <= limit <= 25:
        raise ValueError("Bounded editorial queue must contain 1–25 articles")
    if sha256(source) != SOURCE_SHA256:
        raise ValueError("Original corrected English TEI has changed")
    index = entries(read_body(source)[1])
    if len(index) != SOURCE_COUNT:
        raise ValueError("Canonical historical article count changed")
    by_key = {key: (position, article_id)
              for position, (article_id, key) in enumerate(index)}
    worklist = json.loads(roster.read_text(encoding="utf-8"))
    if worklist.get("source_sha256") != SOURCE_SHA256:
        raise ValueError("Untrusted historical wave-01 source worklist")
    wave = worklist["entries"]
    if len(wave) != 1000 or len({r["source_key"] for r in wave}) != 1000:
        raise ValueError("Expected 1,000 distinct original wave-01 keys")
    drafted = set(load_patches(patches))
    remaining = []
    _, original_body = read_body(source)
    for row in wave:
        key = row["source_key"]
        if key not in by_key:
            raise ValueError("Invented or missing original SWORD key")
        pos, ident = by_key[key]
        if row["index"] != pos + 1 or row["article_id"] != ident:
            raise ValueError("Wave-01 article position or original ID changed")
        if ident in drafted:
            continue
        unit_chars = sum(len(value) for _, _, _, value
                         in text_units(original_body[pos]))
        remaining.append((unit_chars, pos, key, ident))
    chosen = sorted(remaining)[:limit]
    chosen.sort(key=lambda r: r[1])
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Use an empty output directory for deterministic export")
    selected = []
    for unit_chars, pos, key, ident in chosen:
        file = f"{ident}.md"
        content = template(archive, key)
        if not content.startswith("<!-- ISBE-TRANSLATION-V1 "):
            raise ValueError("Invalid source-anchored translation template")
        (output / file).write_text(content, encoding="utf-8")
        selected.append({
            "source_position": pos,
            "source_key": key,
            "article_id": ident,
            "source_text_unit_chars": unit_chars,
            "template": file,
            "translation_status": "english_source_template_only",
        })
    manifest = {
        "schema_version": 1,
        "kind": "next_isbe_source_locked_french_markdown_templates",
        "source_sha256": SOURCE_SHA256,
        "translation_language": "fr",
        "wave_01_original_count": len(wave),
        "drafted_wave_01": len(wave) - len(remaining),
        "pending_wave_01": len(remaining),
        "templates_prepared": len(selected),
        "human_editorial_approvals": 0,
        "publication_permitted": False,
        "articles": selected,
    }
    (output / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--roster", type=Path, required=True)
    parser.add_argument("--patches", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    manifest = prepare(archive=args.archive, source=args.source,
                       roster=args.roster, patches=args.patches,
                       output=args.output, limit=args.limit)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
