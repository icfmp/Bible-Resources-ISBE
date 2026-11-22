#!/usr/bin/env python3
"""Generate a reproducible, NONCANONICAL per-entry recovery delta manifest.

The original CrossWire-derived TEI is read-only. An image having been viewed
is not equivalent to a character-certified 1915 transcription.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = "{http://www.tei-c.org/ns/1.0}"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text_sha(text):
    return sha(text.encode("utf-8"))


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build(root=ROOT):
    root = Path(root)
    reviews = root / "workspace/reviews"
    canonical_path = root / "cleaned/en/ISBE.xml"
    original = canonical_path.read_bytes()
    baseline = sha(original)
    ledger = read(reviews / "empty-article-recovery-ledger.json")
    visual = read(reviews / "1915-visual-page-collation-v1.json")
    prose = read(reviews / "print-prose-candidate-v1.json")
    redirects = read(reviews / "redirect-candidate-v1.json")
    for source_hash in (ledger["baseline_canonical_tei_sha256"],
                        visual["canonical_source_sha256"],
                        prose["document_base_sha256"],
                        redirects["canonical_sha256"]):
        if source_hash != baseline:
            raise ValueError("Source witness digest drift")
    body = ET.fromstring(original).find("./" + NS + "text/" + NS + "body")
    if body is None or len(body) != 9380:
        raise ValueError("Missing or incomplete original corpus")
    articles = {a.get("n"): a for a in body}
    if len(articles) != 9380:
        raise ValueError("Duplicate article source key")
    page_by_key = {r["source_key"]: r for r in visual["records"]}
    case_by_key = {r["source_key"]: r for r in ledger["cases"]}
    if len(page_by_key) != 31 or len(case_by_key) != 31:
        raise ValueError("Duplicate or missing print evidence")
    candidates = {}
    for row in prose["records"]:
        key = row["source_key"]
        if key in candidates:
            raise ValueError("Duplicate recovery candidate")
        candidates[key] = ("prose", row["source_paragraph_id"], row, row["blocks"])
    for row in redirects["records"]:
        key = row["article_key"]
        if key in candidates:
            raise ValueError("Duplicate recovery candidate")
        text = row.get("proposed_print_collated_text") or row["observed_secondary_witness_text"]
        candidates[key] = ("redirect", row["original_empty_paragraph_id"], row, [text])
    if len(candidates) != 31 or set(candidates) != set(page_by_key) or set(candidates) != set(case_by_key):
        raise ValueError("Incomplete 31-entry source-to-print mapping")

    entries = []
    for key in sorted(candidates):
        kind, paragraph_id, candidate, blocks = candidates[key]
        page, case, article = page_by_key[key], case_by_key[key], articles.get(key)
        if article is None:
            raise ValueError(f"No original article {key}")
        ps = [p for p in article.iter() if p.tag == NS + "p"]
        if len(ps) != 1 or ps[0].get(XMLID) != paragraph_id:
            raise ValueError(f"Source paragraph mismatch: {key}")
        if "".join(ps[0].itertext()) != "" or len(ps[0]):
            raise ValueError(f"Original source is not empty: {key}")
        if paragraph_id != case["paragraph_xml_id"] or paragraph_id != page["original_source_paragraph_xml_id"]:
            raise ValueError(f"Evidence identity drift: {key}")
        if not page["visual_page_inspected"] or not case["print_image_reviewed"]:
            raise ValueError(f"Original print page uninspected: {key}")
        if (candidate["approved"] or candidate["print_text_fully_certified"]
                or case["source_recovery_approved"] or page["canonical_modification_approved"]
                or page["all_text_punctuation_and_foreign_script_certified"]):
            raise ValueError(f"Unreviewed approval transition: {key}")
        if not blocks or any(not isinstance(t, str) or not t.strip() for t in blocks):
            raise ValueError(f"Empty candidate text: {key}")
        entries.append({
            "source_key": key,
            "original_paragraph_xml_id": paragraph_id,
            "candidate_type": kind,
            "original_text_sha256": text_sha(""),
            "candidate_block_sha256": [text_sha(block) for block in blocks],
            "candidate_block_count": len(blocks),
            "volume": page["scan_volume"],
            "printed_page": page["printed_page_number"],
            "pdf_page_1_based": page["pdf_page_1_based"],
            "source_pdf_sha256": page["original_pdf_sha256"],
            "page_jpeg_sha256": page["rendered_jpeg_sha256"],
            "evidence_workflow_run": page["evidence_workflow_run"],
            "page_visually_inspected": True,
            "complete_transcription_certified": False,
            "canonical_change_approved": False,
        })
    return {
        "schema_version": 1,
        "purpose": "Unapproved candidate deltas, not a transcript certification or publication authorization",
        "canonical_source_sha256": baseline,
        "original_article_count": 9380,
        "affected_originally_empty_articles": len(entries),
        "candidate_prose": sum(x["candidate_type"] == "prose" for x in entries),
        "candidate_redirects": sum(x["candidate_type"] == "redirect" for x in entries),
        "source_print_pages": len({(x["volume"], x["printed_page"]) for x in entries}),
        "entries": entries,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON report location")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
