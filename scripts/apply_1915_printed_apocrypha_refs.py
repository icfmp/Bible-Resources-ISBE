#!/usr/bin/env python3
"""Apply exact source-printed Apocrypha reference repairs to a NEW ISBE TEI.

The generic operation changes one explicit Scripture ref and the directly
preceding tail, with exact prior-edition/text/hash/image locks and byte-for-
byte inverse verification. No global verse remapping or source mutation.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from scripts.audit_tei_structure import analyze

T = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"
LOCK = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
ET.register_namespace("", "http://www.tei-c.org/ns/1.0")
ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def text_digest(s):
    return sha256(s.encode("utf-8")).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def index(root):
    if root.tag != T + "TEI":
        raise ValueError("Expected official TEI P5")
    body = root.find(f"./{T}text/{T}body")
    if body is None or len(body) != 9380:
        raise ValueError("Wrong original article population")
    result = {}
    for item in body:
        key = item.get("n")
        if not key or not item.get(ID) or key in result:
            raise ValueError("Missing/duplicate article IDs")
        result[key] = item
    return result


def validate_ledger(spec, manifest, canonical):
    if (spec.get("schema_version") != 1
            or spec.get("canonical_source_sha256") != LOCK
            or spec.get("original_canonical_unchanged") is not True
            or spec.get("previous_noncanonical_layer_unchanged") is not True
            or spec.get("previous_noncanonical_layer") != "1915_16_exact_prose_corrections"
            or spec.get("full_1915_historical_article_collation_certified") is not False
            or spec.get("redistribution_authorized") is not False):
        raise ValueError("Unsupported source, editorial layer or release permission")
    if manifest.get("canonical_tei_sha256") != LOCK:
        raise ValueError("Historical 1915 volume witness mismatch")
    vol = next((v for v in manifest["volumes"] if v["volume"] == "2"), None)
    if (vol is None or spec.get("witness_pdf_sha256") != vol["pdf_sha256"]
            or not isinstance(spec.get("witness_jpeg_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", spec["witness_jpeg_sha256"])
            or not isinstance(spec.get("previous_noncanonical_tei_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", spec["previous_noncanonical_tei_sha256"])
            or not spec.get("original_print_quotation", "").startswith("Ad Est 13 9")
            or not spec.get("osis_book_authority", "").startswith("https://wiki.crosswire.org/")):
        raise ValueError("Wrong original 1915 printed or OSIS-source witness")
    orig = index(canonical)
    rows = spec.get("decisions")
    if not isinstance(rows, list) or len(rows) != 1:
        raise ValueError("Only one individually reviewed source-target correction exists")
    seen = set()
    for d in rows:
        key = d.get("source_key")
        article = orig.get(key)
        identity = (key, d.get("source_ref_xml_id"))
        if identity in seen:
            raise ValueError("Duplicated exact scripture reference decision")
        seen.add(identity)
        if (article is None or article.get(ID) != d.get("source_article_xml_id")
                or d.get("approved_for_separate_editorial_tei") is not True
                or d.get("operation") != "replace_one_scripture_ref_with_preceding_tail"
                or d.get("printed_folio") != 1153
                or d.get("pdf_page") != 505
                or d.get("print_reading") != "Ad Est 13 9"
                or not isinstance(d.get("rationale"), str) or len(d["rationale"]) < 90
                or not re.fullmatch(r"[0-9a-f]{64}",d.get("previous_paragraph_text_sha256",""))
                or not re.fullmatch(r"Bible:[A-Za-z0-9]+\.[0-9]+\.[0-9]+",
                                    d.get("source_ref_new_cRef",""))
                or d.get("source_ref_new_cRef") == d.get("source_ref_original_cRef")):
            raise ValueError("Unreviewed reference decision")
        ref_matches = [n for n in article.iter(T+"ref") if n.get(ID)==d.get("source_ref_xml_id")]
        if (len(ref_matches)!=1 or ref_matches[0].get("cRef")!=d.get("source_ref_original_cRef")
                or ref_matches[0].text != d.get("source_ref_original_visible")):
            raise ValueError("Changed original CrossWire reference")
        for name in ("preceding_ref_original_tail","preceding_ref_new_tail",
                     "source_ref_original_visible","source_ref_new_visible"):
            if not d.get(name) or not isinstance(d.get(name),str):
                raise ValueError("Missing old/new exact printed and digital text")
        if ("Additions to" not in d["preceding_ref_original_tail"]
                or not d["preceding_ref_new_tail"].endswith("Ad ")
                or d["source_ref_new_visible"] != "Est 13 9"):
            raise ValueError("The historical quoted source would not be restored")
    return rows


def apply(root, decisions):
    items=index(root)
    original={k:ET.tostring(v,encoding="utf-8") for k,v in items.items()}
    IDs=[node.get(ID) for article in items.values() for node in article.iter() if node.get(ID)]
    changed=set()
    report=[]
    for d in decisions:
        article=items.get(d["source_key"])
        if article is None or article.get(ID)!=d["source_article_xml_id"]:
            raise ValueError("Wrong prior historical article")
        paras=[p for p in article.iter(T+"p") if p.get(ID)==d["source_paragraph_xml_id"]]
        if len(paras)!=1:
            raise ValueError("Wrong preceding historical paragraph")
        para=paras[0]
        old_para="".join(para.itertext())
        if text_digest(old_para)!=d["previous_paragraph_text_sha256"]:
            raise ValueError("Earlier historical printed sentence drift")
        children=list(para)
        positions=[i for i,x in enumerate(children) if x.get(ID)==d["source_ref_xml_id"]]
        if len(positions)!=1 or positions[0]==0:
            raise ValueError("Missing or unpaired scripture reference")
        n=positions[0]
        prev,ref=children[n-1],children[n]
        if (prev.tag!=T+"ref" or ref.tag!=T+"ref"
                or prev.get(ID)!=d["preceding_ref_xml_id"]
                or prev.get("cRef")!=d["preceding_ref_expected_cRef"]
                or prev.tail!=d["preceding_ref_original_tail"]
                or ref.text!=d["source_ref_original_visible"]
                or ref.get("cRef")!=d["source_ref_original_cRef"]
                or ref.get("type")!=d["source_ref_type"]
                or len(ref)>0):
            raise ValueError("Wrong actual prior verse and context; do not remap")
        prior=ET.tostring(article,encoding="utf-8")
        prior_tail, prior_text, prior_target=prev.tail,ref.text,ref.get("cRef")
        prev.tail=d["preceding_ref_new_tail"]
        ref.text=d["source_ref_new_visible"]
        ref.set("cRef",d["source_ref_new_cRef"])
        revised="".join(para.itertext())
        if d["print_reading"] not in revised or revised==old_para:
            raise ValueError("Original 1915 display was not restored")
        final=ET.tostring(article,encoding="utf-8")
        prev.tail,ref.text=prior_tail,prior_text
        ref.set("cRef",prior_target)
        if ET.tostring(article,encoding="utf-8")!=prior:
            raise ValueError("Non-reversible visual text or reference edit")
        prev.tail=d["preceding_ref_new_tail"]
        ref.text=d["source_ref_new_visible"]
        ref.set("cRef",d["source_ref_new_cRef"])
        if ET.tostring(article,encoding="utf-8")!=final:
            raise ValueError("Reapplication modified unrelated XML")
        changed.add(d["source_key"])
        report.append({
            "source_key":d["source_key"],
            "source_article_xml_id":article.get(ID),
            "ref_xml_id":ref.get(ID),
            "before_cRef":prior_target,
            "after_cRef":ref.get("cRef"),
            "prior_paragraph_sha256":text_digest(old_para),
            "revised_paragraph_sha256":text_digest(revised),
            "print_volume_pdf_sha256":d.get("print_pdf_sha256"),
            "reversible":True,
        })
    if [n.get(ID) for a in items.values() for n in a.iter() if n.get(ID)]!=IDs:
        raise ValueError("Unchanged original XML IDs required")
    if any(ET.tostring(a,encoding="utf-8")!=original[k]
           for k,a in items.items() if k not in changed):
        raise ValueError("Unrelated original text changed")
    return changed,report


def run(source, prior, prior_report, prior_validator, ledger, output, report,
        derived_validator, derived_fidelity):
    source,prior,output=Path(source),Path(prior),Path(output)
    if len({p.resolve() for p in (source,prior,output)})!=3:
        raise ValueError("Source and prior witnesses must never be overwritten")
    if digest(source)!=LOCK:
        raise ValueError("CrossWire source TEI changed")
    spec=read(ledger)
    prior_sha=digest(prior)
    state=read(prior_report)
    validator=read(prior_validator)
    if (spec.get("previous_noncanonical_tei_sha256")!=prior_sha
            or state.get("revised_sha256")!=prior_sha
            or state.get("additional_print_fragments_corrected")!=16
            or state.get("article_count")!=9380
            or state.get("publication_permitted") is not False
            or validator.get("expected_candidate_sha256")!=prior_sha
            or validator.get("noncanonical_review_only") is not True):
        raise ValueError("Wrong previous sixteen-correction editorial layer")
    decisions=validate_ledger(spec,read(ROOT/"sources/print/1915-volume-witnesses.json"),
                              ET.parse(source).getroot())
    root=ET.parse(prior).getroot()
    changed,edits=apply(root,decisions)
    output.parent.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(root).write(output,encoding="utf-8",xml_declaration=True)
    reread=index(ET.parse(output).getroot())
    if len(reread)!=9380:
        raise ValueError("Saved article count changed")
    profile=analyze(output)
    if profile["profile_rule_findings"] or profile["duplicate_xml_ids"]:
        raise ValueError("Strict TEI P5 project profile violated")
    result={
        "canonical_sha256":LOCK,
        "previous_editorial_sha256":prior_sha,
        "revised_sha256":digest(output),
        "article_count":len(reread),
        "source_article_identities_preserved":True,
        "scripture_visible_and_target_deltas":len(edits),
        "changed_articles":sorted(changed),
        "unaffected_articles":len(reread)-len(changed),
        "original_crosswire_unchanged":True,
        "previous_editorial_unchanged":True,
        "full_original_print_article_collation_certified":False,
        "publication_permitted":False,
        "changes":edits,
    }
    derived={**validator,"expected_candidate_sha256":result["revised_sha256"],
             "review_delta_ledger":str(ledger),"noncanonical_review_only":True}
    fidelity={
        "candidate_sha256":result["revised_sha256"],
        "article_parity":"PASS","serialized_profile_check":"PASS",
        "publication_permitted":False,"noncanonical":True,
        "independent_human_peer_review":False,
        "changed_print_attested_scripture_ref_deltas":len(edits),
    }
    for target,value in ((report,result),(derived_validator,derived),
                         (derived_fidelity,fidelity)):
        dest=Path(target)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=Path("cleaned/en/ISBE.xml"))
    for name in ("prior","prior-report","prior-validator","ledger","output",
                 "report","derived-validator","derived-fidelity"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    result=run(a.source,a.prior,a.prior_report,a.prior_validator,a.ledger,
               a.output,a.report,a.derived_validator,a.derived_fidelity)
    print(json.dumps({"scripture_visible_and_target_deltas":result["scripture_visible_and_target_deltas"],
                      "changed_articles":result["changed_articles"],
                      "publication_permitted":False},indent=2))


if __name__=="__main__":
    main()
