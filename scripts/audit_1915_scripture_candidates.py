#!/usr/bin/env python3
"""Provenance-locked read-only triage of single-verse metadata inconsistencies.

The digital source provides the discrepancy and neighboring paragraph, while
the separately identified 1915 volume OCR offers *research hints only*.
Neither OCR nor a matching heading certifies print content; decisions require
checking the original page image and recording a review ledger.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

from scripts.audit_scripture_ref_display import scan
from scripts.research_1915_print_pages import expected_volume, find_headings, digest

T = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"
LOCK = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"


def make_digital_queue(source):
    report = scan(source)
    if report["input_sha256"] != LOCK or report["articles_scanned"] != 9380:
        raise ValueError("Canonical ISBE witness drift")
    root = ET.parse(source).getroot()
    body = root.find(f"./{T}text/{T}body")
    by_id = {node.get(ID): node for article in body for node in article.iter() if node.get(ID)}
    for case in report["cases"]:
        node = by_id[case["ref_xml_id"]]
        article = next(a for a in body if a.get(ID) == case["article_xml_id"])
        # Retain the full article for stable review and print searching, but
        # expose only short context around the exact reference in the report.
        context = "".join(article.itertext())
        exact = case["visible"]
        spans = [m.start() for m in re.finditer(re.escape(exact), context)]
        case["article_text_sha256"] = sha256(context.encode("utf-8")).hexdigest()
        case["context_candidates"] = [
            context[max(0, pos-180):pos+len(exact)+180] for pos in spans[:6]
        ]
        case["candidate_volume"] = expected_volume(case["article_key"])
        case["print_page_image_collated"] = False
        case["historical_print_status"] = "not_yet_verified"
        case["source_ref_tag"] = node.tag.replace(T, "")
        case["encoded_source_key"] = case["article_key"]
    report["claims_print_certification"] = False
    return report


def attach_ocr_hints(report, pdf, manifest, volume):
    manifest_data = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if manifest_data["canonical_tei_sha256"] != LOCK:
        raise ValueError("Witness manifest mismatch")
    witnesses = [x for x in manifest_data["volumes"] if x["volume"] == str(volume)]
    if len(witnesses) != 1:
        raise ValueError("Unknown print volume")
    witness = witnesses[0]
    if digest(pdf) != witness["pdf_sha256"]:
        raise ValueError("Original 1915 PDF SHA-256 mismatch")
    text = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True, text=True, check=True, timeout=180,
    ).stdout
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if len(pages) != witness["pages"]:
        raise ValueError("Original 1915 PDF page count mismatch")
    keys = sorted({c["article_key"] for c in report["cases"]
                   if c["candidate_volume"] == str(volume)})
    hits = find_headings(pages, keys, max_hits=12)
    for case in report["cases"]:
        if case["candidate_volume"] != str(volume):
            continue
        case["print_ocr_research"] = {
            "volume": str(volume),
            "pdf_sha256": witness["pdf_sha256"],
            "heading_candidates": hits[case["article_key"]],
            "claim_exact_print_text": False,
            "page_image_inspected": False,
        }
    return len(keys)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tei", type=Path, default=Path("cleaned/en/ISBE.xml"))
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--volume")
    p.add_argument("--pdf", type=Path)
    p.add_argument("--witness-manifest", type=Path,
                   default=Path("sources/print/1915-volume-witnesses.json"))
    a = p.parse_args()
    if bool(a.volume) != bool(a.pdf):
        p.error("--volume and --pdf must be provided together")
    report = make_digital_queue(a.tei)
    if a.pdf:
        count = attach_ocr_hints(report, a.pdf, a.witness_manifest, a.volume)
        print("Historical OCR candidate keys, NOT visual certification:", count)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("Candidates:", report["candidate_count"])
    for case in report["cases"]:
        print("REVIEW", json.dumps({
            "key": case["article_key"], "volume": case["candidate_volume"],
            "visible": case["visible"], "cRef": case["cRef"],
            "context_candidates": case["context_candidates"],
            "print_ocr_research": case.get("print_ocr_research"),
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
