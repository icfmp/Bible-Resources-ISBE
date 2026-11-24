#!/usr/bin/env python3
"""Adapt source-locked TEI P5 entries and references to SWORD dictionaries.

The source master stays unchanged. Entry wrapper div elements are converted to
entryFree; article and section links gain explicit SWORD module:key targets,
while the exact source target remains in corresp. Bible cRef is retained and
exposed via native osisRef. All these adapter-only changes are reported;
nested sections are retained for independent reader compatibility review.
"""
import argparse
import copy
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

TEI="http://www.tei-c.org/ns/1.0"
XML="http://www.w3.org/XML/1998/namespace"
NS=f"{{{TEI}}}"
ET.register_namespace("",TEI)

def digest(path):
    out=sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            out.update(chunk)
    return out.hexdigest()

def read_entries(source,expected_sha,expected_count):
    source=Path(source)
    if expected_sha and digest(source)!=expected_sha:
        raise ValueError("Source TEI SHA-256 is not the locked historical master")
    root=ET.parse(source).getroot()
    if root.tag!=NS+"TEI":
        raise ValueError("Not a TEI P5 document")
    header=root.find(NS+"teiHeader")
    body=root.find("./"+NS+"text/"+NS+"body")
    if header is None or body is None:
        raise ValueError("Missing TEI header or body")
    entries=list(body)
    if expected_count and len(entries)!=expected_count:
        raise ValueError(f"Expected {expected_count} source entries; got {len(entries)}")
    ids=set()
    keys=set()
    nested=0
    details=[]
    for i,entry in enumerate(entries):
        key=entry.get("n")
        identifier=entry.get(f"{{{XML}}}id")
        if entry.tag!=NS+"div" or entry.get("type")!="entry":
            raise ValueError(f"Unexpected article element at {i}")
        if not key or not identifier or "|" in key or "\n" in key:
            raise ValueError(f"Missing/unsupported SWORD dictionary key: {key!r}")
        if key in keys or identifier in ids:
            raise ValueError(f"Duplicate article key or identifier: {key!r}")
        keys.add(key)
        ids.add(identifier)
        count=sum(1 for x in entry.iter() if x is not entry and x.tag==NS+"div")
        nested+=count
        details.append({
           "key":key,"xml_id":identifier,"nested_divisions":count,
           "source_text_sha256":sha256("".join(entry.itertext()).encode("utf-8")).hexdigest()
        })
    return header,entries,nested,details

def convert(source,outpath,reportpath,expected_sha,expected_count,module_id):
    # SWORD TEIHTMLHREF splits the target at its first ':' and interprets
    # the left part as the *actual module ID*, not a magic 'self' alias.
    # Explicit module naming works even if a dictionary key contains ':'.
    if not module_id or any(c in module_id for c in (":","/","\\","\n"," ")):
        raise ValueError("SWORD module ID must be a valid, nonempty link work name")
    source=Path(source);outpath=Path(outpath);reportpath=Path(reportpath)
    header,entries,nested,details=read_entries(source,expected_sha,expected_count)
    output=ET.Element(NS+"TEI",{f"{{{XML}}}lang":"en"})
    output.append(copy.deepcopy(header))
    text=ET.SubElement(output,NS+"text")
    body=ET.SubElement(text,NS+"body")
    # SWORD dictionary cross-links address ENTRY KEYS under a real module ID,
    # not source TEI xml:id values. The filter treats 'self' as a literal work.
    # Resolve every existing target against the complete source ID inventory,
    # preserve its exact original selector as TEI @corresp, and explicitly
    # record the lost intra-article scroll precision for editorial review.
    id_to_key={}
    for entry in entries:
        for node in entry.iter():
            identifier=node.get(f"{{{XML}}}id")
            if identifier:
                if identifier in id_to_key:
                    raise ValueError("Duplicate source element XML id")
                id_to_key[identifier]=entry.get("n")
    retargeted=0
    section_links=0
    scripture_exposed=0
    for entry in entries:
        item=copy.deepcopy(entry)
        item.tag=NS+"entryFree"
        del item.attrib["type"]
        # Each entry becomes a standalone SWORD raw payload after tei2mod.
        # Retain its inherited TEI P5 namespace within the native fragment.
        item.attrib["xmlns"]=TEI
        for ref in item.iter(NS+"ref"):
            target=ref.get("target")
            if target and target.startswith("#"):
                if ref.get("corresp"):
                    raise ValueError("Cannot overwrite original TEI ref corresp")
                original_id=target[1:]
                if original_id not in id_to_key:
                    raise ValueError("Unresolved article or section source target")
                key=id_to_key[original_id]
                ref.set("corresp",target)
                ref.set("target",module_id+":"+key)
                retargeted+=1
                if ref.get("type")=="section":
                    section_links+=1
            cref=ref.get("cRef")
            if cref:
                if ref.get("osisRef"):
                    raise ValueError("Cannot overwrite original native Bible reference")
                # The original Bible: OSIS address remains byte-for-byte in
                # @cRef; @osisRef makes the link available to SWORD TEI UI.
                ref.set("osisRef",cref)
                scripture_exposed+=1
        body.append(item)
    outpath.parent.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(output).write(outpath,encoding="utf-8",xml_declaration=True)
    parsed=ET.parse(outpath).getroot()
    produced=list(parsed.find("./"+NS+"text/"+NS+"body"))
    if len(produced)!=len(details):
        raise ValueError("Output count mismatch")
    for original,mapped,entry in zip(entries,produced,details):
        if (mapped.tag!=NS+"entryFree" or mapped.get("n")!=entry["key"] or
            mapped.get(f"{{{XML}}}id")!=entry["xml_id"] or
            "".join(original.itertext())!="".join(mapped.itertext())):
            raise ValueError("Source article text changed by TEI adapter")
        if len(original)!=len(mapped):
            raise ValueError("Source article child nodes were dropped")
    if retargeted!=sum(1 for entry in entries for ref in entry.iter(NS+"ref")
                       if (ref.get("target") or "").startswith("#")):
        raise ValueError("Unconverted native SWORD internal reference")
    report={
      "schema_version":1,"status":"TEI_dictionary_import_input_not_native_approved",
      "source_path":str(source),"source_sha256":digest(source),
      "sword_dictionary_module_id":module_id,
      "sword_link_scheme":"explicit_work_colon_entry_key",
      "sword_import_input":str(outpath),"sword_import_sha256":digest(outpath),
      "source_entry_count":len(entries),"converted_entry_count":len(produced),
      "article_ids_preserved":True,"entry_visible_text_preserved":True,
      "original_child_elements_preserved":True,
      "nested_divisions_preserved_unadapted":nested,
      "internal_references_retargeted_to_source_key":retargeted,
      "original_xml_reference_anchors_preserved_in_corresp":True,
      "section_links_with_reduced_native_scroll_precision":section_links,
      "scripture_references_exposed_via_osisRef":scripture_exposed,
      "source_markup_links_require_reader_audit":True,
      "rights_cleared":False,"publication_permitted":False,
      "entries":details
    }
    reportpath.parent.mkdir(parents=True,exist_ok=True)
    reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                          encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",default="sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml")
    p.add_argument("--output",required=True)
    p.add_argument("--report",required=True)
    p.add_argument("--expected-sha256",required=True)
    p.add_argument("--expected-count",type=int,required=True)
    p.add_argument("--module-id",required=True,
                   help="Installed SWORD dictionary module ID for native cross-links")
    args=p.parse_args()
    report=convert(args.source,args.output,args.report,args.expected_sha256,args.expected_count,args.module_id)
    print(json.dumps({k:v for k,v in report.items() if k!="entries"},indent=2))

if __name__=="__main__":
    main()
