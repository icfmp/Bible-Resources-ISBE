#!/usr/bin/env python3
"""Audit-only equivalence of common CrossWire-expanded printed abbreviations.

Historical ISBE uses abbreviations AV, RV, OT, NT, Heb, Gr, OE, etc.
CrossWire's canonical digital source sometimes spells out those words.
This gives an *additional* research score, not a normalized text, not an
editorial correction and never a substitute for source-image collation.

Only match strictly enumerated full phrase boundaries, and only collapse
a phrase when its compact abbreviation occurs in this same OCR candidate
span. Keep the two witnesses, their original lengths/hashes and the raw
four-token scores completely unchanged.
"""
from collections import Counter

# The printed abbreviated forms below have been directly observed in
# original 1915 facsimiles (for example the ABIDE and REPAIR entries).
# Longer source expressions MUST precede prefixes.
EXPLICIT_SOURCE_TO_PRINT = (
    (("the", "revised", "version", "british", "and", "american", "margin"), "rvm"),
    (("revised", "version", "british", "and", "american", "margin"), "rvm"),
    (("the", "king", "james", "version", "margin"), "avm"),
    (("king", "james", "version", "margin"), "avm"),
    (("the", "revised", "version", "british", "and", "american"), "rv"),
    (("revised", "version", "british", "and", "american"), "rv"),
    (("the", "revised", "version", "margin"), "rvm"),
    (("revised", "version", "margin"), "rvm"),
    (("the", "king", "james", "version"), "av"),
    (("king", "james", "version"), "av"),
    (("the", "revised", "version"), "rv"),
    (("revised", "version"), "rv"),
    (("old", "testament"), "ot"),
    (("new", "testament"), "nt"),
    (("old", "english"), "oe"),
    (("hebrew",), "heb"),
    (("greek",), "gr"),
)


def research_fold_digital_expansions(source_tokens, ocr_tokens):
    """Return separate *derived* tokens and audit counts, never edit source.

    Explicit printed abbreviation token evidence is necessary but not
    sufficient to prove equivalence of any particular historical passage.
    """
    recognized = set(ocr_tokens) & {abbr for _, abbr in EXPLICIT_SOURCE_TO_PRINT}
    result = []
    matches = Counter()
    at = 0
    while at < len(source_tokens):
        selected = None
        for expression, abbrev in EXPLICIT_SOURCE_TO_PRINT:
            if (abbrev in recognized
                    and tuple(source_tokens[at:at+len(expression)]) == expression):
                selected = (expression, abbrev)
                break
        if selected is None:
            result.append(source_tokens[at])
            at += 1
        else:
            expression, abbrev = selected
            result.append(abbrev)
            matches[abbrev] += 1
            at += len(expression)
    return result, dict(sorted(matches.items()))


def research_abbreviation_effect(source_tokens, ocr_tokens, raw_fourgram, recall):
    """Only a score differential; raw four-gram finding is always retained."""
    if raw_fourgram is None or len(source_tokens) < 4 or len(ocr_tokens) < 4:
        return None
    derived, evidence = research_fold_digital_expansions(source_tokens, ocr_tokens)
    folded = recall(derived, ocr_tokens, 4)
    if folded is None:
        return None
    return {
        "raw_source_fourgram_recall": raw_fourgram,
        "derived_abbreviation_equivalence_fourgram_recall": folded,
        "derived_minus_raw_fourgram_recall": round(folded - raw_fourgram, 4),
        "source_expressions_compacted_by_print_abbreviation": evidence,
        "diagnostic_source_derived_token_count": len(derived),
        "original_tei_and_ocr_text_unchanged": True,
        "printed_abbreviation_matches_are_not_image_certifications": True,
        "publication_permitted": False,
    }
