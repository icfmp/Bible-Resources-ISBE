#!/usr/bin/env python3
"""Read-only OCR concordance for provisional prose, never a printed-text certification.

The PDF must be exactly one of the five SHA-pinned original 1915 volumes.
The score reports only how well normalized LATIN candidate tokens align with
the printed scan's OCR layer; Greek/Hebrew/punctuation require image review.
"""
import argparse
import difflib
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

from scripts.audit_1915_prose_evidence import audit, load, ROOT


def latin_tokens(value):
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(c for c in decomposed if ord(c) < 128)
    return re.findall(r"[a-z0-9]+", ascii_text.lower())


def concordance(candidate, scanned):
    proposed = latin_tokens(candidate)
    original = latin_tokens(scanned)
    if not proposed or not original:
        return {"matched_candidate_tokens": 0, "candidate_token_count": len(proposed),
                "ordered_token_recall": 0, "unmatched_candidate_tokens": proposed[:20]}
    alignment = difflib.SequenceMatcher(None, proposed, original, autojunk=False)
    blocks = alignment.get_matching_blocks()
    positions = set()
    for block in blocks:
        positions.update(range(block.a, block.a + block.size))
    missing = [token for i, token in enumerate(proposed) if i not in positions]
    return {"matched_candidate_tokens": len(positions),
            "candidate_token_count": len(proposed),
            "ordered_token_recall": round(len(positions) / len(proposed), 3),
            "unmatched_candidate_tokens": missing[:20]}


def inspect(pdf_path, volume, root=ROOT):
    root = Path(root)
    witness = load(root / "workspace/witnesses/print/1915-volume-witnesses.json")
    volumes = {v["volume"]: v for v in witness["volumes"]}
    if volume not in volumes:
        raise ValueError("Unknown 1915 volume")
    actual_digest = hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest()
    if actual_digest != volumes[volume]["pdf_sha256"]:
        raise ValueError("1915 original PDF SHA mismatch")
    proof = audit(root)
    rows = [r for r in proof["records"] if r["printed_volume"] == volume]
    prose = {r["source_key"]: r for r in load(
        root / "workspace/reviews/print-prose-candidate-v1.json")["records"]}
    results = []
    for row in rows:
        p = row["pdf_page_1_based"]
        output = subprocess.run(
            ["pdftotext", "-f", str(p), "-l", str(p), "-layout",
             str(pdf_path), "-"], check=True, capture_output=True,
            text=True, timeout=60,
        ).stdout
        compare = concordance("\n".join(prose[row["source_key"]]["blocks"]), output)
        results.append({
            "source_key": row["source_key"],
            "volume": volume,
            "printed_folio": row["printed_folio"],
            "pdf_page_1_based": p,
            **compare,
            "ocr_collation_only": True,
            "full_print_text_certified": False,
        })
    return {"schema_version": 1, "original_pdf_sha256": actual_digest,
            "volume": volume, "inspected_articles": len(results),
            "method": "ordered normalized Latin token agreement with primary 1915 PDF OCR, NOT image collation",
            "entries": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--volume", required=True)
    args = parser.parse_args()
    print(json.dumps(inspect(args.pdf, args.volume), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
