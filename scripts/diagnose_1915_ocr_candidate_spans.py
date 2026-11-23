#!/usr/bin/env python3
"""Read-only, provenance-preserving diagnostics for 1915 OCR anomaly queues.

Only the *existing*, conservatively bounded article OCR spans are examined.
Source text and historical OCR prose never enter serialized reports. An OCR
span that has many more tokens than a TEI article can cross an unrecognized
historical heading; numerical and lexical matches cannot certify print text.
"""
from collections import Counter, defaultdict
from hashlib import sha256
import math


def shatokens(tokens):
    return sha256(" ".join(tokens).encode("utf-8")).hexdigest()


def multiset_recall(source, observed, n):
    """Multiset token n-gram overlap, retaining repeated phrases."""
    if len(source) < n or len(observed) < n:
        return None
    left = Counter(tuple(source[i:i+n]) for i in range(len(source)-n+1))
    right = Counter(tuple(observed[i:i+n]) for i in range(len(observed)-n+1))
    return round(sum((left & right).values()) / (len(source)-n+1), 4)


def diagnostic_category(row):
    """One of the two PR #60 queues, or no targeted review."""
    words = row["tei_latin_tokens"]
    observed = row["ocr_latin_tokens"]
    recall = row["source_fourgram_recall"]
    if observed is None or words < 100 or recall is None:
        return None
    if row["status"] == "ocr_count_near_source_candidate" and recall < 0.25:
        return "similar_length_low_phrase_overlap"
    if (row["status"] == "ocr_count_diff_over_10pct_candidate"
            and observed >= 2 * words and recall >= 0.6):
        return "long_ocr_span_source_phrases_present"
    return None


def dense_unique_fourgram_window(source, observed, page_by_token):
    """Locate the tightest interval containing >=80% of uniquely matched 4-grams.

    A source four-gram must occur exactly once in BOTH witnesses. Other
    repeated/common phrases cannot supply false evidence of localization.
    The result is a *candidate* overlap footprint, not a source collation.
    """
    if len(source) < 4 or len(observed) < 4:
        return None
    own = Counter(tuple(source[i:i+4]) for i in range(len(source)-3))
    qualifying = {g for g, c in own.items() if c == 1}
    observed_positions = defaultdict(list)
    for pos in range(len(observed)-3):
        gram = tuple(observed[pos:pos+4])
        if gram in qualifying:
            observed_positions[gram].append(pos)
    positions = sorted(
        locations[0] for gram, locations in observed_positions.items()
        if len(locations) == 1
    )
    if len(positions) < 12:
        return None
    count = max(12, math.ceil(0.8 * len(positions)))
    best = min(
        ((positions[i + count - 1] + 4 - positions[i], positions[i],
          positions[i + count - 1] + 3)
         for i in range(len(positions) - count + 1)),
        key=lambda x: (x[0], x[1]),
    )
    size, first, last = best
    return {
        "matched_unique_fourgrams": len(positions),
        "window_80pct_matched_fourgrams": count,
        "window_first_ocr_token_offset": first,
        "window_last_ocr_token_offset": last,
        "window_length_latin_tokens": size,
        "window_fraction_of_full_ocr_span": round(size / len(observed), 4),
        "window_first_scan_pdf_page_1_based": page_by_token[first],
        "window_last_scan_pdf_page_1_based": page_by_token[last],
        "source_print_fidelity_certified": False,
    }


def diagnose_candidates(lines, entries, heading_positions, rows, tokenize):
    """Give every queued 24+9-type case reproducible, nontextual evidence.

    Arguments are the exact in-memory lines/headings/TEI article material
    from the same SHA-locked volume pipeline, not a second download or OCR.
    """
    if len(entries) != len(rows):
        raise ValueError("Source and OCR result article inventories disagree")
    out = []
    for i, (entry, row) in enumerate(zip(entries, rows)):
        if (entry["key"] != row["article_key"]
                or entry["article_xml_id"] != row["article_xml_id"]):
            raise ValueError("Source/OCR row identity drift")
        category = diagnostic_category(row)
        if category is None:
            continue
        begin, end = heading_positions.get(i), heading_positions.get(i + 1)
        if begin is None or end is None or end <= begin:
            raise ValueError("Queued OCR anomaly has unverified article boundaries")
        raw_tokens, pages = [], []
        page_counts = Counter()
        for line in lines[begin:end]:
            words = tokenize(line["text"])
            raw_tokens.extend(words)
            pages.extend([line["page"]] * len(words))
            page_counts[line["page"]] += len(words)
        heading_length = len(tokenize(entry["key"]))
        ocr = raw_tokens[heading_length:]
        page_by_token = pages[heading_length:]
        source = entry.get("source_latin_tokens")
        if (source is None or len(source) != row["tei_latin_tokens"]
                or len(ocr) != row["ocr_latin_tokens"]):
            raise ValueError("Reported candidate OCR count differs from exact span")
        gram3 = multiset_recall(source, ocr, 3)
        gram2 = multiset_recall(source, ocr, 2)
        gram1 = multiset_recall(source, ocr, 1)
        gram4 = multiset_recall(source, ocr, 4)
        if gram4 != row["source_fourgram_recall"]:
            raise ValueError("Existing four-gram recall cannot be reproduced")
        # Calculate high-discrimination 4-gram localization without
        # publishing historic wording or using a guessed page target.
        localized = dense_unique_fourgram_window(source, ocr, page_by_token)
        start_page = lines[begin]["page"]
        end_page = lines[end]["page"]
        if end_page < start_page:
            raise ValueError("Printed OCR span runs backwards")
        if page_counts and (min(page_counts) < start_page or max(page_counts) > end_page):
            raise ValueError("Printed page distribution is not inside known heading range")
        out.append({
            "source_key": entry["key"],
            "article_xml_id": entry["article_xml_id"],
            "review_queue": category,
            "source_latin_token_count": len(source),
            "candidate_ocr_latin_token_count": len(ocr),
            "source_tokens_sha256": shatokens(source),
            "ocr_candidate_tokens_sha256": shatokens(ocr),
            "initial_heading_scan_pdf_page_1_based": start_page,
            "next_known_heading_scan_pdf_page_1_based": end_page,
            "next_source_article_key": entries[i+1]["key"],
            "span_pdf_page_count_inclusive": end_page - start_page + 1,
            "ocr_word_count_by_scan_page": [
                {"scan_pdf_page_1_based": p, "ocr_tokens_in_page_segment": n}
                for p, n in sorted(page_counts.items())
            ],
            "tei_token_unigram_recall": gram1,
            "tei_token_bigram_recall": gram2,
            "tei_token_trigram_recall": gram3,
            "tei_token_fourgram_recall": gram4,
            "unique_fourgram_overlap_footprint": localized,
            "candidate_ocr_span_not_an_original_print_certification": True,
            "print_page_images_directly_compared": False,
            "textual_correction_authorized": False,
            "publication_permitted": False,
        })
    out.sort(key=lambda row: (row["review_queue"], row["source_key"]))
    return out
