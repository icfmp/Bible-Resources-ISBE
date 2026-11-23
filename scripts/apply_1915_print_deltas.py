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
    """Apply exact, independently reviewed text or reference deltas in memory.

    Generic operations never infer their scope from a global replacement rule.
    The old text, destination, unit ID and/or old canonical scripture target are
    explicit preconditions for each operation. Existing IDs are never renamed.
    """
    articles=articles_by_key(root)
    original_ids={n.get(XMLID) for a in articles.values() for n in a.iter() if n.get(XMLID)}
    changed=set()
    recorded=[]
    new_ids=set()
    seen=set()
    for row in decisions:
        kind=row.get("operation")
        if kind not in {"replace_article_ref","replace_text_span","replace_scripture_ref_series"}:
            raise ValueError("Unsupported editorial operation")
        if row.get("approved_for_separate_editorial_tei") is not True:
            raise ValueError("Unreviewed editorial delta")
        key=row.get("source_key")
        if key not in articles:
            raise ValueError("Missing source article")
        old=row.get("original_visible")
        revised=row.get("printed_visible")
        if not old or not revised or old==revised:
            raise ValueError("Editorial operation must state distinct exact readings")
        identity=(key,row.get("source_unit_xml_id"),kind,old)
        if identity in seen:
            raise ValueError("Repeated editorial operation")
        seen.add(identity)
        article=articles[key]
        paragraphs=[n for n in article.iter()
                    if n.tag==TEI+"p" and n.get(XMLID)==row.get("source_unit_xml_id")]
        if len(paragraphs)!=1:
            raise ValueError("Original paragraph identity mismatch")
        paragraph=paragraphs[0]
        old_text="".join(paragraph.itertext())
        if old_text.count(old)!=1:
            raise ValueError("Source text is missing or ambiguous")
        info={"operation":kind,"article_key":key,
              "article_xml_id":article.get(XMLID),
              "source_paragraph_xml_id":paragraph.get(XMLID),
              "original_visible":old,"revised_visible":revised,
              "rationale":row.get("rationale"),
              "original_unit_text_sha256":sha_bytes(old_text.encode("utf-8"))}
        if kind=="replace_article_ref":
            before_key=row["original_target_key"]
            after_key=row["printed_target_key"]
            if (before_key not in articles or after_key not in articles
                    or before_key==after_key):
                raise ValueError("Missing or identical old/new link target")
            refs=[n for n in paragraph.iter() if n.tag==TEI+"ref"
                  and n.get("n")=="ISBE:"+before_key
                  and n.get("target")=="#"+articles[before_key].get(XMLID)
                  and n.text==old]
            if len(refs)!=1 or len(refs[0]) or not refs[0].get(XMLID):
                raise ValueError("Original linked reading or target mismatch")
            ref=refs[0]
            info.update({"ref_xml_id":ref.get(XMLID),
                         "original_source_ref_n":ref.get("n"),
                         "original_active_target":ref.get("target"),
                         "original_ref_xml_sha256":sha_bytes(ET.tostring(ref,encoding="utf-8"))})
            # Attribute n remains the *original* CrossWire digital target.
            ref.text=revised
            ref.set("target","#"+articles[after_key].get(XMLID))
            info["revised_active_target"]=ref.get("target")

        elif kind=="replace_text_span":
            slots=[]
            for node in paragraph.iter():
                if node.text and old in node.text:
                    slots.append((node,"text"))
                # The paragraph's own tail is outside the reviewed unit.
                if node is not paragraph and node.tail and old in node.tail:
                    slots.append((node,"tail"))
            if len(slots)!=1:
                raise ValueError("Historical phrase spans multiple markup boundaries")
            node,attribute=slots[0]
            value=getattr(node,attribute)
            if value.count(old)!=1:
                raise ValueError("Historical source reading is not unique in its text slot")
            setattr(node,attribute,value.replace(old,revised,1))
            info["edited_slot"]=attribute
            info["slot_element_xml_id"]=node.get(XMLID)

        else:  # replace_scripture_ref_series
            refid=row.get("source_ref_xml_id")
            refs=[n for n in paragraph if n.tag==TEI+"ref" and n.get(XMLID)==refid]
            if len(refs)!=1:
                raise ValueError("Original scripture reference element is absent")
            ref=refs[0]
            if (len(ref) or ref.text!=old
                    or ref.get("type")!="scripture"
                    or ref.get("cRef")!=row.get("original_c_ref")
                    or ref.get("target") is not None):
                raise ValueError("Original scripture reference or target mismatch")
            replacements=row.get("replacements")
            if (not isinstance(replacements,list) or not 2<=len(replacements)<=10
                    or any(not isinstance(item,dict) or not item.get("visible")
                           or not item.get("cRef","").startswith("Bible:")
                           for item in replacements)):
                raise ValueError("Invalid historical scripture reference sequence")
            if "; ".join(item["visible"] for item in replacements)!=revised:
                raise ValueError("Printed scripture sequence differs from reviewed reading")
            info.update({"ref_xml_id":ref.get(XMLID),
                         "original_scripture_cRef":ref.get("cRef"),
                         "original_ref_xml_sha256":sha_bytes(ET.tostring(ref,encoding="utf-8"))})
            tail=ref.tail
            index=list(paragraph).index(ref)
            ref.text=replacements[0]["visible"]
            ref.set("cRef",replacements[0]["cRef"])
            ref.tail="; "
            added=[]
            for position,item in enumerate(replacements[1:],start=1):
                next_id=refid+f"-print-{position:03d}"
                if next_id in original_ids or next_id in new_ids:
                    raise ValueError("New historical reference XML ID collides")
                node=ET.Element(TEI+"ref",{XMLID:next_id,"type":"scripture","cRef":item["cRef"]})
                node.text=item["visible"]
                node.tail="; " if position<len(replacements)-1 else tail
                paragraph.insert(index+position,node)
                new_ids.add(next_id)
                added.append(next_id)
            info["revised_scripture_cRefs"]=[item["cRef"] for item in replacements]
            info["added_xml_ids"]=added

        final_text="".join(paragraph.itertext())
        if final_text==old_text or final_text.count(revised)!=1:
            raise ValueError("Reviewed operation did not produce the expected visible text")
        info["revised_unit_text_sha256"]=sha_bytes(final_text.encode("utf-8"))
        recorded.append(info)
        changed.add(key)
    return changed,recorded,new_ids

def validate_decisions(spec, evidence):
    if spec.get("schema_version")!=1 or spec.get("canonical_source_sha256")!=SOURCE_SHA:
        raise ValueError("Wrong editorial delta source or schema")
    if spec.get("publication_permitted") is not False or spec.get("independent_human_peer_review") is not False:
        raise ValueError("Editorial text correction is not release/human approval")
    keys=[(d.get("source_key"),d.get("source_unit_xml_id"),d.get("operation"),d.get("original_visible"))
          for d in spec.get("decisions",[])]
    if not keys or len(keys)!=len(set(keys)):
        raise ValueError("Missing or duplicated approval")
    manifest=read(ROOT/"sources/print/1915-volume-witnesses.json")
    volumes={v["volume"]:v for v in manifest["volumes"]}
    for delta in spec["decisions"]:
        rows=[r for r in evidence["cases"] if r["source_key"]==delta["source_key"]
              and r["source_text_exact"]==delta["original_visible"]
              and r["printed_text_reading"]==delta["printed_visible"]
              and r.get("source_unit_xml_id")==delta["source_unit_xml_id"]]
        if len(rows)!=1:
            raise ValueError("Approved correction not bound to print/source contrast")
        e=rows[0]
        original=volumes.get(e.get("print_volume"))
        image=e.get("rendered_jpeg_sha256")
        if (e.get("review_status")!="primary_print_folio_visually_checked_ai_assisted_not_full_article"
                or original is None or e["original_pdf_sha256"]!=original["pdf_sha256"]
                or delta.get("evidence_pdf_sha256")!=e.get("original_pdf_sha256")
                or delta.get("evidence_rendered_jpeg_sha256")!=image
                or delta.get("evidence_workflow_run")!=e.get("primary_evidence_workflow")
                or not isinstance(image,str) or len(image)!=64
                or any(c not in "0123456789abcdef" for c in image)
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
    changed,deltas,new_ids=apply_operations(root,spec["decisions"])
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
    before_ids=set(ids_before)
    after_ids=set(ids_after)
    if (len(ids_after)!=len(after_ids) or not before_ids.issubset(after_ids)
            or after_ids-before_ids!=new_ids
            or [x for x in ids_after if x in before_ids]!=ids_before):
        raise ValueError("Original XML identifiers changed or new IDs are unapproved")
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
        "original_xml_ids_preserved":len(ids_before),
        "new_xml_ids":len(new_ids),
        "total_xml_ids":len(ids_after),
        "applied_operations":len(deltas),
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
                       "approved_text_modifications":len(deltas),"publication_permitted":False,
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
        print("APPROVED_PRINT_DELTA",d["article_key"],d["operation"],d["source_paragraph_xml_id"],
              repr(d["original_visible"]), "->",repr(d["revised_visible"]))

if __name__=="__main__":
    main()
