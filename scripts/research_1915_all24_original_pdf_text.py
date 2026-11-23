#!/usr/bin/env python3
"""Internal read-only per-article ORIGINAL 1915 PDF text-layer extraction.

Exact SHA-locked print witness, original PDF *text layer* (not new OCR).
Page boundaries are observations; the print text layer is an unreliable
transcription and MUST be compared visually with original page images.
No edits, historical collation approval, or redistribution permission.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

LOCK="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"

def extract(pdf, manifest, review, volume, target):
    pdf=Path(pdf); target=Path(target)
    if sha256(pdf.read_bytes()).hexdigest()!=next(
       v["pdf_sha256"] for v in manifest["volumes"] if v["volume"]==volume):
        raise ValueError("Original printed PDF source SHA mismatch")
    if (manifest.get("canonical_tei_sha256")!=LOCK or
        review.get("canonical_tei_sha256")!=LOCK or
        review.get("schema_version")!=2 or
        review.get("full_historical_collation_certified") is not False or
        review.get("publication_permitted") is not False):
        raise ValueError("Review or original printed source is not locked")
    items=[r for r in review["entries"] if r["volume"]==volume]
    if not items or len({r["source_key"] for r in items})!=len(items):
        raise ValueError("Wrong unique source inventory")
    target.mkdir(parents=True,exist_ok=True)
    pages={}
    for row in items:
        start=row["pdf_page"]
        extra=[r["pdf_page"] for r in row.get("verified_continuation_pages",[])]
        if row.get("pending_continuation_pdf_pages"):
            raise ValueError("Original printed continuation missing")
        for n in [start]+extra:
            if n not in pages:
                result=subprocess.run([
                    "pdftotext","-f",str(n),"-l",str(n),"-layout","-nopgbrk",
                    "-enc","UTF-8",str(pdf),"-"],
                    capture_output=True,check=True,timeout=90)
                pages[n]=result.stdout.decode("utf-8",errors="strict")
    records=[]
    for row in items:
        numbers=[row["pdf_page"]]+[
            p["pdf_page"] for p in row.get("verified_continuation_pages",[])]
        key=row["source_key"]
        text="\n\n--- ORIGINAL 1915 PDF PAGE TRANSITION ---\n\n".join(
            pages[p] for p in numbers)
        dest=target/f"{volume}-{key.replace(' ','_').replace(';','_')}.txt"
        dest.write_text(text,encoding="utf-8")
        records.append({
            "source_key":key,"source_xml_id":row["source_article_xml_id"],
            "volume":volume,"pdf_pages":numbers,"source_original_pdf_sha256":
                next(v["pdf_sha256"] for v in manifest["volumes"] if v["volume"]==volume),
            "pdf_text_layer_sha256":sha256(text.encode()).hexdigest(),
            "pdf_text_layer_reliable_as_original_print":False,
            "requires_visual_original_image_confirmation":True,
            "full_historical_article_collation_certified":False,
            "research_only_filename":dest.name,
        })
    index={"schema_version":1,"original_print_volume":volume,
            "articles":records,"publication_permitted":False,
            "source_modified":False,"original_pdf_layer_not_ground_truth":True}
    (target/"index.json").write_text(
        json.dumps(index,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return index

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf",required=True,type=Path)
    p.add_argument("--volume",required=True)
    p.add_argument("--output-dir",required=True,type=Path)
    p.add_argument("--manifest",type=Path,default=Path("sources/print/1915-volume-witnesses.json"))
    p.add_argument("--review",type=Path,default=Path("workspace/reviews/1915-article-wide-prose-review-v2.json"))
    a=p.parse_args()
    data=extract(a.pdf,json.loads(a.manifest.read_text()),
                 json.loads(a.review.read_text()),a.volume,a.output_dir)
    print(json.dumps({"volume":a.volume,"articles":len(data["articles"]),
                      "pdf_text_layer_not_ground_truth":True},indent=2))
if __name__=="__main__":
    main()
