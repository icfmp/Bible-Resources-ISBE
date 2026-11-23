#!/usr/bin/env python3
"""Locate *possible* original 1915 headword pages despite compound CrossWire keys.

This is an OCR locator and optionally a bounded visual-image evidence emitter.
No OCR inference is treated as editorial certification; visual inspection and
exact source anchors are required before changing a separate edition.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

from scripts.research_1915_print_pages import digest, expected_volume, normalize
from scripts.audit_1915_scripture_candidates import make_digital_queue
from scripts.render_1915_print_evidence import render_pages

def locate(pages, key, limit=4):
    # The original printed heading can vary from the CrossWire digital title.
    # First headword before punctuation is useful for manual-search discovery.
    first = re.split(r"[,;]", key)[0].strip()
    if first.endswith(", BOOK OF"):
        first = first.split(",")[0]
    words = first.split()
    terms = [first]
    if len(words) > 1:
        terms.append(words[0])
    results = []
    for page_no, page in enumerate(pages, 1):
        for lineno, line in enumerate(page.splitlines(), 1):
            for term in terms:
                # Uppercase first-word headings stand out from OCR running
                # headers but do not prove the occurrence is an entry.
                m = re.search(r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])", line, re.I)
                if not m:
                    continue
                found = m.group()
                surrounding = line[max(0, m.start()-35):m.end()+140].strip()
                is_upper = found.isupper()
                score = (4 if is_upper else 1) + (2 if term == first else 0)
                if "INTERNATIONAL STANDARD" in line:
                    score = 0
                if score:
                    results.append({
                        "page": page_no, "line": lineno, "score": score,
                        "term": term, "excerpt": surrounding[:195],
                        "page_image_inspected": False
                    })
    results.sort(key=lambda v: (-v["score"],v["page"],v["line"]))
    selected = []
    for result in results:
        if result["page"] not in {x["page"] for x in selected}:
            selected.append(result)
        if len(selected) == limit:
            break
    return selected

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf", required=True, type=Path)
    p.add_argument("--volume", required=True)
    p.add_argument("--manifest", default="workspace/witnesses/print/1915-volume-witnesses.json")
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--render-pages", action="store_true")
    p.add_argument("--render-limit", type=int, default=3)
    a=p.parse_args()
    manifest=json.loads(Path(a.manifest).read_text())
    witness, = [v for v in manifest["volumes"] if v["volume"]==a.volume]
    if digest(a.pdf)!=witness["pdf_sha256"]:
        raise ValueError("Not the pinned primary print witness")
    pages=subprocess.run(["pdftotext","-layout",str(a.pdf),"-"],check=True,
                         capture_output=True,text=True,timeout=180).stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if len(pages)!=witness["pages"]:
        raise ValueError("Wrong historical print PDF page count")
    q=make_digital_queue(Path("workspace/witnesses/crosswire-2.2/ISBE.xml"))
    keys=sorted({c["article_key"] for c in q["cases"] if expected_volume(c["article_key"])==a.volume})
    rows=[{"key":k,"candidate_pages":locate(pages,k)} for k in keys]
    result={"volume":a.volume,"pdf_sha256":witness["pdf_sha256"],
            "source_text_sha256":q["input_sha256"],"print_verified":False,
            "scope":"OCR locator only, no image/content certification",
            "cases":rows}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for row in rows:
        print("HEADWORD_LOCATOR",json.dumps(row,ensure_ascii=False))
    if a.render_pages:
        best=[]
        for row in rows:
            if row["candidate_pages"]:
                page=row["candidate_pages"][0]["page"]
                if page not in best and len(best)<a.render_limit:
                    best.append(page)
        if best:
            render_pages(a.pdf,a.volume,best,a.manifest)
if __name__=="__main__":
    main()
