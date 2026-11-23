#!/usr/bin/env python3
"""Build a separately versioned, second-pass visually reviewed 1915 ISBE TEI.

The CrossWire-derived canonical source is immutable. Printed-text approval
is separate from independent human review and redistribution permission.
"""
import argparse
import hashlib
import json
from pathlib import Path

from preview_print_prose import apply
from validate_prose_preview_profile import validate

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "workspace" / "reviews"
EXPECTED_SOURCE = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def approved_records(approval, prose, redirects, visual):
    """Fail closed on every wrong source, missing entry, or changed reading."""
    if approval["canonical_source_sha256"] != EXPECTED_SOURCE:
        raise ValueError("Second-pass record refers to a different source")
    if approval["legal_redistribution_clearance"] or approval["published"]:
        raise ValueError("Text approval does not confer redistribution rights")
    if approval["independent_human_peer_review"]:
        raise ValueError("No independent human peer review is documented")
    pages = {r["source_key"]: r for r in visual["records"]}
    p = {r["source_key"]: r for r in prose["records"]}
    d = {r["article_key"]: r for r in redirects["records"]}
    if len(p) != 20 or len(d) != 11 or set(p) & set(d):
        raise ValueError("Unexpected restoration candidate population")
    if len(pages) != 31 or len(approval["records"]) != 31:
        raise ValueError("Missing original image evidence or approval")
    if approval["source_empty_entries_recovered"] != 31:
        raise ValueError("Incorrect approval population")
    seen = set()
    for row in approval["records"]:
        key = row["source_key"]
        if key in seen or key not in (set(p) | set(d)):
            raise ValueError(f"Unexpected or repeated approval: {key}")
        seen.add(key)
        if row["second_pass_visual_reading"] != "matches_proposed_text":
            raise ValueError(f"Unverified second pass: {key}")
        if row["approved_for_separate_editorial_tei"] is not True:
            raise ValueError(f"Unapproved recovery: {key}")
        page = pages[key]
        if (
            row["source_paragraph_xml_id"] != page["original_source_paragraph_xml_id"]
            or row["scan_volume"] != page["scan_volume"]
            or row["original_pdf_page_1_based"] != page["pdf_page_1_based"]
            or row["printed_page"] != page["printed_page_number"]
            or row["source_pdf_sha256"] != page["original_pdf_sha256"]
            or row["rendered_image_sha256"] != page["rendered_jpeg_sha256"]
            or row["evidence_workflow_run"] != page["evidence_workflow_run"]
            or not page["visual_page_inspected"]
        ):
            raise ValueError(f"Source page identity or digest mismatch: {key}")
        if key in p:
            c = p[key]
            if row["kind"] != "prose" or row["approved_blocks"] != c["blocks"]:
                raise ValueError(f"Printed prose transcription changed after visual review: {key}")
            if row["source_paragraph_xml_id"] != c["source_paragraph_id"]:
                raise ValueError(f"Source paragraph mismatch: {key}")
        else:
            c = d[key]
            if (
                row["kind"] != "redirect"
                or row["approved_printed_paragraph"] != c["proposed_print_collated_text"]
                or row["source_paragraph_xml_id"] != c["original_empty_paragraph_id"]
            ):
                raise ValueError(f"Printed redirect transcription changed: {key}")
    if seen != (set(p) | set(d)):
        raise ValueError(f"Missing second-pass approvals: {sorted((set(p) | set(d)) - seen)}")
    return len(seen)


def finalize(source, output, report_path, manifest_path, fidelity_path, approvals_path=None):
    source = Path(source)
    if hashlib.sha256(source.read_bytes()).hexdigest() != EXPECTED_SOURCE:
        raise ValueError("Canonical source has changed")
    approvals_path = Path(approvals_path or REVIEWS / "1915-second-pass-visual-approval-v1.json")
    approval = read(approvals_path)
    prose = read(REVIEWS / "print-prose-candidate-v1.json")
    redirects = read(REVIEWS / "redirect-candidate-v1.json")
    visual = read(REVIEWS / "1915-visual-page-collation-v1.json")
    count = approved_records(approval, prose, redirects, visual)
    result = apply(
        source, REVIEWS / "redirect-candidate-v1.json",
        REVIEWS / "print-prose-candidate-v1.json", output, report_path
    )
    # The historical review-only generator remains conservative. Only this
    # separately checked edition carries the second-pass editorial decision.
    result.update({
        "edition_status": "second_visual_pass_print_transcription_approved",
        "second_pass_approved_entries": count,
        "human_independent_peer_review": False,
        "original_canonical_unchanged": True,
        "publication_permitted": False,
        "editorial_decision_manifest": str(approvals_path.relative_to(ROOT)),
    })
    Path(report_path).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fidelity = validate(
        source, output, report_path,
        ROOT / "workspace/changes/tei-p5-candidate-v1.json",
        manifest_path, fidelity_path
    )
    fidelity["historical_print_page_images"] = "SECOND_VISUAL_PASS_REVIEWED"
    fidelity["approved_text_modifications"] = count
    fidelity["independent_human_peer_review"] = False
    fidelity["publication_permitted"] = False
    Path(fidelity_path).write_text(json.dumps(fidelity, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="cleaned/en/ISBE.xml")
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--validator-manifest", required=True)
    parser.add_argument("--fidelity-report", required=True)
    args = parser.parse_args()
    output = finalize(args.source, args.output, args.report,
                      args.validator_manifest, args.fidelity_report)
    print(json.dumps(output, indent=2))
