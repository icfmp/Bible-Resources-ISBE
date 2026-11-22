#!/usr/bin/env python3
"""Official P5 input lock for unapproved source-locked ISBE historical text specimen."""
import argparse
import hashlib
import json
from pathlib import Path
from audit_tei_structure import analyze

SOURCE_HASH="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate(source,candidate,report_path,manifest_path,out_manifest,out_fidelity):
    report=json.loads(Path(report_path).read_text())
    if sha(source)!=SOURCE_HASH or report["canonical_source_sha256"]!=SOURCE_HASH:
        raise ValueError("Canonical source digest mismatch")
    if sha(candidate)!=report["provisional_candidate_sha256"]:
        raise ValueError("Specimen digest mismatch")
    if not report["noncanonical"] or report["publication_permitted"]:
        raise ValueError("Unapproved edition must not be marked releasable")
    for key,expected in [
        ("original_entries",9380),("proposed_redirects",11),
        ("proposed_historical_text_entries",20),
        ("unchanged_articles_verified",9349),
        ("original_ids_preserved",185657),("new_xml_ids",2)
    ]:
        if report[key]!=expected:
            raise ValueError(f"Incorrect parity result for {key}: {report[key]}")
    stat=analyze(candidate)
    if stat["entry_count"]!=9380 or stat["unique_xml_ids"]!=185659:
        raise ValueError("Unexpected TEI article/ID count")
    if stat["duplicate_xml_ids"] or stat["profile_rule_findings"]:
        raise ValueError("TEI profile violations")
    if stat["link_classes"].get("active_original_isbe_target",0):
        raise ValueError("Active invalid CrossWire targets")
    original=json.loads(Path(manifest_path).read_text())
    original["expected_candidate_sha256"]=sha(candidate)
    original["noncanonical_review_only"]=True
    fidelity={
        "candidate_sha256":sha(candidate),
        "article_parity":"PASS",
        "serialized_profile_check":"PASS",
        "noncanonical":True,
        "publication_permitted":False,
        "historical_print_page_images":"NOT_REVIEWED",
        "unchanged_articles_verified":9349,
        "approved_text_modifications":0,
    }
    for path,data in [(out_manifest,original),(out_fidelity,fidelity)]:
        path=Path(path)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    return fidelity

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for field in ("source","candidate","report","manifest","out-manifest","out-fidelity"):
        p.add_argument("--"+field,required=True)
    a=vars(p.parse_args())
    print(json.dumps(validate(a["source"],a["candidate"],a["report"],a["manifest"],a["out_manifest"],a["out_fidelity"]),indent=2))
