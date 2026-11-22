#!/usr/bin/env python3
"""Generate an explicit, NONCANONICAL preview of historical ISBE redirects.

Never alters or promotes cleaned/en/ISBE.xml. No claim of 1915 transcription:
the short proposed 'See' text is a modern review aid, not source wording.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "http://www.tei-c.org/ns/1.0"
Q=lambda s: "{"+NS+"}"+s
XMLID="{http://www.w3.org/XML/1998/namespace}id"
ET.register_namespace("",NS)

def article_text(node):
    return "".join(node.itertext())

def preview(source,manifest_path,destination,report_path):
    source=Path(source)
    raw=source.read_bytes()
    lock=hashlib.sha256(raw).hexdigest()
    spec=json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if lock!=spec["canonical_sha256"]:
        raise ValueError("Canonical SHA-256 differs from explicitly locked witness")
    records=spec["records"]
    if len(records)!=10 or len({r["article_key"] for r in records})!=10:
        raise ValueError("Expected exactly ten unique review records")
    if any(r["approved"] or r["source_image_verified"] for r in records):
        raise ValueError("This tool is for UNAPPROVED review specimens only")
    tree=ET.ElementTree(ET.fromstring(raw))
    body=tree.find("./"+Q("text")+"/"+Q("body"))
    if body is None:
        raise ValueError("Missing TEI body")
    articles={a.get("n"):a for a in body}
    if len(articles)!=9380:
        raise ValueError("Unexpected article coverage")
    originals={key:(article_text(article),[n.get(XMLID) for n in article.iter()])
               for key,article in articles.items()}
    ids={n.get(XMLID) for a in articles.values() for n in a.iter()}
    # The canonical P5 has source-backed bibliography wrapper divisions with no ID.
    # Their absence of xml:id is intentional; preserve all existing IDs instead.
    report=[]
    for record in records:
        key=record["article_key"]
        article=articles.get(key)
        if article is None:
            raise ValueError(f"Missing source article: {key}")
        paragraphs=[x for x in article.iter() if x.tag==Q("p")]
        if len(paragraphs)!=1:
            raise ValueError(f"Unexpected original paragraph shape for {key}")
        p=paragraphs[0]
        if p.get(XMLID)!=record["original_empty_paragraph_id"] or len(p) or (p.text or "").strip():
            raise ValueError(f"Not the verified empty source paragraph: {key}")
        if not record["proposed_targets"]:
            raise ValueError("Empty target proposal")
        p.text="See "
        resolved=[]
        for pos,target_key in enumerate(record["proposed_targets"]):
            target=articles.get(target_key)
            if target is None:
                # Expose the gap, do not invent a destination or link.
                item=ET.SubElement(p,Q("seg"),{"type":"unresolved-editorial-preview"})
            else:
                item=ET.SubElement(p,Q("ref"),{"type":"article","target":"#"+target.get(XMLID)})
            item.text=target_key
            item.tail=("." if pos==len(record["proposed_targets"])-1 else "; ")
            resolved.append({"target_key":target_key,"resolved":target is not None})
        report.append({"article_key":key,
            "source_paragraph_xml_id":p.get(XMLID),
            "preview_only":True,
            "proposed_visible_text":article_text(p),
            "proposed_targets":resolved,
            "secondary_witness":record["secondary_witness_url"]})
    for key,article in articles.items():
        after_ids=[n.get(XMLID) for n in article.iter() if n.get(XMLID)]
        before_text,before_ids=originals[key]
        if key not in {r["article_key"] for r in records}:
            if article_text(article)!=before_text or after_ids!=before_ids:
                raise ValueError(f"Untouched article drift: {key}")
        elif not all(uid in after_ids for uid in before_ids):
            raise ValueError(f"Original IDs lost in proposed entry: {key}")
    all_ids=[n.get(XMLID) for article in articles.values()
             for n in article.iter() if n.get(XMLID)]
    if len(all_ids)!=len(set(all_ids)):
        raise ValueError("Duplicate IDs")
    out=Path(destination)
    out.parent.mkdir(parents=True,exist_ok=True)
    tree.write(out,encoding="utf-8",xml_declaration=True)
    # Independently reopen serialized candidate and verify original source parity.
    check=ET.parse(out).getroot().find("./"+Q("text")+"/"+Q("body"))
    if check is None or len(check)!=9380:
        raise ValueError("Serialized candidate damaged corpus")
    check_articles={a.get("n"):a for a in check}
    for key,(txt,original_ids) in originals.items():
        article=check_articles[key]
        if key not in {r["article_key"] for r in records}:
            if article_text(article)!=txt:
                raise ValueError(f"Serialized unexpected text drift: {key}")
        current_ids={x.get(XMLID) for x in article.iter()}
        if not set(original_ids).issubset(current_ids):
            raise ValueError(f"Serialized original ID lost: {key}")
    result={"source_sha256":lock,"candidate_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
            "noncanonical":True,"changed_articles":len(report),
            "untouched_articles_verified":len(articles)-len(report),
            "original_ids_preserved":True,
            "proposed_links_unresolved":sum(not p["resolved"] for r in report for p in r["proposed_targets"]),
            "records":report}
    dst=Path(report_path)
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",type=Path,default=Path("cleaned/en/ISBE.xml"))
    ap.add_argument("--manifest",type=Path,default=Path("workspace/reviews/redirect-candidate-v1.json"))
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    result=preview(args.source,args.manifest,args.output,args.report)
    print(json.dumps({k:v for k,v in result.items() if k!="records"},indent=2))
    for r in result["records"]:
        print(r["article_key"],":",r["proposed_visible_text"],
              "resolved",sum(x["resolved"] for x in r["proposed_targets"]),
              "/",len(r["proposed_targets"]))

if __name__=="__main__":
    main()
