#!/usr/bin/env python3
"""Validate limited visual-printed-heading observations, not article text.

The index keys and XML IDs come from the preserved canonical source
index; PDF SHA locks come from exact 1915 printed source manifest.
A SHA-named, visually inspected page is evidence only for the
recorded headings. This does NOT establish that article prose is
complete, correct or publishable.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from scripts.research_1915_print_pages import expected_volume

SHA = re.compile(r"^[0-9a-f]{64}$")
EVIDENCE_URL = re.compile(
    r"^https://github\.com/icfmp/Bible-Resources-ISBE/actions/runs/[1-9][0-9]*$"
)
CATEGORIES = {
    "visually_confirmed_intervening_print_article",
    "visually_checked_heading_boundary_no_intervening_print_article_seen",
    "visually_confirmed_midpage_alphabetic_section_break",
}


def validate(ledger, source_manifest, article_index):
    lock = source_manifest["canonical_tei_sha256"]
    if (
        ledger["original_canonical_tei_sha256"] != lock
        or ledger.get("schema_version") not in {1, 2}
        or ledger.get("full_article_text_collation_performed") is not False
        or ledger.get("redistribution_authorized") is not False
        or ledger.get("original_crosswire_and_canonical_tei_changed") is not False
        or ledger.get("printed_page_images_visually_inspected") is not True
        or not EVIDENCE_URL.fullmatch(ledger.get("evidence_workflow", ""))
        or not isinstance(ledger.get("records"), list)
        or not ledger["records"]
    ):
        raise ValueError("Visual inspection ledger claims unearned text or legal status")
    volumes = {w["volume"]: w for w in source_manifest["volumes"]}
    if len(volumes) != 5:
        raise ValueError("Unexpected original five-volume source inventory")
    by_key = {a["key"]: a for a in article_index}
    if len(by_key) != 9380 or len(article_index) != 9380:
        raise ValueError("Untrustworthy canonical digital article index")
    seen = set()
    outcome = {}
    for record in ledger["records"]:
        key = record["source_key"]
        article = by_key.get(key)
        volume = record["volume"]
        if (key in seen or article is None
                or volume not in volumes
                or expected_volume(key) != volume
                or article["id"] != record["source_article_xml_id"]
                or record["source_pdf_sha256"] != volumes[volume]["pdf_sha256"]
                or record["classification"] not in CATEGORIES
                or record["heading_image_reviewed"] is not True
                or any(record.get(field) is not False for field in (
                    "full_article_text_collated", "print_content_certified",
                    "editorial_correction_approved", "publication_permitted"
                ))):
            raise ValueError("Unverified original printed heading or invented source ID")
        seen.add(key)
        if not isinstance(record.get("observed_boundary"), str) or len(
                record["observed_boundary"].strip()) < 45:
            raise ValueError("Visual claim lacks specific documented limits")
        pages = record.get("pages")
        if not isinstance(pages, list) or not pages:
            raise ValueError("Original page-image witnesses absent")
        physical = [p["pdf_page_1_based"] for p in pages]
        if physical != sorted(set(physical)):
            raise ValueError("Duplicate or reordered printed page images")
        for image in pages:
            if (not isinstance(image["pdf_page_1_based"], int)
                    or not 1 <= image["pdf_page_1_based"] <= volumes[volume]["pages"]
                    or not isinstance(image["printed_folio"], int)
                    or not 1 <= image["printed_folio"] <= 4000
                    or not SHA.fullmatch(image["image_sha256"])):
                raise ValueError("Visual printed page or JPEG evidence impossible")
        start = record["initial_candidate_pdf_page"]
        if start != physical[0]:
            raise ValueError("Printed article heading not visually evidenced")
        other = record.get("intervening_source_key")
        other_id = record.get("intervening_source_article_xml_id")
        end = record.get("incorrect_digital_next_heading_pdf_page")
        if record["classification"] == "visually_confirmed_intervening_print_article":
            if (not other or other == key or other not in by_key
                    or other_id != by_key[other]["id"]
                    or expected_volume(other) != volume
                    or not isinstance(end, int)
                    or end not in physical or end < start
                    or len(pages) < 1):
                raise ValueError("Original intervening printed heading not evidenced")
        elif record["classification"] == "visually_confirmed_midpage_alphabetic_section_break":
            if (other is not None or other_id is not None or end is not None
                    or len(pages) != 1
                    or not key[0].isupper()):
                raise ValueError("Midpage letter-section review invented a source entry")
        elif other is not None or other_id is not None or end is not None:
            raise ValueError("Non-conflicting print review invents another article")
        outcome[record["classification"]] = outcome.get(record["classification"], 0) + 1
    return {
        "case_count": len(seen),
        "categories": dict(sorted(outcome.items())),
        "source_tei_sha256": lock,
        "textual_corrections_authorized": 0,
        "publication_permitted": False,
    }


def validate_supersession(v2, original):
    """The earlier image observations may be extended, NEVER retroactively edited."""
    if (
        original.get("schema_version") != 1
        or v2.get("schema_version") != 2
        or v2.get("supersedes")
        != "workspace/reviews/1915-ocr-print-heading-visual-inspection-v1.json"
        or v2.get("original_canonical_tei_sha256")
        != original.get("original_canonical_tei_sha256")
        or v2.get("records", [])[:len(original["records"])] != original["records"]
        or len(v2.get("records", [])) <= len(original["records"])
    ):
        raise ValueError("Visual print review edited or lost older source image evidence")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", type=Path, default=Path(
        "workspace/reviews/1915-ocr-print-heading-visual-inspection-v2.json"))
    p.add_argument("--original-ledger", type=Path, default=Path(
        "workspace/reviews/1915-ocr-print-heading-visual-inspection-v1.json"))
    p.add_argument("--source-manifest", type=Path, default=Path(
        "workspace/witnesses/print/1915-volume-witnesses.json"))
    p.add_argument("--article-index", type=Path, default=Path(
        "workspace/witnesses/crosswire-2.2/article-index.json"))
    a = p.parse_args()
    def read(path):
        return json.loads(path.read_text(encoding="utf-8"))
    ledger = read(a.ledger)
    if ledger.get("schema_version") == 2:
        validate_supersession(ledger, read(a.original_ledger))
    result = validate(ledger, read(a.source_manifest), read(a.article_index))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
