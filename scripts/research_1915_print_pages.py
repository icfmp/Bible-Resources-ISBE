#!/usr/bin/env python3
"""Locate *candidate* 1915 printed ISBE headings in independently scanned PDFs.

Only source-provenance and OCR location research. This script does NOT certify
print typography, resolve manuscript variants, correct a digital text, or
authorize changes to the canonical TEI. It never modifies the original scans.
"""
import argparse
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

EXPECTED_CANONICAL_SHA256 = (
    "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
)
BOOK_ID = "James Orr, The International Standard Bible Encyclopaedia, 1915"


def normalize(value):
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    return " ".join(re.findall(r"[A-Z0-9]+", value.upper()))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def candidate_heading(line, key):
    """Scores *possible* headword headings, never claims certainty from OCR."""
    cleaned = normalize(line)
    target = normalize(key)
    if not target or (cleaned != target and not cleaned.startswith(target + " ")):
        return 0
    if len(line.strip()) > 190:
        return 0
    raw = line.strip()
    # Strongest evidence is a short uppercase prefix at beginning of an OCR
    # line, rather than an incidental mention in prose or running headers.
    if normalize(raw) == target:
        return 4
    stem = re.sub(r"[^A-Za-z]+", "", raw[:len(key)+8])
    uppercase = stem and stem.upper() == stem
    return 3 if uppercase else 2


def find_headings(pages, source_keys, max_hits=8):
    out = {}
    for key in source_keys:
        hits = []
        for index, page in enumerate(pages):
            lines = page.splitlines()
            for i, line in enumerate(lines):
                score = candidate_heading(line, key)
                if not score:
                    continue
                hits.append({
                    "pdf_page_1_based": index + 1,
                    "ocr_line_1_based": i + 1,
                    "score": score,
                    "source_line": line.strip()[:190],
                    "previous_line": lines[i-1].strip()[:130] if i else "",
                    "following_lines": " ".join(
                        l.strip() for l in lines[i+1:i+3]
                    )[:240],
                    "page_image_inspected": False,
                })
        hits.sort(key=lambda r: (-r["score"], r["pdf_page_1_based"],
                                 r["ocr_line_1_based"]))
        out[key] = hits[:max_hits]
    return out


def analyze_pdf(pdf_path, source_ledger_path, volume):
    pdf_path = Path(pdf_path)
    if pdf_path.read_bytes()[:5] != b"%PDF-":
        raise ValueError("Historical scan is not a PDF")
    ledger = json.loads(Path(source_ledger_path).read_text(encoding="utf-8"))
    if ledger.get("baseline_canonical_tei_sha256") != EXPECTED_CANONICAL_SHA256:
        raise ValueError("Different source-locked canonical edition")
    cases = ledger["cases"]
    keys = [case["source_key"] for case in cases]
    if len(keys) != 31 or len(keys) != len(set(keys)):
        raise ValueError("Expected the 31 known distinct source gaps")
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True, text=True, check=True, timeout=180,
    )
    pages = result.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if len(pages) < 100:
        raise ValueError("Expected a complete historical volume, not an excerpt")
    # These scans should never be confused with the 1979-1995 revision.
    front = normalize(" ".join(pages[:10]))
    if "INTERNATIONAL STANDARD BIBLE" not in front:
        raise ValueError("PDF is not an identifiable ISBE historical scan")
    heading_candidates = find_headings(pages, keys)
    case_results = [
        {"source_key": key, "proposed_genre": next(
            case["genre_hypothesis"] for case in cases
            if case["source_key"] == key),
         "candidates": heading_candidates[key],
         "ocr_does_not_certify_print": True}
        for key in keys
    ]
    return {
        "historical_witness": BOOK_ID,
        "witness_volume": volume,
        "pdf_sha256": digest(pdf_path),
        "pdf_total_pages": len(pages),
        "canonical_source_sha256": EXPECTED_CANONICAL_SHA256,
        "claims_exact_print_verification": False,
        "total_checked_keys": len(case_results),
        "keys_with_heading_candidates": sum(
            bool(row["candidates"]) for row in case_results),
        "cases": case_results,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf", type=Path, required=True)
    p.add_argument("--volume", required=True)
    p.add_argument("--ledger", type=Path,
                   default=Path("workspace/reviews/empty-article-recovery-ledger.json"))
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    report = analyze_pdf(a.pdf, a.ledger, a.volume)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print("Witness:", report["historical_witness"], "vol.", a.volume, flush=True)
    print("PDF SHA256:", report["pdf_sha256"], flush=True)
    print("Pages:", report["pdf_total_pages"], flush=True)
    for case in report["cases"]:
        if case["candidates"]:
            best = case["candidates"][0]
            print("CANDIDATE:", repr(case["source_key"]), "pdf-page",
                  best["pdf_page_1_based"], "score", best["score"],
                  repr(best["source_line"]), flush=True)
    print("OCR heading candidates:",
          report["keys_with_heading_candidates"], "/",
          report["total_checked_keys"], flush=True)


if __name__ == "__main__":
    main()
