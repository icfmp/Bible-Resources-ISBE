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


# Physical 1915 five-volume boundaries, not the four-volume 1979 revision.
# Headwords at exact boundary are not among the 31 source gaps.
VOLUME_BOUNDARIES = ("CLEMENCY", "HERESY", "NAARAH", "SOCKET")


def expected_volume(source_key):
    """Restrict OCR headword evidence to its alphabetical print volume."""
    key = normalize(source_key)
    if not key:
        raise ValueError("Missing ISBE headword")
    return str(1 + sum(key >= limit for limit in VOLUME_BOUNDARIES))


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
    stem = re.sub(r"[^A-Za-z]+", "", raw[:len(key)])
    uppercase = bool(stem) and stem.upper() == stem
    if normalize(raw) == target:
        return 5 if uppercase else 1
    # Historical headwords are usually printed uppercase. Lowercase words
    # and TitleCase alphabetical-index labels remain low-confidence mentions.
    return 4 if uppercase else 1


def find_headings(pages, source_keys, max_hits=8):
    out = {}
    for key in source_keys:
        hits = []
        for index, page in enumerate(pages):
            lines = page.splitlines()
            for i, line in enumerate(lines):
                # This historical scan has two printed columns. pdftotext's
                # layout mode often concatenates both onto ONE OCR line with
                # many spaces. Check each column-shaped span independently.
                segments = [line] + [
                    segment for segment in re.split(r"\s{4,}", line)
                    if segment and segment != line
                ]
                matches = []
                for segment in segments:
                    score = candidate_heading(segment, key)
                    if score:
                        matches.append((score, segment))
                if not matches:
                    continue
                score, segment = max(matches, key=lambda item: item[0])
                hits.append({
                    "pdf_page_1_based": index + 1,
                    "ocr_line_1_based": i + 1,
                    "score": score,
                    "source_line": segment.strip()[:190],
                    "whole_ocr_line": line.strip()[:250],
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


def verify_print_witness(manifest_path, volume, pdf_sha256, pages):
    """Fail closed if remote scans differ from the identified 1915 source."""
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("manifest_version") != 1:
        raise ValueError("Unreviewed historical witness manifest")
    if manifest.get("canonical_tei_sha256") != EXPECTED_CANONICAL_SHA256:
        raise ValueError("Witness source and canonical text locks differ")
    volumes = manifest.get("volumes", [])
    if len(volumes) != 5 or len({v["volume"] for v in volumes}) != 5:
        raise ValueError("Expected five uniquely identified original print volumes")
    matches = [v for v in volumes if v["volume"] == str(volume)]
    if len(matches) != 1:
        raise ValueError(f"Missing exact print source volume {volume}")
    witness = matches[0]
    if witness["pdf_sha256"] != pdf_sha256 or witness["pages"] != pages:
        raise ValueError("Downloaded original print witness does not match pinned SHA256/pages")
    if witness.get("print_page_images_reviewed") is not False:
        raise ValueError("Research provenance must not assert unearned visual review")
    return witness


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
        {"source_key": key,
         "expected_print_volume": expected_volume(key),
         "proposed_genre": next(
             case["genre_hypothesis"] for case in cases
             if case["source_key"] == key),
         # Vol V contains a back-of-book index to earlier volumes. Matches
         # there for ABISSEI etc are NOT original articles in volume V.
         "candidates": (
             heading_candidates[key]
             if expected_volume(key) == str(volume) else []
         ),
         "off_volume_mentions_ignored": (
             len(heading_candidates[key])
             if expected_volume(key) != str(volume) else 0
         ),
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
            any(hit["score"] >= 4 for hit in row["candidates"])
            for row in case_results),
        "keys_with_weak_mentions_only": sum(
            bool(row["candidates"]) and not any(
                hit["score"] >= 4 for hit in row["candidates"])
            for row in case_results),
        "cases": case_results,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf", type=Path, required=True)
    p.add_argument("--volume", required=True)
    p.add_argument("--witness-manifest", type=Path)
    p.add_argument("--ledger", type=Path,
                   default=Path("workspace/reviews/empty-article-recovery-ledger.json"))
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    report = analyze_pdf(a.pdf, a.ledger, a.volume)
    if a.witness_manifest:
        verify_print_witness(
            a.witness_manifest, a.volume,
            report["pdf_sha256"], report["pdf_total_pages"]
        )
        report["exact_1915_scan_sha256_verified"] = True
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print("Witness:", report["historical_witness"], "vol.", a.volume, flush=True)
    print("PDF SHA256:", report["pdf_sha256"], flush=True)
    print("Pages:", report["pdf_total_pages"], flush=True)
    for case in report["cases"]:
        if case["candidates"] and case["candidates"][0]["score"] >= 4:
            best = case["candidates"][0]
            print("CANDIDATE:", repr(case["source_key"]), "pdf-page",
                  best["pdf_page_1_based"], "score", best["score"],
                  repr(best["source_line"]), flush=True)
    print("Strong OCR heading candidates:",
          report["keys_with_heading_candidates"], "/",
          report["total_checked_keys"], flush=True)


if __name__ == "__main__":
    main()
