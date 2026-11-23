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
from time import monotonic
import unicodedata
import xml.etree.ElementTree as ET

from scripts.research_1915_print_pages import (
    candidate_heading, expected_volume, normalize,
)
from scripts.diagnose_1915_ocr_candidate_spans import diagnose_candidates
from scripts.guard_1915_print_headword_interleaving import guard_interleaved_headings

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


def token_fourgram_overlap(source_tokens, ocr_tokens):
    """Conservative ordered-four-token overlap, NOT text/print certification.

    A four-token run is robust enough to distinguish much common-word
    coincidence, yet sensitive to OCR errors, hyphenation, textual variants
    and wrong article boundaries. Source and OCR occurrences are counted
    with multiplicity; neither witness is rewritten.
    """
    if len(source_tokens) < 4 or len(ocr_tokens) < 4:
        return None, None
    source = Counter(
        tuple(source_tokens[i:i+4]) for i in range(len(source_tokens)-3)
    )
    observed = Counter(
        tuple(ocr_tokens[i:i+4]) for i in range(len(ocr_tokens)-3)
    )
    common = sum((source & observed).values())
    source_recall = round(common / (len(source_tokens)-3), 4)
    ocr_precision = round(common / (len(ocr_tokens)-3), 4)
    return source_recall, ocr_precision


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
        source_tokens = latin_tokens(text)
        entries.append({
            "key": key, "article_xml_id": article.get(ID),
            "tei_latin_tokens": len(source_tokens),
            # Nonauthorial source-key display never appears in this sample.
            # Used only to disambiguate a duplicated OCR heading candidate.
            "opening_latin_tokens": source_tokens[:16],
            # Transient internal evidence; NEVER serialized to JSON reports.
            "source_latin_tokens": source_tokens,
        })
    if not entries:
        raise ValueError("No TEI entries for original historical print volume")
    return entries


def _tag(elem):
    return elem.tag.rsplit("}", 1)[-1]


def bbox_lines(path, page_count):
    """Two printed columns, read in physical bands separated by section letters.

    A full-width alphabetic section heading can occur midway down a page:
    upper left/right columns must be read before lower left/right columns.
    Blindly sorting the *entire* left column before the entire right one
    can swallow text belonging to the previous encyclopedia letter.
    Only a centered, oversized, single uppercase Latin letter triggers a
    band split. Ordinary page headings/prose cannot trigger a rearrangement.
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
        possible_sections = []
        heights = []
        for line in page.iter():
            if _tag(line) != "line":
                continue
            valid = []
            for word in line:
                if _tag(word) != "word" or not (word.text or "").strip():
                    continue
                xmin = float(word.attrib["xMin"])
                xmax = float(word.attrib["xMax"])
                ymin = float(word.attrib["yMin"])
                ymax = float(word.attrib["yMax"])
                x, y = (xmin + xmax) / 2, (ymin + ymax) / 2
                if not (0.075 * height <= y <= 0.94 * height):
                    continue
                valid.append((xmin, x, y, ymax - ymin, word.text.strip()))
            if not valid:
                continue
            if (len(valid) == 1
                    and re.fullmatch(r"[A-Z]", valid[0][4])
                    and 0.45 * width <= valid[0][1] <= 0.55 * width
                    and 0.18 * height <= valid[0][2] <= 0.85 * height):
                possible_sections.append(valid[0])
                continue
            groups = {0: [], 1: []}
            for xmin, x, y, w_height, text in valid:
                heights.append(w_height)
                groups[int(x >= width / 2)].append((xmin, y, text))
            for col, words in groups.items():
                if words:
                    words.sort(key=lambda item: item[0])
                    text = " ".join(w[2] for w in words)
                    y = min(w[1] for w in words)
                    buckets[col].append((y, text))

        # Compare the section letter size against *actual glyph heights* on
        # the same source page, not a fixed font size or per-book exception.
        if heights:
            sorted_heights = sorted(heights)
            usual_height = sorted_heights[len(sorted_heights) // 2]
        else:
            usual_height = 0
        # A *large centered capital* alone is not sufficient: printed
        # page prose, diagrams and roman enumerations can generate hundreds
        # of false section breaks. Demand physical white space across BOTH
        # columns plus a first NEW left-column headword beginning with the
        # same printed alphabetic letter, all using source-agnostic geometry.
        cuts_by_y = {}
        for xmin, x, y, w_height, letter in possible_sections:
            if usual_height <= 0 or w_height < 1.5 * usual_height:
                continue
            distances = [
                abs(candidate_y - y)
                for col in (0, 1)
                for candidate_y, _ in buckets[col]
            ]
            if not distances or min(distances) < 1.8 * usual_height:
                continue
            following_left = sorted(
                (candidate_y, text) for candidate_y, text in buckets[0]
                if y < candidate_y <= y + 0.13 * height
            )
            # Near the printed V section the next left-column entry is
            # VAGABOND, while the right column above still carries UZZIEL.
            # The test depends on typography and the current letter, never
            # on any particular encyclopedia entry or hardcoded PDF page.
            if not any(
                re.match(
                    r"^\s*" + re.escape(letter) + r"[A-Z-]{3,}\s*[:,;(]",
                    text,
                )
                for _, text in following_left[:4]
            ):
                continue
            cuts_by_y[y] = letter
        cuts = sorted(cuts_by_y)
        # A *rejected* candidate is an ordinary OCR token. Never erase
        # potential authorial text merely because it resembles a section.
        for xmin, x, y, _, value in possible_sections:
            if y not in cuts_by_y:
                buckets[int(x >= width / 2)].append((y, value))
        edges = [float("-inf"), *cuts, float("inf")]
        for band in range(len(edges)-1):
            for col in (0, 1):
                for y, text in sorted(buckets[col], key=lambda item: item[0]):
                    if not (edges[band] < y < edges[band+1]):
                        continue
                    if re.search(
                        r"INTERNATIONAL\s+STANDARD\s+BIBLE\s+ENCYCLOP",
                        text, re.I,
                    ):
                        continue
                    result.append({
                        "page": pages_seen,
                        "column": "left" if col == 0 else "right",
                        "y": round(y, 1),
                        "section_band": band,
                        "midpage_letter_section": cuts_by_y.get(edges[band]) if band else None,
                        "text": text,
                    })
        page.clear()
    if pages_seen != page_count:
        raise ValueError(f"Scanned PDF page count differs: {pages_seen} != {page_count}")
    return result


def _opening_context_agrees(lines, position, entry):
    """Supplemental evidence for a repeated title candidate.

    This is not print certification: source opening prose can differ, and a
    failed check always leaves the occurrence unresolved. Avoid matching
    common one-word overlaps as alleged proof of an article heading.
    """
    source = [t for t in entry.get("opening_latin_tokens", ())
              if len(t) >= 4]
    if len(source) < 3:
        return False
    # Stop at a page turn or the next few OCR lines; never seek a match in
    # a different, possibly unrelated article hundreds of lines away.
    window = []
    page = lines[position]["page"]
    for line in lines[position+1:position+7]:
        if line["page"] > page + 1:
            break
        window.extend(latin_tokens(line["text"]))
    pos = 0
    matches = 0
    for token in source[:10]:
        try:
            loc = window.index(token, pos)
        except ValueError:
            continue
        pos = loc + 1
        matches += 1
    return matches >= 3


def _repeated_title_rescues(lines, entries, hits, strict):
    """Rescue only a title bracketed by two securely ordered unique titles.

    A duplicate outside the bracket is rejected as a repeated mention;
    a duplicate inside remains ambiguous. Requiring an *exact* standalone
    heading or corroborating opening words avoids arbitrary title selection.
    Previously trusted headings are never moved or replaced.
    """
    indices = sorted(strict)
    rescues = {}
    for index, positions in sorted(hits.items()):
        if index in strict or len(positions) < 2:
            continue
        offset = bisect_left(indices, index)
        if offset == 0 or offset == len(indices):
            continue
        lower, upper = strict[indices[offset-1]], strict[indices[offset]]
        if lower >= upper:
            continue
        between = [pos for pos in positions if lower < pos < upper]
        if len(between) != 1:
            continue
        pos = between[0]
        normalized_heading = normalize(entries[index]["key"])
        standalone = normalize(lines[pos]["text"]) == normalized_heading
        if standalone or _opening_context_agrees(lines, pos, entries[index]):
            rescues[index] = pos
    return rescues


def _weak_contextual_title_rescues(lines, entries, weak_hits, strict, promoted):
    """TitleCase/lowercase OCR headings must have independent opening evidence.

    Do not accept low-scoring matches globally. Only consider a unique
    exact-text heading between two independently accepted strict anchors,
    and match at least three ordered distinctive source words immediately
    after it. This protects against a sentence/prose line looking like a
    short article name.
    """
    anchors = sorted(strict)
    rescued = {}
    for index, positions in weak_hits.items():
        if index in strict or index in promoted:
            continue
        offset = bisect_left(anchors, index)
        if not 0 < offset < len(anchors):
            continue
        lower, upper = strict[anchors[offset-1]], strict[anchors[offset]]
        if lower >= upper:
            continue
        between = [pos for pos in positions if lower < pos < upper]
        if len(between) != 1:
            continue
        pos = between[0]
        if (normalize(lines[pos]["text"]) == normalize(entries[index]["key"])
                and _opening_context_agrees(lines, pos, entries[index])):
            rescued[index] = pos
    return rescued


def unique_print_headings(lines, entries):
    """Two-stage monotonic alignment, preserving a strict-baseline counter.

    First find unique, strongly scored heading candidates (the v1 rule).
    Resolve a duplicated title only if exactly one printed occurrence lies
    between two v1 anchors, with exact-heading or opening-prose support.
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
    weak_hits = defaultdict(list)
    for pos, line in enumerate(lines):
        text = line["text"]
        prefix = normalize(text)
        if not prefix:
            continue
        strong, weak = [], []
        for canon, key, index in by_word.get(prefix.split()[0], ()):
            if canon not in unique_names:
                continue
            score = candidate_heading(text, key)
            if score >= 4:
                strong.append((len(canon), index))
            elif score == 1 and prefix == canon:
                weak.append((len(canon), index))
        # Never allow a weak title to override a strong title on this line.
        matches = strong or weak
        if not matches:
            continue
        best = max(length for length, _ in matches)
        winners = [index for length, index in matches if length == best]
        if len(winners) != 1:
            continue
        if strong:
            hits[winners[0]].append(pos)
        else:
            weak_hits[winners[0]].append(pos)
    unique = [(positions[0], index)
              for index, positions in hits.items() if len(positions) == 1]
    unique.sort()

    # Original strictly monotonic v1 anchor baseline, not a permissive
    # replacement for the already audited first pass.
    tails, owners = [], []
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
    strict = {index: pos for i, (pos, index) in enumerate(unique)
              if i in kept}
    rescues = _repeated_title_rescues(lines, entries, hits, strict)
    weak_rescues = _weak_contextual_title_rescues(
        lines, entries, weak_hits, strict, rescues
    )
    accepted = dict(strict)
    accepted.update(rescues)
    accepted.update(weak_rescues)
    if len(set(accepted.values())) != len(accepted):
        raise ValueError("Duplicate source heading positions assigned")
    sorted_positions = [accepted[i] for i in sorted(accepted)]
    if sorted_positions != sorted(sorted_positions):
        raise ValueError("Repaired heading sequence is not monotonic")
    return accepted, {
        "headword_candidates_total": sum(len(v) for v in hits.values()),
        "unique_ocr_heading_articles": len(unique),
        "strict_ordered_unique_heading_articles": len(strict),
        "ordered_unique_heading_articles": len(accepted),
        "bracketed_duplicate_heading_rescues": len(rescues),
        "weak_heading_candidates": sum(len(v) for v in weak_hits.values()),
        "weak_bracketed_context_rescues": len(weak_rescues),
        "ambiguous_multiple_heading_articles": sum(len(p) != 1 for p in hits.values()),
        "nonmonotonic_unique_heading_articles": len(unique) - len(strict),
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
            "source_fourgram_recall": None,
            "ocr_fourgram_precision": None,
            "status": "unresolved_print_boundaries",
            "visually_verified": False,
            "full_print_text_certified": False,
        }
        start = accepted.get(i)
        stop = accepted.get(i + 1)
        # Count only between *consecutive* article headings in TEI order,
        # which forbids absorbing an unlocated intervening article.
        if start is not None and stop is not None and stop > start:
            span_tokens = []
            for line in lines[start:stop]:
                span_tokens.extend(latin_tokens(line["text"]))
            heading_tokens = len(latin_tokens(entry["key"]))
            # Match the original v1 word-count rule exactly: subtract the
            # synthetic source headword token count, without pretending the
            # OCR headword typography is fully proved.
            ocr_body_tokens = span_tokens[heading_tokens:]
            ocr_count = len(ocr_body_tokens)
            tei_count = row["tei_latin_tokens"]
            source_recall, ocr_precision = token_fourgram_overlap(
                entry.get("source_latin_tokens", []), ocr_body_tokens
            )
            row.update({
                "ocr_latin_tokens": ocr_count,
                "source_fourgram_recall": source_recall,
                "ocr_fourgram_precision": ocr_precision,
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
    letter_breaks = sorted({
        (line["page"], line["midpage_letter_section"])
        for line in lines if line.get("midpage_letter_section")
    })
    alignment["printed_pages_with_explicit_midpage_section_breaks"] = len(letter_breaks)
    alignment["printed_midpage_section_break_candidates"] = [
        {"pdf_page_1_based": page, "letter": letter, "image_verified": False}
        for page, letter in letter_breaks
    ]
    reports, _ = assess(lines, entries, accepted)
    reports, guarded = guard_interleaved_headings(lines, entries, accepted, reports)
    statuses = dict(sorted(Counter(row["status"] for row in reports).items()))
    targeted = diagnose_candidates(lines, entries, accepted, reports, latin_tokens)
    return {
        "schema_version": 8,
        "volume": volume,
        "print_pdf_sha256": pdf_sha,
        "canonical_tei_sha256": source_sha,
        "pdf_pages": witness[0]["pages"],
        "ocr_latin_token_definition": "NFKD decomposition then ASCII [a-z0-9]+; non-Latin characters, punctuation and typography are not compared",
        "lexical_comparison": "ordered 4-token multiset overlap: source recall and OCR precision; generated for candidate segmentation only, never proof of print fidelity",
        "extraction": "single pdftotext -bbox-layout pass over entire SHA-locked original volume",
        "alignment": "strong source-ordered OCR anchors; midpage centered uppercase alphabetic section bands read left/right in each band; independently recognized interrupted printed headings quarantine invalid digital-neighbor spans",
        "source": manifest["bibliographic_citation"],
        "original_pages_2887_2888_available_in_volume_v": False if volume == "5" else None,
        "ocr_not_original_print_certification": True,
        "publication_permitted": False,
        "articles_in_volume": len(entries),
        "article_count_sum": sum(statuses.values()),
        "heading_diagnostics": alignment,
        "ocr_intervals_withdrawn_due_to_independent_intervening_print_headwords": guarded,
        "independent_print_order_does_not_imply_digital_source_order": True,
        "status_counts": statuses,
        "content_candidate_diagnostic_method": "existing SHA-locked 1915 PDF OCR bboxes, no second extraction; 1/2/3/4-gram evidence and unique 4-gram localization; no historical image certification",
        "content_candidate_diagnostics": targeted,
        "content_candidate_diagnostic_count": len(targeted),
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
        started = monotonic()
        subprocess.run(
            ["pdftotext", "-bbox-layout", str(pdf), str(bbox)],
            check=True, timeout=300,
        )
        extraction_seconds = monotonic() - started
        result = compare_bbox(
            bbox, pdf_sha, digest(tei), volume, manifest, entries,
        )
        result["ocr_extraction_seconds"] = round(extraction_seconds, 2)
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
        "ocr_extraction_seconds": result["ocr_extraction_seconds"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
