#!/usr/bin/env python3
"""Compact cohort transport; canonical TEI and the existing bridge remain authoritative."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.markdown_translation_bridge import compile_draft
from scripts.select_translation_pilot import SOURCE_SHA256
from scripts.translation_markdown_layout import (
    BLOCK_END, BLOCK_START, HEADER, HEADER_END, build_blocks, load_article, metadata,
)


def source_record(archive, key, *, expected_sha=SOURCE_SHA256):
    row, article = load_article(archive, key, expected_sha=expected_sha)
    return {
        "article_id": row["article_id"], "source_key": key,
        "source_sha256": expected_sha,
        "source_article_sha256": row["source_article_sha256"],
        "blocks": [[b["id"], b["prefix"],
                    [v if k == "marker" else list(v) for k, v in b["parts"]]]
                   for b in build_blocks(article)],
    }


def slots(record):
    return [p for _, _, parts in record["blocks"] for p in parts if isinstance(p, list)]


def render(record, targets, preserve=None):
    if not isinstance(targets, list) or len(targets) != len(slots(record)):
        raise ValueError("Target count differs from source slot count")
    if any(not isinstance(v, str) or not v.strip() for v in targets):
        raise ValueError("Missing or non-string translation slot")
    if any("⟦ISBE:" in v or "<!-- ISBE-" in v for v in targets):
        raise ValueError("Reserved marker in translation")
    if preserve is None:
        preserve = {}
    if not isinstance(preserve, dict):
        raise ValueError("Preservation reasons must be an object")
    head = metadata(record, source_sha=record["source_sha256"])
    head["preserve"] = preserve
    result = [HEADER + json.dumps(head, ensure_ascii=False, sort_keys=True) + HEADER_END]
    translated = iter(targets)
    for ident, prefix, parts in record["blocks"]:
        body = prefix + "".join(next(translated) if isinstance(p, list) else p for p in parts)
        result.extend([f"{BLOCK_START}{ident} -->\n", body,
                       f"\n{BLOCK_END}{ident} -->\n\n"])
    return "".join(result)


def jsonl(records):
    return "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in records)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def export_queue(archive, queue, *, expected_sha=SOURCE_SHA256):
    manifest = json.loads((queue / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest["source_sha256"] != expected_sha or manifest["publication_permitted"] is not False:
        raise ValueError("Untrusted source queue")
    seen, records = set(), []
    for entry in manifest["articles"]:
        record = source_record(archive, entry["source_key"], expected_sha=expected_sha)
        ident = record["article_id"]
        if (ident in seen or ident != entry["article_id"]
                or record["source_article_sha256"] != entry["source_article_sha256"]
                or entry["template"] != ident + ".md"):
            raise ValueError("Duplicate or mismatched canonical identity")
        seen.add(ident)
        original = (queue / entry["template"]).read_bytes()
        if hashlib.sha256(original).hexdigest() != entry["template_sha256"]:
            raise ValueError("Source template checksum mismatch")
        if render(record, [p[2] for p in slots(record)]).encode("utf-8") != original:
            raise ValueError("Compact export does not reconstruct exact source template")
        records.append(record)
    if len(records) != manifest["templates_prepared"]:
        raise ValueError("Source queue count mismatch")
    return records


def compile_group(archive, records, translations, *, expected_sha=SOURCE_SHA256):
    """Compile all inputs before returning any output; subset groups allowed."""
    by_id = {}
    for record in records:
        ident = record["article_id"]
        if ident in by_id:
            raise ValueError("Duplicate source article")
        by_id[ident] = record
    manuscripts, articles, reports = {}, [], []
    batch = None
    for target in translations:
        if set(target) - {"article_id", "targets", "preserve"}:
            raise ValueError("Unknown translation fields")
        ident = target["article_id"]
        if ident not in by_id or ident in manuscripts:
            raise ValueError("Unknown or duplicate translated article")
        record = by_id[ident]
        if record != source_record(archive, record["source_key"], expected_sha=expected_sha):
            raise ValueError("Compact source differs from canonical source")
        manuscript = render(record, target["targets"], target.get("preserve", {}))
        patch, report = compile_draft(archive, manuscript, expected_sha=expected_sha)
        manuscripts[ident] = manuscript
        articles.extend(patch["articles"])
        reports.append(report)
        if batch is None:
            batch = {k: v for k, v in patch.items() if k != "articles"}
    if not articles:
        raise ValueError("Empty translation group")
    batch["articles"] = articles
    return batch, manuscripts, reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    exp = sub.add_parser("export")
    for arg in ("archive", "queue", "output"):
        exp.add_argument("--" + arg, required=True, type=Path)
    comp = sub.add_parser("compile")
    for arg in ("archive", "source", "translations", "output"):
        comp.add_argument("--" + arg, required=True, type=Path)
    args = parser.parse_args()
    if args.action == "export":
        records = export_queue(args.archive, args.queue)
        data = jsonl(records).encode("utf-8")
        if args.output.exists() and args.output.read_bytes() != data:
            raise ValueError("Refusing to overwrite changed compact export")
        args.output.write_bytes(data)
        print("SOURCE_LOCKED_JSONL_ARTICLES", len(records))
    else:
        batch, manuscripts, reports = compile_group(
            args.archive, read_jsonl(args.source), read_jsonl(args.translations))
        if args.output.exists() and any(args.output.iterdir()):
            raise ValueError("Use an empty output directory")
        args.output.mkdir(parents=True, exist_ok=True)
        working = args.output / "working"
        working.mkdir()
        for ident, text in manuscripts.items():
            (working / (ident + ".md")).write_text(text, encoding="utf-8")
        for name, value in (("batch.json", batch), ("reports.json", reports)):
            (args.output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("SOURCE_LOCKED_DRAFTS", len(manuscripts))


if __name__ == "__main__":
    main()
