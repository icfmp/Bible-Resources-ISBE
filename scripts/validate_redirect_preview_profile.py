#!/usr/bin/env python3
"""Bridge the independently checked review specimen to official P5 schema gates.

This is NOT canonical promotion. It builds temporary validator inputs only
when the precisely declared editorial exceptions and serialized ISBE profile
have been checked, and preserves the pinned TEI 4.12.0 schema provenance.
"""
import argparse
import hashlib
import json
from pathlib import Path
from audit_tei_structure import analyze

EXPECTED_SOURCE="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"

def prepare(source, candidate, change_report, original_manifest, manifest_out, report_out):
    source,candidate=Path(source),Path(candidate)
    report=json.loads(Path(change_report).read_text(encoding="utf-8"))
    if hashlib.sha256(source.read_bytes()).hexdigest()!=EXPECTED_SOURCE:
        raise ValueError("Canonical witness changed")
    if report["source_sha256"]!=EXPECTED_SOURCE or report["noncanonical"] is not True:
        raise ValueError("Incorrect source lock or publication status")
    if report["candidate_sha256"]!=hashlib.sha256(candidate.read_bytes()).hexdigest():
        raise ValueError("Serialized preview differs from proof")
    if report["changed_articles"]!=11 or report["untouched_articles_verified"]!=9369:
        raise ValueError("Article-level parity incomplete")
    if report["proposed_links_unresolved"] or report["original_ids_preserved"] is not True:
        raise ValueError("Missing targets or source XML IDs")
    if len(report["records"])!=11:
        raise ValueError("Unexpected editorial delta record count")
    structural=analyze(candidate)
    if structural["entry_count"]!=9380 or structural["duplicate_xml_ids"]:
        raise ValueError("Article or ID violation")
    if structural["profile_rule_findings"]:
        raise ValueError("Candidate fails the actual strict project profile")
    if structural["link_classes"].get("active_original_isbe_target",0):
        raise ValueError("Unresolved active source navigation")
    if structural["unique_xml_ids"]!=185657:
        raise ValueError("Original stable ID coverage differs")
    manifest=json.loads(Path(original_manifest).read_text(encoding="utf-8"))
    manifest["expected_candidate_sha256"]=report["candidate_sha256"]
    manifest["review_preview_only"]=True
    fidelity={
        "candidate_sha256":report["candidate_sha256"],
        "article_parity":"PASS",
        "serialized_profile_check":"PASS",
        "review_preview_only":True,
        "unaltered_articles_verified":9369,
        "declared_editorial_candidates":11,
        "full_corpus_ids_preserved":185657,
        "historical_print_witness_review":"NOT_VERIFIED",
        "publication":"PROHIBITED",
    }
    for output,data in [(manifest_out,manifest),(report_out,fidelity)]:
        out=Path(output)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--change-report",type=Path,required=True)
    p.add_argument("--original-manifest",type=Path,required=True)
    p.add_argument("--manifest-out",type=Path,required=True)
    p.add_argument("--report-out",type=Path,required=True)
    a=p.parse_args()
    prepare(a.source,a.candidate,a.change_report,a.original_manifest,
            a.manifest_out,a.report_out)
    print("Full source-parity and strict structural profile verified for noncanonical preview")

if __name__=="__main__":
    main()
