#!/usr/bin/env python3
"""Apply reviewed 1915 print corrections to a SEPARATE editorial TEI.

Never mutate the canonical source or the 31-entry reviewed baseline.
All changes are exact, source-locked, reversible and witness-bound.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from audit_tei_structure import analyze

TEI="{http://www.tei-c.org/ns/1.0}"
XMLID="{http://www.w3.org/XML/1998/namespace}id"
SOURCE_SHA="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
ROOT=Path(__file__).resolve().parents[1]
ET.register_namespace("","http://www.tei-c.org/ns/1.0")

def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()

def sha_file(path):
    return sha_bytes(Path(path).read_bytes())

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def articles_by_key(root):
    if root.tag!=TEI+"TEI":
        raise ValueError("Expected TEI document")
    body=root.find(f"./{TEI}text/{TEI}body")
    if body is None:
        raise ValueError("Missing TEI body")
    rows={}
    for article in body:
        key=article.get("n")
        if not key or not article.get(XMLID) or key in rows:
            raise ValueError("Missing or duplicated source article")
        rows[key]=article
    return rows

def apply_operations(root, decisions):
    """Pure in-memory patch with verified old reading, source reference and target."""
    articles=articles_by_key(root)
    changed=set()
    ledger=[]
    for row in decisions:
        if row.get("operation")!="replace_article_ref" or row.get("approved_for_separate_editorial_tei") is not True:
            raise ValueError("Unreviewed or unsupported editorial delta")
        key=row["source_key"]
        if key in changed or key not in articles:
            raise ValueError("Repeated or missing affected article")
        before_key=row["original_target_key"]
        after_key=row["printed_target_key"]
        if before_key not in articles or after_key not in articles or before_key==after_key:
            raise ValueError("Missing or identical old/new link target")
        article=articles[key]
        matches=[n for n in article.iter()
                 if n.tag==TEI+"p" and n.get(XMLID)==row["source_unit_xml_id"]]
        if len(matches)!=1:
            raise ValueError("Original paragraph identity mismatch")
        paragraph=matches[0]
        refs=[n for n in paragraph.iter() if n.tag==TEI+"ref"
              and n.get("n")=="ISBE:"+before_key
              and n.get("target")=="#"+articles[before_key].get(XMLID)
              and n.text==row["original_visible"]]
        if len(refs)!=1:
            raise ValueError("Original linked reading or target mismatch")
        ref=refs[0]
        if len(ref) or not ref.get(XMLID):
            raise ValueError("Unexpected complex or unidentified ref")
        original_unit="".join(paragraph.itertext())
        old_xml=ET.tostring(article,encoding="utf-8")
        old_ref_xml=ET.tostring(ref,encoding="utf-8")
        old_target=ref.get("target")
        # Keep ref/@n as the original CrossWire target for provenance. The
        # active ref/@target and visible text follow independently verified print.
        ref.text=row["printed_visible"]
        ref.set("target","#"+articles[after_key].get(XMLID))
        if ET.tostring(article,encoding="utf-8")==old_xml:
            raise ValueError("Editorial change had no effect")
        ledger.append({
            "article_key":key,"article_xml_id":article.get(XMLID),
            "source_paragraph_xml_id":paragraph.get(XMLID),
            "ref_xml_id":ref.get(XMLID),
            "original_visible":row["original_visible"],
            "revised_visible":row["printed_visible"],
            "original_source_ref_n":ref.get("n"),
            "original_active_target":old_target,
            "revised_active_target":ref.get("target"),
            "original_ref_xml_sha256":sha_bytes(old_ref_xml),
            "original_unit_text_sha256":sha_bytes(original_unit.encode("utf-8")),
            "revised_unit_text_sha256":sha_bytes("".join(paragraph.itertext()).encode("utf-8")),
            "rationale":row["rationale"],
        })
        changed.add(key)
    return changed,ledger

def validate_decisions(spec, evidence):
    if spec.get("schema_version")!=1 or spec.get("canonical_source_sha256")!=SOURCE_SHA:
        raise ValueError("Wrong editorial delta source or schema")
    if spec.get("publication_permitted") is not False or spec.get("independent_human_peer_review") is not False:
        raise ValueError("Editorial text correction is not release/human approval")
    if not spec.get("decisions") or len(spec["decisions"])!=len({d["source_key"] for d in spec["decisions"]}):
        raise ValueError("Missing or duplicated approval")
    for delta in spec["decisions"]:
        rows=[r for r in evidence["cases"] if r["source_key"]==delta["source_key"]
              and r["source_text_exact"]==delta["original_visible"]
              and r["printed_text_reading"]==delta["printed_visible"]
              and r.get("source_unit_xml_id")==delta["source_unit_xml_id"]]
        if len(rows)!=1:
            raise ValueError("Approved correction not bound to print/source contrast")
        e=rows[0]
        if (e.get("review_status")!="primary_print_folio_visually_checked_ai_assisted_not_full_article"
                or e["original_pdf_sha256"]!="f1232371fec1df1382692b2f1be8993fb1d594eda46170aaccd6337ce98a29f5"
                or not e.get("rendered_jpeg_sha256")
                or e.get("approved") is not False):
            raise ValueError("Unverified 1915 original printed-page evidence")
    return len(spec["decisions"])

def apply_files(source,baseline,baseline_report,ledger_path,output,report,baseline_manifest,derived_manifest,fidelity):
    for p in (source,baseline,baseline_report,ledger_path,baseline_manifest):
        if not Path(p).is_file():
            raise ValueError("Required source or approved baseline missing")
    if sha_file(source)!=SOURCE_SHA:
        raise ValueError("Canonical CrossWire witness drift")
    status=read(baseline_report)
    baseline_hash=sha_file(baseline)
    if status.get("canonical_source_sha256")!=SOURCE_SHA or status.get("provisional_candidate_sha256")!=baseline_hash:
        raise ValueError("Second-pass 31-entry baseline identity mismatch")
    if (status.get("original_entries")!=9380 or status.get("proposed_redirects")!=11
            or status.get("proposed_historical_text_entries")!=20
            or status.get("publication_permitted") is not False):
        raise ValueError("Baseline is not the approved separate 31-entry witness")
    spec=read(ledger_path)
    evidence=read(ROOT/spec["source_evidence_ledger"])
    if evidence.get("canonical_sha256")!=SOURCE_SHA:
        raise ValueError("Historical witness ledger source drift")
    validate_decisions(spec,evidence)
    root=ET.parse(baseline).getroot()
    articles=articles_by_key(root)
    if len(articles)!=9380:
        raise ValueError("Unexpected 1915 editorial baseline population")
    before={k:ET.tostring(v,encoding="utf-8") for k,v in articles.items()}
    ids_before=[n.get(XMLID) for a in articles.values() for n in a.iter() if n.get(XMLID)]
    changed,deltas=apply_operations(root,spec["decisions"])
    if changed & set(status["affected_keys"]):
        raise ValueError("Print delta conflicts with original 31 reviewed recoveries")
    if any(ET.tostring(a,encoding="utf-8")!=before[k] for k,a in articles.items() if k not in changed):
        raise ValueError("Unreviewed in-memory structural change")
    out=Path(output)
    out.parent.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(root).write(out,encoding="utf-8",xml_declaration=True)
    reloaded=articles_by_key(ET.parse(out).getroot())
    if len(reloaded)!=len(articles):
        raise ValueError("Article coverage changed")
    if any(ET.tostring(reloaded[k],encoding="utf-8")!=before[k] for k in articles if k not in changed):
        raise ValueError("Unreviewed serialized content/structure drift")
    ids_after=[n.get(XMLID) for a in reloaded.values() for n in a.iter() if n.get(XMLID)]
    if ids_after!=ids_before or len(set(ids_after))!=len(ids_after):
        raise ValueError("XML identifiers changed or duplicated")
    id_set=set(ids_after)
    if any(ref.get("target")[1:] not in id_set for a in reloaded.values()
           for ref in a.iter(TEI+"ref") if (ref.get("target") or "").startswith("#")):
        raise ValueError("Broken internal reference after editorial revision")
    structures=analyze(out)
    if structures["profile_rule_findings"] or structures["duplicate_xml_ids"]:
        raise ValueError("TEI project structural profile violated")
    candidate_hash=sha_file(out)
    record={
        "canonical_source_sha256":SOURCE_SHA,
        "baseline_31_entry_candidate_sha256":baseline_hash,
        "edited_candidate_sha256":candidate_hash,
        "original_entries":len(articles),
        "unchanged_articles_verified":len(articles)-len(changed),
        "changed_articles":len(changed),
        "original_xml_ids_preserved":len(ids_after),
        "source_zip_imp_and_canonical_unchanged":True,
        "noncanonical":True,"publication_permitted":False,
        "independent_human_peer_review":False,
        "deltas":deltas,
    }
    for path,data in [(report,record),
                      (derived_manifest,{**read(baseline_manifest),"expected_candidate_sha256":candidate_hash,
                       "noncanonical_review_only":True,"review_delta_ledger":str(ledger_path)}),
                      (fidelity,{"candidate_sha256":candidate_hash,"article_parity":"PASS",
                       "serialized_profile_check":"PASS","unchanged_articles_verified":len(articles)-len(changed),
                       "approved_text_modifications":len(changed),"publication_permitted":False,
                       "noncanonical":True,"independent_human_peer_review":False})]:
        dst=Path(path)
        dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return record

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",default="cleaned/en/ISBE.xml")
    for field in ("baseline","baseline-report","ledger","output","report",
                  "baseline-manifest","derived-manifest","fidelity"):
        p.add_argument("--"+field,required=True)
    a=vars(p.parse_args())
    out=apply_files(a["source"],a["baseline"],a["baseline_report"],
                    a["ledger"],a["output"],a["report"],a["baseline_manifest"],
                    a["derived_manifest"],a["fidelity"])
    print(json.dumps({k:v for k,v in out.items() if k!="deltas"},indent=2))
    for d in out["deltas"]:
        print("APPROVED_PRINT_DELTA",d["article_key"],d["ref_xml_id"],
              repr(d["original_visible"]), "->",repr(d["revised_visible"]))

if __name__=="__main__":
    main()
