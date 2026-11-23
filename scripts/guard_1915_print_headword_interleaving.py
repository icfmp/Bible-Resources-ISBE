#!/usr/bin/env python3
"""Fail closed when a printed headword interrupts two digital source keys.

The 1915 printed volume's order need not equal CrossWire's alphabetically
sorted key order. A valid OCR count interval must therefore NOT contain a
separately evidenced printed article heading, even if that heading has a
different position in the TEI key index. This prevents false huge omissions.

This is a research-only guard: a detected OCR headword is not a visually
verified original title and never authorizes editorial changes.
"""
from collections import Counter, defaultdict
import re

from scripts.research_1915_print_pages import candidate_heading, normalize


def is_strong_print_heading(line, key):
    """Require explicit title typography, not mere uppercase prose mentions.

    The source key sometimes joins separately pronounced printed headwords
    with semicolons (e.g. CHILD; CHILDREN), whereas a printed line
    interposes transliterations before the second capitalized title.
    """
    original = line.strip()
    if len(original) > 190 or not original:
        return False
    parts = [p.strip() for p in key.split(";")]
    if len(parts) > 1:
        if any(not p or len(normalize(p).replace(" ", "")) < 4 for p in parts):
            return False
        first = parts[0]
        # The first printed title is fully uppercase and is followed by
        # its genuine printed pronunciation, not simply words of prose.
        initial = re.match(
            r"^\s*" + re.escape(first) + r"\s*[,:(]\s*",
            original,
        )
        if not initial or first != first.upper():
            return False
        # Every additional separately named title must be visibly uppercase
        # and followed by typographic punctuation, within this SAME OCR line.
        tail = original[initial.end():]
        for part in parts[1:]:
            match = re.search(
                r"(?<![A-Za-z])" + re.escape(part) + r"\s*[,:(]",
                tail,
            )
            if not match or part != part.upper():
                return False
            tail = tail[match.end():]
        return True
    if candidate_heading(original, key) < 4:
        return False
    if normalize(original) == normalize(key):
        return True
    # Single-word headings are common; ignoring comma+pronunciation
    # discarded explicit headings such as ANTICHRIST or COCKATRICE.
    # The existing >=8-letter/uniqueness gate limits incidental mentions.
    return bool(re.match(
        r"^\s*" + re.escape(key) + r"\s*[:,;(]",
        original,
    ))


def strong_intervening_heading_candidates(lines, entries):
    """Recognize rare, unique, well-delimited title lines across all entries.

    High specificity is intentional. A common word matching a dictionary
    index is NOT a trusted start of a separate historical print article.
    Only a unique uppercase headword with structural punctuation, a
    standalone heading, or separately pronounced semicolon-separated source
    aliases qualifies. Duplicate occurrences are left untrusted.
    """
    by_first = defaultdict(list)
    norm_duplicates = Counter(normalize(entry["key"]) for entry in entries)
    for i, entry in enumerate(entries):
        norm = normalize(entry["key"])
        words = norm.split()
        if (not words or sum(map(len, words)) < 8
                or norm_duplicates[norm] != 1):
            continue
        by_first[words[0]].append((i, entry["key"], norm, words))
    hits = defaultdict(list)
    for pos, line in enumerate(lines):
        original = line["text"].strip()
        norm = normalize(original)
        if not norm:
            continue
        for index, key, title, words in by_first.get(norm.split()[0], ()):
            if not is_strong_print_heading(original, key):
                continue
            hits[index].append(pos)
    return [
        {"article_index": index, "line_position": positions[0],
         "source_key": entries[index]["key"],
         "source_article_xml_id": entries[index]["article_xml_id"],
         "scan_pdf_page_1_based": lines[positions[0]]["page"],
         "image_verified": False}
        for index, positions in hits.items() if len(positions) == 1
    ]


def guard_interleaved_headings(lines, entries, accepted, reports):
    """Withdraw only OCR metrics whose source-ordered span hides another title.

    The canonical entry list, original source words, original PDF and the
    identities of all entries are preserved. Multiple independent
    intervening headwords can be retained in a single research record.
    """
    if len(entries) != len(reports):
        raise ValueError("Canonical/OCR article inventory differs")
    potential = strong_intervening_heading_candidates(lines, entries)
    barriers = 0
    for i, row in enumerate(reports):
        if (row["article_key"] != entries[i]["key"]
                or row["article_xml_id"] != entries[i]["article_xml_id"]):
            raise ValueError("Original source article identity drift")
        start, stop = accepted.get(i), accepted.get(i + 1)
        witnesses = []
        if start is not None and stop is not None and start < stop:
            witnesses = [
                {"source_key": h["source_key"],
                 "source_article_xml_id": h["source_article_xml_id"],
                 "scan_pdf_page_1_based": h["scan_pdf_page_1_based"],
                 "image_verified": False}
                for h in potential if (start < h["line_position"] < stop
                    and h["article_index"] not in {i, i + 1})
            ]
        witnesses.sort(key=lambda h: (
            h["scan_pdf_page_1_based"], h["source_key"]
        ))
        row["intervening_print_heading_candidates"] = witnesses
        row["withheld_ocr_span_start_scan_pdf_page_1_based"] = None
        row["withheld_ocr_span_next_heading_scan_pdf_page_1_based"] = None
        if not witnesses:
            continue
        if row["ocr_latin_tokens"] is None:
            # No OCR word-count claim to withdraw from an already unresolved
            # source entry. Keep its status unchanged.
            continue
        row["withheld_ocr_span_start_scan_pdf_page_1_based"] = lines[start]["page"]
        row["withheld_ocr_span_next_heading_scan_pdf_page_1_based"] = lines[stop]["page"]
        for name in (
            "ocr_latin_tokens", "ocr_start_pdf_page", "ocr_end_pdf_page",
            "ocr_to_tei_ratio", "source_fourgram_recall",
            "ocr_fourgram_precision",
        ):
            row[name] = None
        row["status"] = "unresolved_intervening_print_heading"
        barriers += 1
    return reports, barriers
