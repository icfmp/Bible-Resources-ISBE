#!/usr/bin/env python3
"""Read-only source-locked verification of printed-vs-digital ISBE contrasts."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

TEI="{http://www.tei-c.org/ns/1.0}"
XML_ID="{http://www.w3.org/XML/1998/namespace}id"
SOURCE_SHA="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
REVIEW_STATUS="primary_print_folio_visually_checked_ai_assisted_not_full_article"

def check(tei_path, ledger_path):
    raw=Path(tei_path).read_bytes()
    ledger=json.loads(Path(ledger_path).read_text(encoding="utf-8"))
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA or ledger.get("canonical_sha256")!=SOURCE_SHA:
        raise ValueError("Unapproved canonical source digest")
    if ledger.get("schema_version")!=1:
        raise ValueError("Unknown editorial review schema")
    root=ET.fromstring(raw)
    body=root.find(f"./{TEI}text/{TEI}body")
    if root.tag!=TEI+"TEI" or body is None:
        raise ValueError("Missing canonical TEI")
    articles={}
    for article in body:
        key=article.get("n")
        if not key or not article.get(XML_ID) or key in articles:
            raise ValueError("Missing or duplicate source article")
        articles[key]=article
    if len(articles)!=9380:
        raise ValueError("Unexpected article coverage")
    manifest=json.loads((Path(__file__).resolve().parents[1]/
        "sources/print/1915-volume-witnesses.json").read_text(encoding="utf-8"))
    volumes={v["volume"]:v for v in manifest["volumes"]}
    out=[]
    anchors=set()
    for case in ledger["cases"]:
        key,anchor=case["source_key"],case["source_text_exact"]
        if not anchor or not case.get("printed_text_reading") or (key,anchor) in anchors:
            raise ValueError("Invalid or duplicate source anchor")
        anchors.add((key,anchor))
        if case.get("approved") is not False or case.get("proposed_change") is not None:
            raise ValueError("Comparison ledger cannot authorize editorial text changes")
        if case.get("review_status")!=REVIEW_STATUS:
            raise ValueError("Witness status must not be overstated")
        witness=volumes.get(case.get("print_volume"))
        if witness is None or case.get("original_pdf_sha256")!=witness["pdf_sha256"]:
            raise ValueError("Original full-volume print SHA mismatch")
        page=case.get("primary_pdf_page_1_based")
        if not isinstance(page,int) or not 1<=page<=witness["pages"]:
            raise ValueError("Invalid original printed-page index")
        image_sha=case.get("rendered_jpeg_sha256")
        if (not isinstance(image_sha,str) or len(image_sha)!=64
                or any(c not in "0123456789abcdef" for c in image_sha)):
            raise ValueError("Missing original printed-page image digest")
        article=articles[key]
        matches=[]
        for node in article.iter():
            if node.tag not in (TEI+"p",TEI+"head"):
                continue
            value="".join(node.itertext())
            if anchor in value:
                matches.append((node,value))
        if len(matches)!=1 or matches[0][1].count(anchor)!=1:
            raise ValueError(f"Missing or ambiguous source anchor: {key}: {anchor}")
        node,value=matches[0]
        if not node.get(XML_ID):
            raise ValueError("Missing stable source unit identifier")
        if case.get("source_unit_xml_id") != node.get(XML_ID):
            raise ValueError("Original source unit identifier drift")
        out.append({"source_key":key,"article_xml_id":article.get(XML_ID),
                    "unit_xml_id":node.get(XML_ID),
                    "unit_text_sha256":hashlib.sha256(value.encode("utf-8")).hexdigest(),
                    "source_text_exact":anchor,"printed_text_reading":case["printed_text_reading"],
                    "difference_type":case["difference_type"],"witness_url":case["witness_url"],
                    "print_volume":case["print_volume"],"printed_folio":case["printed_folio"],
                    "primary_pdf_page_1_based":page,"original_pdf_sha256":witness["pdf_sha256"],
                    "rendered_jpeg_sha256":image_sha,"primary_evidence_workflow":case["primary_evidence_workflow"],
                    "review_status":case["review_status"],"approved":False})
    return {"canonical_sha256":SOURCE_SHA,"article_count":len(articles),
            "case_count":len(out),"approved_change_count":0,"cases":out}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tei",default="cleaned/en/ISBE.xml")
    p.add_argument("--ledger",default="workspace/reviews/1915-nonempty-contrast-v1.json")
    p.add_argument("--report",required=True)
    a=p.parse_args()
    report=check(a.tei,a.ledger)
    output=Path(a.report)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for row in report["cases"]:
        print("CONTRAST",row["source_key"],row["unit_xml_id"],
              repr(row["source_text_exact"]), "vs", repr(row["printed_text_reading"]))
    print("PASS: original and canonical texts unchanged; no approved corrections")

if __name__=="__main__":
    main()
