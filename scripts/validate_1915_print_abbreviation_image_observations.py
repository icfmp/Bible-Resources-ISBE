#!/usr/bin/env python3
"""Validate limited 1915 printed-page abbreviation observations (no text edits).

Validates SHA-locked canonical source and original printed PDFs, article
identities and expanded phrase presence *in canonical TEI*. It never claims
that an original JPG was itself scanned in CI: image hash/folio observations
are independently preserved for human direct inspection and follow-up.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from scripts.audit_1915_article_ocr_word_counts import LOCK, digest, latin_tokens
from scripts.research_1915_print_pages import expected_volume

SHA = re.compile(r"^[0-9a-f]{64}$")
ACTION = re.compile(r"^https://github\.com/icfmp/Bible-Resources-ISBE/actions/runs/[0-9]+$")
TEI = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"
ALLOWED = {"AV", "AVm", "RV", "RVm", "OT", "NT", "OE", "Heb", "Gr"}


def contiguous(needles, haystack):
    return any(haystack[i:i+len(needles)] == needles
               for i in range(len(haystack) - len(needles) + 1))


def validate(ledger, sources, root, source_sha):
    if (
        source_sha != LOCK
        or ledger.get("canonical_tei_sha256") != LOCK
        or sources.get("canonical_tei_sha256") != LOCK
        or ledger.get("schema_version") != 1
        or ledger.get("text_redistribution_authorized") is not False
        or ledger.get("full_edition_print_certified") is not False
        or not ACTION.fullmatch(ledger.get("original_1915_print_image_workflow", ""))
        or not ACTION.fullmatch(ledger.get("report_reference", ""))
    ):
        raise ValueError("Original source SHA or publication/print-proof scope mismatch")
    witnesses = {v["volume"]: v for v in sources["volumes"]}
    body = root.find(f"./{TEI}text/{TEI}body")
    if len(witnesses) != 5 or body is None or len(body) != 9380:
        raise ValueError("Original source article inventory incomplete")
    indices = {a.attrib["n"]: a for a in body}
    if len(indices) != 9380:
        raise ValueError("Canonical keys duplicate or missing")
    records = ledger.get("entries")
    if not isinstance(records, list) or len(records) != 3:
        raise ValueError("Expected exactly three bounded printed-image observations")
    checked = set()
    result = {}
    for row in records:
        key, volume = row["source_key"], row["volume"]
        src = indices.get(key)
        witness = witnesses.get(volume)
        if (key in checked or src is None or witness is None
                or expected_volume(key) != volume
                or src.get(ID) != row["source_article_xml_id"]
                or row["original_pdf_sha256"] != witness["pdf_sha256"]
                or not SHA.fullmatch(row["research_jpeg_sha256"])
                or not isinstance(row["scan_pdf_page"], int)
                or not 1 <= row["scan_pdf_page"] <= witness["pages"]
                or not isinstance(row["printed_folio"], int)
                or not 1 <= row["printed_folio"] <= 4000
                or row.get("heading_and_typographic_abbreviations_image_reviewed") is not True
                or row.get("full_historical_prose_collation_completed") is not False
                or row.get("source_digital_text_changed") is not False
                or row.get("approved_textual_corrections") != []
                or row.get("publication_permitted") is not False
                or not isinstance(row.get("review_summary"), str)
                or len(row["review_summary"].strip()) < 70):
            raise ValueError("Invented original 1915 article, printed-image hash or editorial approval")
        checked.add(key)
        forms = row["printed_abbreviations_seen"]
        digital = row["digital_expansions_seen"]
        if (not isinstance(forms, list) or len(forms) != len(set(forms))
                or not forms or any(s not in ALLOWED for s in forms)
                or not isinstance(digital, list) or len(digital) != len(forms)
                or len(set(digital)) != len(digital)):
            raise ValueError("Printed abbreviation/display expansions not properly bounded")
        # A finite whitelist guards against treating arbitrary prose as an
        # approved abbreviation. Candidate pairing is observational only.
        witness_forms = {
            "AV": {"King James Version"},
            "AVm": {"King James Version margin"},
            "RV": {"Revised Version (British and American)", "Revised Version"},
            "RVm": {"Revised Version margin", "Revised Version, margin"},
            "OT": {"Old Testament"}, "NT": {"New Testament"},
            "OE": {"Old English"}, "Heb": {"Hebrew"}, "Gr": {"Greek"}
        }
        observed = [
            " ".join(latin_tokens(" ".join(x.itertext())))
            for x in src if not (x.tag == TEI + "head" and x.get("type") == "index")
        ]
        source_words = latin_tokens(" ".join(observed))
        for form, expansion in zip(forms, digital):
            if (expansion not in witness_forms[form]
                    or not contiguous(latin_tokens(expansion), source_words)):
                raise ValueError("Reported printed expansion absent from immutable canonical article")
        result[key] = {
            "volume": volume, "pdf_page": row["scan_pdf_page"],
            "printed_form_count": len(forms), "image_sha256": row["research_jpeg_sha256"],
            "full_article_print_certified": False,
        }
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", type=Path,
                   default=Path("workspace/reviews/1915-print-abbreviation-image-observations-v1.json"))
    p.add_argument("--source-manifest", type=Path,
                   default=Path("workspace/witnesses/print/1915-volume-witnesses.json"))
    p.add_argument("--tei", type=Path, default=Path("workspace/witnesses/crosswire-2.2/ISBE.xml"))
    args = p.parse_args()
    if digest(args.tei) != LOCK:
        raise ValueError("Noncanonical source TEI")
    read = lambda f: json.loads(f.read_text(encoding="utf-8"))
    result = validate(
        read(args.ledger), read(args.source_manifest),
        ET.parse(args.tei).getroot(), digest(args.tei),
    )
    print(json.dumps({
        "original_image_observations_verified": len(result),
        "case_keys": sorted(result),
        "canonical_source_sha256": LOCK,
        "source_or_print_text_published": False,
        "full_print_prose_certified": False,
    }, indent=2))


if __name__ == "__main__":
    main()
