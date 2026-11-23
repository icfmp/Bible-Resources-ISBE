#!/usr/bin/env python3
"""Apply source-image-reviewed Scripture TARGET corrections only to separate TEI.

The source-faithful CrossWire TEI, original SWORD files, and preceding
31-entry / six-print-delta editorial witness remain immutable. Each candidate
has an exact article, source paragraph, ref ID, old visible label and cRef.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from scripts.audit_tei_structure import analyze
import re
import xml.etree.ElementTree as ET

T="{http://www.tei-c.org/ns/1.0}"
ID="{http://www.w3.org/XML/1998/namespace}id"
LOCK="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
ET.register_namespace("","http://www.tei-c.org/ns/1.0")

def sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def article_map(root):
    body=root.find(f"./{T}text/{T}body")
    if root.tag!=T+"TEI" or body is None:
        raise ValueError("Not a TEI document")
    articles={a.get("n"):a for a in body}
    if len(articles)!=len(body) or any(not a.get("n") or not a.get(ID) for a in body):
        raise ValueError("Invalid article identities")
    return articles

def validate_ledger(ledger,manifest):
    if ledger.get("canonical_sha256")!=LOCK or ledger.get("publication_permitted") is not False or ledger.get("canonical_modified") is not False:
        raise ValueError("Unapproved historical evidence ledger")
    rows=ledger["cases"]
    if len(rows)!=13 or len({r["ref_xml_id"] for r in rows})!=13:
        raise ValueError("Expected 13 distinct source navigation candidates")
    volumes={v["volume"]:v for v in manifest["volumes"]}
    approved=[]
    for row in rows:
        if row["source_pdf_sha256"]!=volumes[row["print_volume"]]["pdf_sha256"]:
            raise ValueError("Historical source PDF digest differs")
        if row["approval"]!="research_only_no_edit":
            raise ValueError("Unexpected editorial approval in evidence ledger")
        if row["disposition"]=="unresolved_no_adequate_print_page":
            if row["proposed_cRef"] is not None:
                raise ValueError("Unresolved printed passage must not be edited")
            continue
        if (row["disposition"]!="visually_attested_candidate"
                or not isinstance(row["pdf_page_1_based"],int)
                or not 1<=row["pdf_page_1_based"]<=volumes[row["print_volume"]]["pages"]
                or not re.fullmatch("[a-f0-9]{64}",row.get("source_image_jpeg_sha256") or "")
                or not row.get("source_image_workflow_run")
                or row["original_cRef"]==row["proposed_cRef"]
                or not re.fullmatch(r"Bible:[A-Za-z0-9]+\.\d+\.\d+",row["proposed_cRef"])):
            raise ValueError("Missing individual original printed-page evidence")
        approved.append(row)
    if len(approved)!=12:
        raise ValueError("Expected exactly 12 source-image-attested metadata changes")
    return approved

def apply_target_changes(root,rows):
    articles=article_map(root)
    changed=set()
    records=[]
    all_ids={n.get(ID) for a in articles.values() for n in a.iter() if n.get(ID)}
    for row in rows:
        key=row["source_key"]
        if key not in articles:
            raise ValueError("Missing original article")
        article=articles[key]
        matches=[r for r in article.iter(T+"ref") if r.get(ID)==row["ref_xml_id"]]
        parents=[p for p in article.iter(T+"p") if p.get(ID)==row["unit_xml_id"]]
        if len(matches)!=1 or len(parents)!=1 or matches[0] not in list(parents[0].iter()):
            raise ValueError("Reference and original parent paragraph identity mismatch")
        ref=matches[0]
        before=ref.get("cRef")
        label="".join(ref.itertext())
        if (ref.get("type")!="scripture" or before!=row["original_cRef"]
                or label!=row["visible"] or ref.get("target") is not None):
            raise ValueError("Source reference visible/cRef/markup drift")
        # The original printed spelling and segmentation must remain unchanged:
        # this layer corrects only the validated target, never displayed prose.
        ref.set("cRef",row["proposed_cRef"])
        records.append({"article_key":key,"article_xml_id":article.get(ID),
                        "source_unit_xml_id":parents[0].get(ID),
                        "ref_xml_id":ref.get(ID),"visible_text_preserved":label,
                        "old_cRef":before,"corrected_cRef":ref.get("cRef"),
                        "print_volume":row["print_volume"],"pdf_page_1_based":row["pdf_page_1_based"],
                        "pdf_sha256":row["source_pdf_sha256"],"image_sha256":row["source_image_jpeg_sha256"]})
        changed.add(key)
    if len(records)!=12 or len(all_ids)!=(sum(1 for a in articles.values() for n in a.iter() if n.get(ID))):
        raise ValueError("Count or identifier inconsistency")
    return changed,records

def run(source,baseline,previous_report,ledger_path,manifest_path,output,report,previous_validator,derived_validator,derived_fidelity):
    if sha(source)!=LOCK:
        raise ValueError("Immutable canonical CrossWire source drift")
    preceding=read(previous_report)
    if (preceding.get("edited_candidate_sha256")!=sha(baseline)
            or preceding.get("original_entries")!=9380
            or preceding.get("applied_operations")!=6
            or preceding.get("publication_permitted") is not False):
        raise ValueError("The earlier 31+6 editorial witness is not the approved baseline")
    ledger=read(ledger_path)
    rows=validate_ledger(ledger,read(manifest_path))
    root=ET.parse(baseline).getroot()
    articles=article_map(root)
    if len(articles)!=9380:
        raise ValueError("Missing historical encyclopedia entries")
    before={key:ET.tostring(a,encoding="utf-8") for key,a in articles.items()}
    texts={key:"".join(a.itertext()) for key,a in articles.items()}
    before_ids=[n.get(ID) for a in articles.values() for n in a.iter() if n.get(ID)]
    changed,records=apply_target_changes(root,rows)
    if any(ET.tostring(a,encoding="utf-8")!=before[key] for key,a in articles.items() if key not in changed):
        raise ValueError("Unrelated article was changed")
    if any("".join(a.itertext())!=texts[key] for key,a in articles.items()):
        raise ValueError("The original visible article text changed")
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(root).write(output,encoding="utf-8",xml_declaration=True)
    reloaded=article_map(ET.parse(output).getroot())
    after_ids=[n.get(ID) for a in reloaded.values() for n in a.iter() if n.get(ID)]
    if list(reloaded)!=list(articles) or after_ids!=before_ids:
        raise ValueError("Historical article order or original IDs changed")
    for key,a in reloaded.items():
        if "".join(a.itertext())!=texts[key] or (key not in changed and ET.tostring(a,encoding="utf-8")!=before[key]):
            raise ValueError("Unexpected serialized historical content changes")
    structure=analyze(output)
    if structure["profile_rule_findings"] or structure["duplicate_xml_ids"]:
        raise ValueError("Source-derived TEI project profile failed")
    result={"canonical_sha256":LOCK,"previous_editorial_sha256":sha(baseline),
            "revised_sha256":sha(output),"article_count":len(articles),
            "changed_articles":len(changed),"unchanged_articles":len(articles)-len(changed),
            "scripture_targets_corrected":len(records),"original_xml_ids_preserved":len(before_ids),
            "visible_text_byte_equivalent":True,"source_zip_imp_and_canonical_unchanged":True,
            "noncanonical":True,"publication_permitted":False,
            "independent_human_peer_review":False,"changes":records}
    validator={**read(previous_validator),"expected_candidate_sha256":result["revised_sha256"],
               "noncanonical_review_only":True,
               "review_delta_ledger":str(ledger_path)}
    fidelity={"candidate_sha256":result["revised_sha256"],
              "article_parity":"PASS","serialized_profile_check":"PASS",
              "publication_permitted":False,
              "noncanonical":True,"independent_human_peer_review":False,
              "changed_reference_metadata_only":len(records)}
    for dst,data in [(report,result),(derived_validator,validator),(derived_fidelity,fidelity)]:
        dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",default="workspace/witnesses/crosswire-2.2/ISBE.xml")
    p.add_argument("--baseline",required=True)
    p.add_argument("--previous-report",required=True)
    p.add_argument("--previous-validator",required=True)
    p.add_argument("--ledger",default="workspace/reviews/1915-scripture-reference-image-triage-v1.json")
    p.add_argument("--manifest",default="workspace/witnesses/print/1915-volume-witnesses.json")
    for k in ("output","report","derived-validator","derived-fidelity"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    result=run(a.source,a.baseline,a.previous_report,a.ledger,a.manifest,
               a.output,a.report,a.previous_validator,a.derived_validator,a.derived_fidelity)
    print(json.dumps({k:v for k,v in result.items() if k!="changes"},indent=2))
    for row in result["changes"]:
        print("SOURCE_BACKED_TARGET",row["article_key"],row["ref_xml_id"],
              row["old_cRef"],"->",row["corrected_cRef"])

if __name__=="__main__":
    main()
