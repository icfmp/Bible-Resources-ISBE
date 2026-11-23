#!/usr/bin/env python3
"""Find unresolved ISBE headword print locations without certifying OCR.

Use only fingerprinted original 1915 printed-volume scans. This is an
investigative candidate ranker: ambiguity is kept, never silently repaired.
"""
import argparse
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata

GAPS = {
    "1": {
        "ASTARTE; ASTORETH": (190, 460, ("ASHTAROTH", "ASTORETH")),
        "CHORBE": (560, 714, ("CORBE", "ZERUBBABEL", "CHOSAMAEUS")),
    },
    "3": {
        "JOSIBIAH": (175, 630, ("JOSHIBIAH", "JOSIBIAH")),
    },
    "4": {
        "PATRIARCHS, TESTAMENTS OF THE TWELVE": (100, 205, ("APOCALYPTIC", "PATRIARCHS")),
        "REGENERATION, BAPTISMAL": (370, 625, ("BAPTISMAL", "REGENERATION")),
    },
    "5": {
        "THOCANUS": (140, 190, ("EZEKIAS", "TIKVAH", "THEOCANUS")),
    },
}


def normalize(txt):
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    return " ".join(re.findall(r"[A-Z0-9]+", txt.upper()))


def score_line(segment, key, context_words):
    source = normalize(segment)
    target = normalize(key)
    if not source or len(source) < 3:
        return 0.0
    # Compare *short leading spans*, not whole prose lines.
    prefix = source[:max(12, len(target) + 5)]
    ratio = SequenceMatcher(None, prefix[:len(target)], target).ratio()
    exact = source == target or source.startswith(target + " ")
    token = target.split()[0]
    token_hit = bool(token and token in source.split()[:4])
    # Context-word scores may point to a body paragraph; never count them
    # alone as a verified article heading.
    ctx = sum(w in source for w in context_words)
    return round(3.0 * float(exact) + 2.0 * ratio +
                 0.7 * float(token_hit) + 0.12 * min(ctx, 2), 3)


def candidate_pages(pages, key, low, high, context, maximum=12):
    candidates = []
    for page_index in range(max(0, low-1), min(len(pages), high)):
        lines = pages[page_index].splitlines()
        for index, full in enumerate(lines):
            for segment in [full, *re.split(r"\s{4,}", full)]:
                segment = segment.strip()
                if not segment:
                    continue
                rating = score_line(segment, key, context)
                if rating < 1.43:
                    continue
                # A candidate with no headword-like element is a weak clue.
                candidates.append({
                    "pdf_page_1_based": page_index + 1,
                    "ocr_line_1_based": index + 1,
                    "rating": rating,
                    "source_span": segment[:180],
                    "full_ocr_line": full.strip()[:250],
                    "next_ocr_line": lines[index+1].strip()[:240]
                      if index+1 < len(lines) else "",
                    "visually_verified": False,
                })
    candidates.sort(key=lambda x: (-x["rating"], x["pdf_page_1_based"], x["ocr_line_1_based"]))
    # Distinct page candidates, not ten matching lines on a single page.
    selected, seen = [], set()
    for c in candidates:
        p = c["pdf_page_1_based"]
        if p in seen:
            continue
        seen.add(p)
        selected.append(c)
        if len(selected) >= maximum:
            break
    return selected


def investigate(pdf, volume, witness_manifest):
    spec = json.loads(Path(witness_manifest).read_text(encoding="utf-8"))
    w = next(v for v in spec["volumes"] if v["volume"] == str(volume))
    raw = Path(pdf).read_bytes()
    if hashlib.sha256(raw).hexdigest() != w["pdf_sha256"]:
        raise ValueError("Historical scan SHA256 mismatch")
    process = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                             check=True, capture_output=True, text=True, timeout=180)
    pages = process.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if len(pages) != w["pages"]:
        raise ValueError("Historical volume page count mismatch")
    output = {
        "historical_witness_volume": str(volume),
        "pdf_sha256": w["pdf_sha256"],
        "pdf_pages": len(pages),
        "print_page_visually_verified": False,
        "key_candidates": [],
    }
    for key, (low, high, context) in GAPS.get(str(volume), {}).items():
        output["key_candidates"].append({
            "source_key": key,
            "search_window_pdf_pages_1_based": [low, high],
            "candidates": candidate_pages(pages, key, low, high, context),
            "confidence": "OCR_ONLY_UNVERIFIED",
        })
    return output


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", required=True)
    p.add_argument("--volume", choices=list(GAPS), required=True)
    p.add_argument("--witness-manifest", default="workspace/witnesses/print/1915-volume-witnesses.json")
    p.add_argument("--output", required=True)
    a = p.parse_args()
    result = investigate(a.pdf, a.volume, a.witness_manifest)
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("VOLUME", a.volume, "verified original PDF", result["pdf_sha256"])
    for entry in result["key_candidates"]:
        print("HEADWORD", entry["source_key"], "range", entry["search_window_pdf_pages_1_based"])
        for hit in entry["candidates"][:10]:
            print("  CANDIDATE", hit["pdf_page_1_based"], hit["rating"],
                  repr(hit["source_span"]), "NEXT", repr(hit["next_ocr_line"][:130]))


if __name__ == "__main__":
    main()
