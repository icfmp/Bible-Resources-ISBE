#!/usr/bin/env python3
"""Validate source-locked *limited* 1915 original-image prose observations.

The handwritten visual readings in the review ledger are independently
recorded. CI does not read the JPEG or certify the entire historical text:
it checks identity, PDF provenance, source fragments and nonapproval gates.
"""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from scripts.audit_1915_article_ocr_word_counts import LOCK, digest
from scripts.research_1915_print_pages import expected_volume

TEI = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"
SHA = re.compile(r"[0-9a-f]{64}")
RUN = re.compile(r"https://github[.]com/icfmp/Bible-Resources-ISBE/actions/runs/[0-9]+")
CLASSES = {
    "misexpanded_abbreviation", "quote_boundary_shift", "punctuation_loss",
    "lexical_substitution", "digitization_marker", "broken_word_expansion",
}
FIELDS = {
    "source_key", "source_article_xml_id", "volume", "pdf_page_1_based",
    "printed_folio", "original_pdf_sha256", "research_jpeg_sha256", "fragments",
    "printed_page_image_visually_inspected", "full_article_prose_verified",
    "correction_authorized", "publication_permitted",
}
FRAGMENT_FIELDS = {
    "digital_source_exact", "printed_visible_reading", "classification",
    "annotation",
}


def validate(ledger, manifest, root, actual_tei_sha256):
    if (actual_tei_sha256 != LOCK or ledger.get("canonical_tei_sha256") != LOCK
            or manifest.get("canonical_tei_sha256") != LOCK
            or ledger.get("schema_version") != 1
            or not RUN.fullmatch(ledger.get("original_print_image_research_run", ""))
            or not isinstance(ledger.get("scope"), str)
            or "not entire article" not in ledger["scope"].lower()
            or ledger.get("original_crosswire_or_canonical_tei_modified") is not False
            or ledger.get("full_article_collation_completed") is not False
            or ledger.get("editorial_corrections_approved") is not False
            or ledger.get("redistribution_authorized") is not False):
        raise ValueError("Unapproved source, scope, textual change or redistribution")
    if root.tag != TEI + "TEI":
        raise ValueError("TEI namespace mismatch")
    body = root.find("./" + TEI + "text/" + TEI + "body")
    if body is None or len(body) != 9380:
        raise ValueError("Canonical source article inventory changed")
    articles = {a.get("n"): a for a in body}
    if len(articles) != 9380:
        raise ValueError("Canonical source keys duplicated")
    volumes = {v["volume"]: v for v in manifest.get("volumes", [])}
    if len(volumes) != 5 or manifest.get("manifest_version") != 1:
        raise ValueError("Historical volume manifest incomplete")
    records = ledger.get("entries")
    if not isinstance(records, list) or not 1 <= len(records) <= 30:
        raise ValueError("No bounded printed-page review observations")
    checked = set()
    total_fragments = 0
    for row in records:
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError("Unexpected review entry fields")
        key = row["source_key"]
        volume = row["volume"]
        source = articles.get(key)
        witness = volumes.get(volume)
        if (not isinstance(key, str) or key in checked
                or source is None or witness is None
                or expected_volume(key) != volume
                or row["source_article_xml_id"] != source.get(ID)
                or row["original_pdf_sha256"] != witness["pdf_sha256"]
                or not isinstance(row["pdf_page_1_based"], int)
                or not 1 <= row["pdf_page_1_based"] <= witness["pages"]
                or not isinstance(row["printed_folio"], int)
                or not 1 <= row["printed_folio"] <= 4000
                or not isinstance(row["research_jpeg_sha256"], str)
                or not SHA.fullmatch(row["research_jpeg_sha256"])
                or row["printed_page_image_visually_inspected"] is not True
                or row["full_article_prose_verified"] is not False
                or row["correction_authorized"] is not False
                or row["publication_permitted"] is not False):
            raise ValueError("Misidentified printed-page or illegal editorial claim")
        checked.add(key)
        fragments = row["fragments"]
        if not isinstance(fragments, list) or not 1 <= len(fragments) <= 5:
            raise ValueError("Each page review needs bounded exact source fragments")
        # Flatten only within this exact source entry. Do not compare a fragment
        # against another article or treat normalized OCR as primary evidence.
        original_article_text = "".join(source.itertext())
        seen = set()
        for fragment in fragments:
            if not isinstance(fragment, dict) or set(fragment) != FRAGMENT_FIELDS:
                raise ValueError("Unexpected fragment metadata")
            digital = fragment["digital_source_exact"]
            printed = fragment["printed_visible_reading"]
            note = fragment["annotation"]
            if (not isinstance(digital, str) or not 10 <= len(digital) <= 160
                    or digital in seen
                    or original_article_text.count(digital) != 1
                    or not isinstance(printed, str) or not 8 <= len(printed) <= 180
                    or digital == printed
                    or fragment["classification"] not in CLASSES
                    or not isinstance(note, str) or not 30 <= len(note) <= 350):
                raise ValueError("Fragment absent, duplicated, fabricated or unbounded")
            seen.add(digital)
            total_fragments += 1
    return {"source_articles_checked": len(checked),
            "bounded_differences_checked": total_fragments,
            "original_source_sha256": LOCK,
            "full_historical_articles_collated": False,
            "textual_corrections_approved": False,
            "publication_permitted": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", type=Path, default=Path(
        "workspace/reviews/1915-low-overlap-prose-image-spotchecks-v1.json"))
    p.add_argument("--manifest", type=Path, default=Path(
        "sources/print/1915-volume-witnesses.json"))
    p.add_argument("--tei", type=Path, default=Path("cleaned/en/ISBE.xml"))
    args = p.parse_args()
    source_sha = digest(args.tei)
    result = validate(
        json.loads(args.ledger.read_text(encoding="utf-8")),
        json.loads(args.manifest.read_text(encoding="utf-8")),
        ET.parse(args.tei).getroot(),
        source_sha,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
