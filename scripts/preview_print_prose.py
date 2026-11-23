#!/usr/bin/env python3
"""Apply OCR-attested missing ISBE article prose to an isolated review candidate.

The exact 1915 print images are not yet proofread. This operation is not
publication-ready, never overwrites the canonical TEI and retains provenance.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

NS="{http://www.tei-c.org/ns/1.0}"
XMLID="{http://www.w3.org/XML/1998/namespace}id"
def q(t): return NS+t
ET.register_namespace("","http://www.tei-c.org/ns/1.0")

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

# UI/navigation/website boilerplate from electronic reproductions is not part
# of the historical encyclopaedia. Target distinctive composed expressions,
# never generic scholarly words such as "editor", "note", or "copyright".
DIGITAL_PARATEXT = re.compile(
    r"(?i)(?:\bCopyright Statement\b|\bBibliography Information\b|"
    r"\bPopular Articles\b|\bFeatured Verse Topics\b|"
    r"\bShare Tweet Save\b|\bJoin PLUS\b|\bSign In\b|"
    r"\bBible Study Tools\b|\bProud member of\b|"
    r"\bNext Article\b|\bPrevious Article\b|"
    r"\bBack to Top\b|\bRead More Articles\b|"
    r"<(?:/)?(?:script|nav|footer|aside|a)(?:\s|>))"
)

def reject_digital_paratext(text, article_key):
    match = DIGITAL_PARATEXT.search(text)
    if match:
        raise ValueError(
            f"Non-content digital paratext in {article_key}: {match.group(0)}"
        )


def apply(source,redirect_manifest,prose_manifest,output,report_path):
    source,output=Path(source),Path(output)
    spec=json.loads(Path(prose_manifest).read_text(encoding="utf-8"))
    if digest(source)!=spec["document_base_sha256"]:
        raise ValueError("Unapproved source SHA256")
    if not spec["prohibited_canonical_promotion"]:
        raise ValueError("Source status cannot be promoted")
    if any(r["approved"] for r in spec["records"]):
        raise ValueError("This generator only handles unapproved specimens")
    for r in spec["records"]:
        if r["print_image_reviewed"] and not r.get("visual_print_witness_review"):
            raise ValueError("A checked historical print page must have a linked review")
        if r.get("print_text_fully_certified"):
            raise ValueError("A partial print check does not certify the whole article")
    if len(spec["records"])!=len({r["source_key"] for r in spec["records"]}) or not spec["records"]:
        raise ValueError("Unexpected source-text revision count")
    redirect=json.loads(Path(redirect_manifest).read_text(encoding="utf-8"))
    if redirect["canonical_sha256"]!=spec["document_base_sha256"]:
        raise ValueError("Redirect/source revision mismatch")
    if len(redirect["records"])!=len({r["article_key"] for r in redirect["records"]}) or not redirect["records"]:
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
    if len(all_candidates)!=len(redirect["records"])+len(spec["records"]): raise ValueError("Overlapping editorial candidates")
    # Apply the separately documented navigation specimens, retaining article IDs.
    for r in redirect["records"]:
        key=r["article_key"]
        article=articles[key]
        children=[x for x in article if x.tag==q("p")]
        if len(children)!=1 or children[0].get(XMLID)!=r["original_empty_paragraph_id"]:
            raise ValueError(f"Original paragraph identity mismatch: {key}")
        p=children[0]
        if (p.text or "").strip() or len(p):
            raise ValueError(f"Unexpected original text in redirect: {key}")
        lead=r["proposed_lead"]
        if not lead.endswith("See "):
            raise ValueError(f"Unverified source redirect lead for {key}")
        p.text=lead
        for i,target_key in enumerate(r["proposed_targets"]):
            target=articles.get(target_key)
            if target is None or target.get(XMLID) is None:
                raise ValueError(f"Unverified navigation destination {target_key}")
            link=ET.SubElement(p,q("ref"),{"type":"article","target":"#"+target.get(XMLID)})
            link.text=r.get("proposed_display_labels",{}).get(target_key,target_key)
            link.tail="." if i==len(r["proposed_targets"])-1 else "; "
        observed=r.get("proposed_print_collated_text", r["observed_secondary_witness_text"])
        actual="".join(p.itertext())
        if actual!=observed:
            raise ValueError(f"Redirect preview differs from witnessed text for {key}")
        affected.add(key)
    # Proposed content-bearing restorations from individually documented historical witnesses.
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
        if not r.get("witness") or not r["witness"].startswith("https://"):
            raise ValueError(f"Historical source URL missing for {key}")
        for block in r["blocks"]:
            reject_digital_paratext(block, key)
        ps[0].text=r["blocks"][0]
        for i,text in enumerate(r["blocks"][1:],start=1):
            new=ET.SubElement(article,q("p"))
            candidate_id=article.get(XMLID)+f"-new-print-prose-{i:03d}"
            if candidate_id in original_ids: raise ValueError("ID collision")
            new.set(XMLID,candidate_id)
            new.text=text
        affected.add(key)
    # Strict text / stable-ID parity outside the declared edited records.
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
        "proposed_redirects":len(redirect["records"]),
        "proposed_historical_text_entries":len(spec["records"]),
        "unchanged_articles_verified":len(articles)-len(affected),
        "original_ids_preserved":len(original_ids),
        "new_xml_ids":len(set(actual_ids)-original_ids),
        "evidence":"1915 volume I searchable text and separately attributed 1915 transcriptions; all require independent page-image comparison",
        "digital_paratext_policy":"distinctive electronic publication notices rejected before candidate serialization",
        "candidate_article_text_blocks_scanned":sum(len(r["blocks"]) for r in spec["records"]),
        "affected_keys":sorted(affected),
    }
    Path(report_path).parent.mkdir(parents=True,exist_ok=True)
    Path(report_path).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",default="workspace/witnesses/crosswire-2.2/ISBE.xml")
    ap.add_argument("--redirects",default="workspace/reviews/redirect-candidate-v1.json")
    ap.add_argument("--prose",default="workspace/reviews/print-prose-candidate-v1.json")
    ap.add_argument("--output",required=True)
    ap.add_argument("--report",required=True)
    opts=ap.parse_args()
    result=apply(opts.source,opts.redirects,opts.prose,opts.output,opts.report)
    print(json.dumps(result,indent=2))
