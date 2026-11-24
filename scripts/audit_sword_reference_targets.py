#!/usr/bin/env python3
"""Source-preserving census of dictionary cross-reference navigation limits.

This independent audit compares original TEI <ref> attributes with the
adapter's <ref> attributes. It documents every section target that native
SWORD can address only at article-key granularity. Nothing is rewritten.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

N="{http://www.tei-c.org/ns/1.0}"
XML="{http://www.w3.org/XML/1998/namespace}"

def digest(path):
    h=sha256()
    with Path(path).open("rb") as inp:
        for chunk in iter(lambda:inp.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def read_entries(path,tag):
    root=ET.parse(path).getroot()
    body=root.find("./"+N+"text/"+N+"body")
    if body is None:
        raise ValueError("Missing dictionary body")
    found={}
    for entry in body:
        key=entry.get("n")
        if entry.tag!=N+tag or not key or key in found:
            raise ValueError("Unexpected wrapper, duplicate key, or empty dictionary key")
        found[key]=entry
    return found

def analyze(source_path,import_path,report_path,module_id):
    if not module_id or ":" in module_id or "/" in module_id:
        raise ValueError("Invalid explicit module ID")
    original=read_entries(source_path,"div")
    adapted=read_entries(import_path,"entryFree")
    if original.keys()!=adapted.keys():
        raise ValueError("Article inventory changed in SWORD adapter")
    by_id={}
    for key,article in original.items():
        if article.get("type")!="entry":
            raise ValueError("Non-entry original article")
        for node in article.iter():
            ident=node.get(XML+"id")
            if ident:
                if ident in by_id:
                    raise ValueError("Duplicate original xml:id")
                by_id[ident]=(key,node,node is article)
    summary={
        "schema_version":1,
        "source_tei_sha256":digest(source_path),
        "explicit_sword_work_id":module_id,
        "sword_import_tei_sha256":digest(import_path),
        "source_article_count":len(original),
        "source_xml_id_count":len(by_id),
        "total_ref_nodes":0,
        "internal_dictionary_refs":0,
        "article_target_refs":0,
        "nested_target_refs":0,
        "section_typed_refs":0,
        "bible_osis_references":0,
        "other_refs":0,
        "source_and_adapter_ref_text_unchanged":True,
        "source_and_adapter_attributes_verified":True,
        "section_target_navigation_exact":False,
        "source_modified":False,
        "rights_cleared":False,
        "published":False,
        "section_ref_register":[]
    }
    destination_types=Counter()
    for source_key,entry in original.items():
        old=list(entry.iter(N+"ref"))
        new=list(adapted[source_key].iter(N+"ref"))
        if len(old)!=len(new):
            raise ValueError("Reference count changed for "+source_key)
        for index,(prev,nxt) in enumerate(zip(old,new)):
            summary["total_ref_nodes"]+=1
            if "".join(prev.itertext())!="".join(nxt.itertext()):
                raise ValueError("Visible reference text changed in "+source_key)
            expected=dict(prev.attrib)
            target=prev.get("target")
            cref=prev.get("cRef")
            section=prev.get("type")=="section"
            if section:
                summary["section_typed_refs"]+=1
            if target and target.startswith("#"):
                ident=target[1:]
                if ident not in by_id:
                    raise ValueError(f"Unresolved original target {ident} in {source_key}")
                dest_key,dest_node,is_article=by_id[ident]
                if "corresp" in expected:
                    raise ValueError("Existing original corresp would be overwritten")
                expected["target"]=module_id+":"+dest_key
                expected["corresp"]=target
                summary["internal_dictionary_refs"]+=1
                destination_types[dest_node.tag.partition("}")[2]]+=1
                if is_article:
                    summary["article_target_refs"]+=1
                else:
                    summary["nested_target_refs"]+=1
                if section or not is_article:
                    head=next((child for child in dest_node
                               if child.tag==N+"head"),None)
                    summary["section_ref_register"].append({
                        "source_article":source_key,
                        "source_ref_index":index,
                        "link_text":"".join(prev.itertext()),
                        "original_target":target,
                        "sword_article_target":module_id+":"+dest_key,
                        "destination_article":dest_key,
                        "destination_node_tag":dest_node.tag.partition("}")[2],
                        "destination_is_article":is_article,
                        "source_ref_type":prev.get("type"),
                        "destination_heading":"".join(head.itertext()) if head is not None else None,
                        "intra_article_scroll_position_preserved":is_article
                    })
            elif not cref:
                summary["other_refs"]+=1
            if cref:
                if "osisRef" in expected:
                    raise ValueError("Original osisRef would be overwritten")
                expected["osisRef"]=cref
                summary["bible_osis_references"]+=1
            if nxt.attrib!=expected:
                raise ValueError(f"Adapter reference attributes changed unexpectedly: {source_key} #{index}")
    summary["target_node_types"]=dict(sorted(destination_types.items()))
    summary["section_ref_register_count"]=len(summary["section_ref_register"])
    summary["section_scroll_precision_limited_count"]=sum(
        not x["destination_is_article"] for x in summary["section_ref_register"])
    report=Path(report_path)
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True)
    p.add_argument("--adapted",required=True)
    p.add_argument("--report",required=True)
    p.add_argument("--module-id",required=True)
    a=p.parse_args()
    result=analyze(a.source,a.adapted,a.report,a.module_id)
    print(json.dumps({k:v for k,v in result.items() if k!="section_ref_register"},
                     indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
