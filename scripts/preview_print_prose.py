#!/usr/bin/env python3
"""Apply OCR-attested missing ISBE article prose to an isolated review candidate.

The exact 1915 print images are not yet proofread. This operation is not
publication-ready, never overwrites the canonical TEI and retains provenance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

NS="{http://www.tei-c.org/ns/1.0}"
XMLID="{http://www.w3.org/XML/1998/namespace}id"
def q(t): return NS+t
ET.register_namespace("","http://www.tei-c.org/ns/1.0")

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def apply(source,redirect_manifest,prose_manifest,output,report_path):
    source,output=Path(source),Path(output)
    spec=json.loads(Path(prose_manifest).read_text(encoding="utf-8"))
    if digest(source)!=spec["document_base_sha256"]:
        raise ValueError("Unapproved source SHA256")
    if not spec["prohibited_canonical_promotion"]:
        raise ValueError("Source status cannot be promoted")
    if any(r["print_image_reviewed"] or r["approved"] for r in spec["records"]):
        raise ValueError("This generator only handles unapproved specimens")
    if len(spec["records"])!=3:
        raise ValueError("Unexpected source-text revision count")
    redirect=json.loads(Path(redirect_manifest).read_text(encoding="utf-8"))
    if redirect["canonical_sha256"]!=spec["document_base_sha256"]:
        raise ValueError("Redirect/source revision mismatch")
    if len(redirect["records"])!=10:
        raise ValueError("Expected ten scoped redirect candidates")
    root=ET.parse(source).getroot()
    body=root.find("./"+q("text")+"/"+q("body"))
    if body is None: raise ValueError("TEI body missing")
    articles={a.get("n"):a for a in body}
    if len(articles)!=9380: raise ValueError("Source coverage changed")
    assert set(articles)=={a.get("n") for a in body}
    original_ids={node.get(XMLID) for article in body for node in article.iter() if node.get(XMLID)}
    original_text={key:"".join(article.itertext()) for key,article in articles.items()}
    affected=set()
    all_candidates={r["article_key"] for r in redirect["records"]}|{r["source_key"] for r in spec["records"]}
    if len(all_candidates)!=13: raise ValueError("Overlapping editorial candidates")
    # Apply the already-reviewed 10 navigation specimens, retaining article IDs.
    for r in redirect["records"]:
        key=r["article_key"]
        article=articles[key]
        children=[x for x in article if x.tag==q("p")]
        if len(children)!=1 or children[0].get(XMLID)!=r["original_empty_paragraph_id"]:
            raise ValueError(f"Original paragraph identity mismatch: {key}")
        p=children[0]
        if (p.text or "").strip() or len(p):
            raise ValueError(f"Unexpected original text in redirect: {key}")
        p.text="See "
        for i,target_key in enumerate(r["proposed_targets"]):
            target=articles.get(target_key)
            if target is None or target.get(XMLID) is None:
                raise ValueError(f"Unverified navigation destination {target_key}")
            link=ET.SubElement(p,q("ref"),{"type":"article","target":"#"+target.get(XMLID)})
            link.text=r.get("proposed_display_labels",{}).get(target_key,target_key)
            link.tail="." if i==len(r["proposed_targets"])-1 else "; "
        affected.add(key)
    # Three content-bearing source-text restorations from 1915 PDF text.
    for r in spec["records"]:
        key=r["source_key"]
        article=articles[key]
        ps=[x for x in article if x.tag==q("p")]
        if len(ps)!=1 or ps[0].get(XMLID)!=r["source_paragraph_id"]:
            raise ValueError(f"Original paragraph identity mismatch: {key}")
        if (ps[0].text or "").strip() or len(ps[0]):
            raise ValueError("Original blank entry unexpectedly contains content")
        if not r["blocks"] or any(not t.strip() for t in r["blocks"]):
            raise ValueError("Blank historical source candidate block")
        ps[0].text=r["blocks"][0]
        for i,text in enumerate(r["blocks"][1:],start=1):
            new=ET.SubElement(article,q("p"))
            candidate_id=article.get(XMLID)+f"-new-print-prose-{i:03d}"
            if candidate_id in original_ids: raise ValueError("ID collision")
            new.set(XMLID,candidate_id)
            new.text=text
        affected.add(key)
    # Strict text / stable-ID parity outside the 13 edited records.
    for key,article in articles.items():
        if key not in affected and original_text[key]!="".join(article.itertext()):
            raise ValueError(f"Unexpected unrelated text change: {key}")
    after_ids={node.get(XMLID) for article in body for node in article.iter() if node.get(XMLID)}
    if not original_ids.issubset(after_ids):
        raise ValueError("Lost original XML IDs")
    output.parent.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(root).write(output,encoding="utf-8",xml_declaration=True)
    check=ET.parse(output).getroot().find("./"+q("text")+"/"+q("body"))
    if check is None or len(check)!=9380: raise ValueError("Serialized corpus coverage mismatch")
    check_articles={a.get("n"):a for a in check}
    for key,article in check_articles.items():
        if key not in affected and original_text[key]!="".join(article.itertext()):
            raise ValueError(f"Serialized text drift: {key}")
    actual_ids=[n.get(XMLID) for article in check for n in article.iter() if n.get(XMLID)]
    if len(actual_ids)!=len(set(actual_ids)) or not original_ids.issubset(set(actual_ids)):
        raise ValueError("Serialized XML identifier defect")
    report={
        "canonical_source_sha256":digest(source),
        "provisional_candidate_sha256":digest(output),
        "noncanonical":True,
        "publication_permitted":False,
        "original_entries":9380,
        "proposed_redirects":10,
        "proposed_historical_text_entries":3,
        "unchanged_articles_verified":9370-3,
        "original_ids_preserved":len(original_ids),
        "new_xml_ids":len(set(actual_ids)-original_ids),
        "evidence":"1915 volume I searchable text; requires page-image comparison",
        "affected_keys":sorted(affected),
    }
    Path(report_path).parent.mkdir(parents=True,exist_ok=True)
    Path(report_path).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",default="cleaned/en/ISBE.xml")
    ap.add_argument("--redirects",default="workspace/reviews/redirect-candidate-v1.json")
    ap.add_argument("--prose",default="workspace/reviews/print-prose-candidate-v1.json")
    ap.add_argument("--output",required=True)
    ap.add_argument("--report",required=True)
    opts=ap.parse_args()
    result=apply(opts.source,opts.redirects,opts.prose,opts.output,opts.report)
    print(json.dumps(result,indent=2))
