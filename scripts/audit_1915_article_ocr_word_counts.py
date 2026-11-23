#!/usr/bin/env python3
"""Read-only article-level Latin-token count triage: 1915 print OCR vs TEI.

This tool checks exact SHA-locked 1915 PDFs, calls pdftotext exactly ONCE
per volume (bbox-layout), and never OCRs or alters printed images. It
aligns only strong, unique, monotonic printed headword candidates. Counts
are emitted ONLY between two immediately consecutive TEI article starts:
intermediate unlocated titles make both boundaries unusable. The printed
headword itself and the artificial TEI index head are excluded.

OCR and title alignment cannot establish printed-text fidelity; status
names are deliberately *candidates*, never approvals or certifications.
"""
import argparse
from bisect import bisect_left
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET

from scripts.research_1915_print_pages import (
    candidate_heading, expected_volume, normalize,
)

TEI = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"
LOCK = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"


def digest(path):
    h = sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def latin_tokens(text):
    decomp = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(ch for ch in decomp if ord(ch) < 128)
    return re.findall(r"[a-z0-9]+", ascii_text.lower())


def tei_entries(path, volume, manifest):
    if digest(path) != LOCK or manifest.get("canonical_tei_sha256") != LOCK:
        raise ValueError("Canonical TEI source SHA-256 drift")
    root = ET.parse(path).getroot()
    body = root.find(f"./{TEI}text/{TEI}body")
    if root.tag != TEI + "TEI" or body is None or len(body) != 9380:
        raise ValueError("Unexpected canonical encyclopedia article coverage")
    entries = []
    all_keys = set()
    for article in body:
        key = article.get("n")
        if not key or key in all_keys or not article.get(ID):
            raise ValueError("Missing or duplicate article identity")
        all_keys.add(key)
        if expected_volume(key) != volume:
            continue
        # The canonical index head is constructed from the dictionary key;
        # it does NOT come from the article's printed text.
        text = " ".join(
            " ".join(child.itertext()) for child in article
            if not (child.tag == TEI + "head" and child.get("type") == "index")
        )
        entries.append({
            "key": key, "article_xml_id": article.get(ID),
            "tei_latin_tokens": len(latin_tokens(text)),
        })
    if not entries:
        raise ValueError("No TEI entries for original historical print volume")
    return entries


def _tag(elem):
    return elem.tag.rsplit("}", 1)[-1]


def bbox_lines(path, page_count):
    """Return left-column then right-column lines per original PDF page.

    Poppler's word bounding boxes, not plaintext padding/reading order,
    determine columns. That avoids interleaving two parallel columns.
    Pages with unusual layouts remain candidates, not guaranteed text.
    """
    result = []
    pages_seen = 0
    for _, page in ET.iterparse(path, events=("end",)):
        if _tag(page) != "page":
            continue
        pages_seen += 1
        width = float(page.attrib["width"])
        height = float(page.attrib["height"])
        if width < 100 or height < 100:
            raise ValueError("Invalid scanned page coordinates")
        buckets = {0: [], 1: []}
        for line in page.iter():
            if _tag(line) != "line":
                continue
            groups = {0: [], 1: []}
            for word in line:
                if _tag(word) != "word" or not (word.text or "").strip():
                    continue
                x = (float(word.attrib["xMin"]) + float(word.attrib["xMax"])) / 2
                y = (float(word.attrib["yMin"]) + float(word.attrib["yMax"])) / 2
                # Crop page furniture, not authorial body text; a missed
                # heading is preferable to a false-perfect OCR comparison.
                if not (0.075 * height <= y <= 0.94 * height):
                    continue
                groups[int(x >= width / 2)].append(
                    (float(word.attrib["xMin"]), y, word.text.strip())
                )
            for col, words in groups.items():
                if words:
                    words.sort(key=lambda item: item[0])
                    text = " ".join(w[2] for w in words)
                    y = min(w[1] for w in words)
                    buckets[col].append((y, text))
        for col in (0, 1):
            for y, text in sorted(buckets[col], key=lambda item: item[0]):
                # Headers/footers can survive physical cropping. A line
                # identical to this running title is not article content.
                if re.search(r"INTERNATIONAL\s+STANDARD\s+BIBLE\s+ENCYCLOP", text, re.I):
                    continue
                result.append({
                    "page": pages_seen, "column": "left" if col == 0 else "right",
                    "y": round(y, 1), "text": text,
                })
        page.clear()
    if pages_seen != page_count:
        raise ValueError(f"Scanned PDF page count differs: {pages_seen} != {page_count}")
    return result


def unique_print_headings(lines, entries):
    """Conservative unique candidate + monotonic order alignment.

    Duplicate normalized keys, multiple OCR occurrences, and inversions
    are *not* assigned a plausible-looking boundary.
    """
    by_word = defaultdict(list)
    normalized = defaultdict(list)
    for index, entry in enumerate(entries):
        key = entry["key"]
        canon = normalize(key)
        if not canon:
            continue
        normalized[canon].append(index)
        by_word[canon.split()[0]].append((canon, key, index))
    unique_names = {canon for canon, indices in normalized.items()
                    if len(indices) == 1}
    hits = defaultdict(list)
    for pos, line in enumerate(lines):
        text = line["text"]
        prefix = normalize(text)
        if not prefix:
            continue
        first = prefix.split()[0]
        candidates = [
            (len(canon), index, key) for canon, key, index
            in by_word.get(first, ())
            if canon in unique_names and candidate_heading(text, key) >= 4
        ]
        if not candidates:
            continue
        # Only one candidate heading can start at the same printed line.
        best = max(c[0] for c in candidates)
        winners = [c for c in candidates if c[0] == best]
        if len(winners) != 1:
            continue
        _, index, key = winners[0]
        hits[index].append(pos)
    unique = [(positions[0], index)
              for index, positions in hits.items() if len(positions) == 1]
    unique.sort()

    # The original encyclopedia is in alphabetical article order. Longest
    # increasing subsequence keeps print positions and digital order aligned.
    tails = []
    owners = []
    previous = [-1] * len(unique)
    for i, (_, index) in enumerate(unique):
        slot = bisect_left(tails, index)
        if slot == len(tails):
            tails.append(index)
            owners.append(i)
        else:
            tails[slot], owners[slot] = index, i
        if slot:
            previous[i] = owners[slot - 1]
    kept = set()
    if owners:
        cur = owners[-1]
        while cur >= 0:
            kept.add(cur)
            cur = previous[cur]
    accepted = {index: pos for i, (pos, index) in enumerate(unique)
                if i in kept}
    return accepted, {
        "headword_candidates_total": sum(len(v) for v in hits.values()),
        "unique_ocr_heading_articles": len(unique),
        "ordered_unique_heading_articles": len(accepted),
        "ambiguous_multiple_heading_articles": sum(len(p) != 1 for p in hits.values()),
        "nonmonotonic_unique_heading_articles": len(unique) - len(accepted),
        "normalized_key_collisions": sum(len(v) > 1 for v in normalized.values()),
    }


def assess(lines, entries, accepted):
    reports = []
    classes = Counter()
    for i, entry in enumerate(entries):
        row = {
            "article_key": entry["key"],
            "article_xml_id": entry["article_xml_id"],
            "tei_latin_tokens": entry["tei_latin_tokens"],
            "ocr_latin_tokens": None,
            "ocr_start_pdf_page": None,
            "ocr_end_pdf_page": None,
            "ocr_to_tei_ratio": None,
            "status": "unresolved_print_boundaries",
            "visually_verified": False,
            "full_print_text_certified": False,
        }
        start = accepted.get(i)
        stop = accepted.get(i + 1)
        # Count only between *consecutive* article headings in TEI order,
        # which forbids absorbing an unlocated intervening article.
        if start is not None and stop is not None and stop > start:
            total = sum(len(latin_tokens(line["text"]))
                        for line in lines[start:stop])
            heading_tokens = len(latin_tokens(entry["key"]))
            ocr_count = max(0, total - heading_tokens)
            tei_count = row["tei_latin_tokens"]
            row.update({
                "ocr_latin_tokens": ocr_count,
                "ocr_start_pdf_page": lines[start]["page"],
                "ocr_end_pdf_page": lines[stop]["page"],
                "ocr_to_tei_ratio": round(ocr_count / tei_count, 4) if tei_count else None,
            })
            if tei_count == 0:
                row["status"] = ("source_empty_print_ocr_nonempty"
                                 if ocr_count > 0 else "both_zero_candidate")
            else:
                gap = abs(ocr_count - tei_count) / tei_count
                row["status"] = (
                    "ocr_count_near_source_candidate" if gap <= 0.1
                    else "ocr_count_diff_over_10pct_candidate"
                )
        classes[row["status"]] += 1
        reports.append(row)
    return reports, dict(sorted(classes.items()))


def compare_bbox(bbox_file, pdf_sha, source_sha, volume, manifest, entries):
    witness = [v for v in manifest["volumes"] if v["volume"] == volume]
    if len(witness) != 1 or witness[0]["pdf_sha256"] != pdf_sha:
        raise ValueError("Wrong source-identified 1915 scanned volume")
    lines = bbox_lines(bbox_file, witness[0]["pages"])
    accepted, alignment = unique_print_headings(lines, entries)
    reports, statuses = assess(lines, entries, accepted)
    return {
        "schema_version": 1,
        "volume": volume,
        "print_pdf_sha256": pdf_sha,
        "canonical_tei_sha256": source_sha,
        "pdf_pages": witness[0]["pages"],
        "ocr_latin_token_definition": "NFKD decomposition then ASCII [a-z0-9]+; non-Latin characters, punctuation and typography are not compared",
        "extraction": "single pdftotext -bbox-layout pass over entire SHA-locked original volume",
        "alignment": "unique uppercase OCR headword candidates in two-column geometric reading order, longest monotonic subsequence, immediately adjacent TEI article pairs only",
        "source": manifest["bibliographic_citation"],
        "original_pages_2887_2888_available_in_volume_v": False if volume == "5" else None,
        "ocr_not_original_print_certification": True,
        "publication_permitted": False,
        "articles_in_volume": len(entries),
        "article_count_sum": sum(statuses.values()),
        "heading_diagnostics": alignment,
        "status_counts": statuses,
        "entries": reports,
    }


def run(pdf, volume, manifest_file, tei, report):
    manifest = json.loads(Path(manifest_file).read_text(encoding="utf-8"))
    witnesses = {v["volume"]: v for v in manifest["volumes"]}
    if volume not in witnesses or len(witnesses) != 5:
        raise ValueError("Unapproved printed volume")
    pdf_sha = digest(pdf)
    if pdf_sha != witnesses[volume]["pdf_sha256"]:
        raise ValueError("Original scanned PDF SHA-256 mismatch")
    entries = tei_entries(tei, volume, manifest)
    with tempfile.TemporaryDirectory(prefix="isbe-1915-ocr-") as tmp:
        bbox = Path(tmp) / "page-words.xhtml"
        subprocess.run(
            ["pdftotext", "-bbox-layout", str(pdf), str(bbox)],
            check=True, timeout=300,
        )
        result = compare_bbox(
            bbox, pdf_sha, digest(tei), volume, manifest, entries,
        )
    dest = Path(report)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--volume", required=True)
    p.add_argument("--pdf", type=Path, required=True)
    p.add_argument("--tei", type=Path, default=Path("cleaned/en/ISBE.xml"))
    p.add_argument("--manifest", type=Path, default=Path("sources/print/1915-volume-witnesses.json"))
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    result = run(a.pdf, a.volume, a.manifest, a.tei, a.report)
    print(json.dumps({
        "volume": result["volume"], "pdf_pages": result["pdf_pages"],
        "articles_in_volume": result["articles_in_volume"],
        "status_counts": result["status_counts"],
        "heading_diagnostics": result["heading_diagnostics"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
