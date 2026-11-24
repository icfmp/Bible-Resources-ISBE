#!/usr/bin/env python3
"""Select source-attested dictionary-to-dictionary links near article openings.

Produces a *diagnostic* sample register; no historical text, targets or markup
are rewritten. A link in the module is not yet a verified GUI navigation.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

TEI="{http://www.tei-c.org/ns/1.0}"
XML="{http://www.w3.org/XML/1998/namespace}"

def digest(path):
    h=sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def entries(path, expected_tag):
    body=ET.parse(path).getroot().find("./"+TEI+"text/"+TEI+"body")
    if body is None:
        raise ValueError("Missing TEI dictionary body")
    data={}
    for entry in body:
        key=entry.get("n")
        if entry.tag!=TEI+expected_tag or not key or key in data:
            raise ValueError("Invalid wrapper or duplicate key")
        data[key]=entry
    return data

def ref_offsets(entry):
    """Return reference elements at true concatenated-text offsets."""
    refs=[]
    offset=0
    def scan(node):
        nonlocal offset
        if node.tag==TEI+"ref":
            refs.append((offset,node))
        if node.text:
            offset+=len(node.text)
        for child in node:
            scan(child)
            if child.tail:
                offset+=len(child.tail)
    scan(entry)
    return refs

def analyse(source,adapted,output,limit=25):
    old=entries(source,"div")
    new=entries(adapted,"entryFree")
    if old.keys()!=new.keys():
        raise ValueError("Changed dictionary entry inventory")
    id_to_article={}
    for key,item in old.items():
        if item.get("type")!="entry":
            raise ValueError("Not a historical article")
        for node in item.iter():
            ident=node.get(XML+"id")
            if ident:
                if ident in id_to_article:
                    raise ValueError("Duplicate original ID")
                id_to_article[ident]=key
    choices=[]
    candidate_count=0
    cross_count=0
    for key,item in old.items():
        refs=ref_offsets(item)
        converted=ref_offsets(new[key])
        if len(refs)!=len(converted):
            raise ValueError("Changed number of link nodes")
        first_clickable=next((offset for offset,ref in refs
                              if ref.get("cRef") or (ref.get("target") or "").startswith("#")),None)
        text="".join(item.itertext())
        first_for_article=None
        for (offset,ref),(_,replacement) in zip(refs,converted):
            target=ref.get("target") or ""
            if not target.startswith("#"):
                continue
            dest=id_to_article.get(target[1:])
            if dest is None:
                raise ValueError(f"Unresolved original target {target}")
            if replacement.get("target")!="self:"+dest or replacement.get("corresp")!=target:
                raise ValueError(f"Original crosslink not correctly mapped: {key}")
            if dest==key:
                continue
            cross_count+=1
            if "".join(ref.itertext())!="".join(replacement.itertext()):
                raise ValueError("Link text was changed")
            label="".join(ref.itertext()).strip()
            if not label or not text or first_for_article is not None:
                continue
            first_for_article={
                "source_article":key,
                "destination_article":dest,
                "link_text":label,
                "original_xml_target":target,
                "native_link_target":"self:"+dest,
                "first_cross_article_link_text_offset":offset,
                "is_first_clickable_reference":offset==first_clickable,
                "article_text_length":len(text),
                "source_text_preserved":text=="".join(new[key].itertext())
            }
        if first_for_article:
            candidate_count+=1
            choices.append(first_for_article)
    # Prefer first true hyperlink near the start, not a hidden/screen-deep
    # source location. Only actual GUI screenshots determine click geometry.
    choices.sort(key=lambda x:(not x["is_first_clickable_reference"],
                               x["first_cross_article_link_text_offset"],
                               -min(x["article_text_length"],300),x["source_article"]))
    report={
        "schema_version":1,
        "source_sha256":digest(source),
        "adapted_sha256":digest(adapted),
        "source_article_count":len(old),
        "cross_article_reference_count":cross_count,
        "articles_with_cross_article_references":candidate_count,
        "chosen_samples":choices[:limit],
        "source_modified":False,
        "actual_GUI_dictionary_link_click_verified":False,
        "requires_reader_screenshot_review":True
    }
    out=Path(output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True)
    p.add_argument("--adapted",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--limit",type=int,default=25)
    a=p.parse_args()
    if not 1<=a.limit<=100:
        raise SystemExit("--limit requires 1..100")
    report=analyse(a.source,a.adapted,a.output,a.limit)
    print(json.dumps({k:v for k,v in report.items() if k!="chosen_samples"},
                     indent=2,ensure_ascii=False))
    print(json.dumps({"first_sample":report["chosen_samples"][0] if report["chosen_samples"] else None},
                     ensure_ascii=False))
    if not report["chosen_samples"]:
        raise SystemExit("No dictionary-to-dictionary link sample available")

if __name__=="__main__":
    main()
