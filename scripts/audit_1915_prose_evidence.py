#!/usr/bin/env python3
"""Audit *provenance*, not typography, of the 20 provisional 1915 ISBE prose articles.

Output is reproducible and read-only. A page previously viewed is NOT a
character-level collation. No candidate approval or canonical TEI change.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "workspace" / "reviews"
EXPECTED_SHA = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def unique(rows, key):
    result = {}
    for row in rows:
        label = row[key]
        if label in result:
            raise ValueError("Duplicate article: " + str(label))
        result[label] = row
    return result


def audit(root=ROOT):
    root = Path(root)
    review = root / "workspace" / "reviews"
    prose = load(review / "print-prose-candidate-v1.json")
    pages = load(review / "1915-visual-page-collation-v1.json")
    ledger = load(review / "empty-article-recovery-ledger.json")
    sources = load(root / "workspace" / "witnesses" / "print" / "1915-volume-witnesses.json")
    digest = hashlib.sha256((root / "workspace" / "witnesses" / "crosswire-2.2" / "ISBE.xml").read_bytes()).hexdigest()
    locked = (EXPECTED_SHA, prose["document_base_sha256"],
              pages["canonical_source_sha256"],
              ledger["baseline_canonical_tei_sha256"],
              sources["canonical_tei_sha256"])
    if len(set(locked + (digest,))) != 1:
        raise ValueError("Canonical SHA lock mismatch")
    if not prose["prohibited_canonical_promotion"] or prose["rights_status"] != "not cleared":
        raise ValueError("Unsafe editorial or legal status")
    entries = unique(prose["records"], "source_key")
    inspected = unique(pages["records"], "source_key")
    cases = unique(ledger["cases"], "source_key")
    volumes = unique(sources["volumes"], "volume")
    if len(entries) != 20 or len(inspected) != 31 or len(cases) != 31 or len(volumes) != 5:
        raise ValueError("Unexpected baseline corpus coverage")
    if set(entries) - set(inspected) or set(entries) - set(cases):
        raise ValueError("Unlocated prose article")
    out = []
    for key, candidate in sorted(entries.items()):
        page = inspected[key]
        case = cases[key]
        volume = volumes[page["scan_volume"]]
        if candidate["source_paragraph_id"] != page["original_source_paragraph_xml_id"]:
            raise ValueError("Page/article ID mismatch: " + key)
        if candidate["source_paragraph_id"] != case["paragraph_xml_id"]:
            raise ValueError("Ledger/article ID mismatch: " + key)
        if volume["pdf_sha256"] != page["original_pdf_sha256"]:
            raise ValueError("Historical PDF SHA mismatch: " + key)
        if not (1 <= page["pdf_page_1_based"] <= volume["pages"]):
            raise ValueError("Historical PDF page out of bounds: " + key)
        if not page["visual_page_inspected"] or not case["print_image_reviewed"]:
            raise ValueError("Unverified page inspection claim: " + key)
        if not page["rendered_jpeg_sha256"] or len(page["rendered_jpeg_sha256"]) != 64:
            raise ValueError("Missing image digest: " + key)
        if any((candidate["approved"], candidate["print_text_fully_certified"],
                page["all_text_punctuation_and_foreign_script_certified"],
                page["canonical_modification_approved"],
                case["source_recovery_approved"],
                case["print_transcription_fully_certified"])):
            raise ValueError("Unexpected promotion or certification: " + key)
        if candidate["print_page_inspection_status"] != "visually_inspected_not_fully_text_collated":
            raise ValueError("Misleading page review status: " + key)
        if candidate["full_transcription_review"] != "pending_character_level_1915_fidelity_review":
            raise ValueError("Misleading full-text certification: " + key)
        blocks = candidate["blocks"]
        if not blocks or any(not isinstance(block, str) or not block.strip() for block in blocks):
            raise ValueError("Missing candidate prose: " + key)
        text = "\n".join(blocks)
        out.append({
            "source_key": key,
            "source_paragraph_xml_id": candidate["source_paragraph_id"],
            "candidate_source_status": candidate["source_status"],
            "candidate_block_count": len(blocks),
            "candidate_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "printed_volume": page["scan_volume"],
            "printed_folio": page["printed_page_number"],
            "pdf_page_1_based": page["pdf_page_1_based"],
            "original_pdf_sha256": page["original_pdf_sha256"],
            "rendered_page_jpeg_sha256": page["rendered_jpeg_sha256"],
            "visual_evidence_workflow": page["evidence_workflow_run"],
            "contains_hebrew": any("\u0590" <= ch <= "\u05ff" for ch in text),
            "contains_greek": any("\u0370" <= ch <= "\u03ff" or "\u1f00" <= ch <= "\u1fff" for ch in text),
            "review_status": "primary_print_page_visually_inspected__full_text_not_collated",
            "editorial_approval": False,
        })
    return {
        "schema_version": 1,
        "scope": "Provenance and candidate integrity only, NOT character-level comparison with printed page images",
        "canonical_source_sha256": digest,
        "prose_articles": len(out),
        "fully_certified_articles": 0,
        "rights_cleared": False,
        "records": out,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit()
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
