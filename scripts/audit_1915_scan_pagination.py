#!/usr/bin/env python3
"""Read-only continuity inventory of printed 1915 folios in SHA-pinned PDFs.

OCR headers are only candidate pagination evidence; use adjacent original
page images to certify any apparent missing leaves before editorial action.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

HEADER=re.compile(r"INTERNATIONAL\s+STANDARD\s+BIBLE\s+ENCYCLOP(?:A)?EDIA",re.I)
NUM=re.compile(r"(?<![\d])([1-3]\d{2,3})(?![\d])")

def printed_folio(page):
    lines=[x.strip() for x in page.splitlines() if x.strip()][:6]
    head=" ".join(lines[:3])
    if not HEADER.search(head):
        return None
    numbers=[int(m.group(1)) for m in NUM.finditer(head)]
    numbers=[n for n in numbers if 200<=n<=3541]
    # Most headings contain one physical printed folio number. If the OCR
    # header is ambiguous, avoid guessing and simply skip that page.
    return numbers[0] if len(numbers)==1 else None

def audit_pages(pages):
    folios=[printed_folio(page) for page in pages]
    gaps=[]
    for index in range(len(folios)-1):
        left,right=folios[index:index+2]
        if left is None or right is None:
            continue
        if 2<=right-left<=12:
            candidate={"pdf_page_before_1_based":index+1,
                       "printed_before":left,"pdf_page_after_1_based":index+2,
                       "printed_after":right,
                       "unseen_printed_folios":list(range(left+1,right)),
                       "disposition":"candidate_for_image_review",
                       "confirmed_missing_from_print":False}
            # A one-digit OCR misread (e.g. 2950 -> 2960) can resemble a
            # ten-page omission. Keep the candidate visible and append
            # neighboring-header evidence, never an automatic dismissal.
            next_index=index+2
            repeat_index=index+(right-left)
            next_folio=folios[next_index] if next_index<len(folios) else None
            repeat_folio=folios[repeat_index] if repeat_index<len(folios) else None
            candidate["ocr_followup"]={
                "next_pdf_page_1_based":next_index+1 if next_index<len(folios) else None,
                "next_recognized_folio":next_folio,
                "expected_next_without_gap":left+2,
                "later_pdf_page_1_based":repeat_index+1 if repeat_index<len(folios) else None,
                "later_recognized_folio":repeat_folio,
                "probable_header_misread_not_image_certified":(
                    right-left>=3 and next_folio==left+2 and repeat_folio==right),
            }
            gaps.append(candidate)
    return {"pdf_pages":len(pages),"recognized_printed_folios":sum(n is not None for n in folios),
            "adjacent_page_jump_candidates":len(gaps),"candidate_gaps":gaps,
            "method":"strict original-text OCR header detection; no page-image certification"}

def audit_pdf(pdf,manifest,volume):
    pdf=Path(pdf)
    data=json.loads(Path(manifest).read_text(encoding="utf-8"))
    source,=[v for v in data["volumes"] if v["volume"]==str(volume)]
    digest=sha256(pdf.read_bytes()).hexdigest()
    if digest!=source["pdf_sha256"]:
        raise ValueError("Print witness SHA-256 drift")
    pages=subprocess.run(["pdftotext","-layout",str(pdf),"-"],
                         capture_output=True,text=True,check=True,timeout=180).stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if len(pages)!=source["pages"]:
        raise ValueError("Print witness page-count drift")
    return {"volume":str(volume),"source_pdf_sha256":digest,
            "bibliographic_source":data["bibliographic_citation"],**audit_pages(pages)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf",required=True,type=Path)
    p.add_argument("--volume",required=True)
    p.add_argument("--manifest",default="sources/print/1915-volume-witnesses.json")
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=audit_pdf(a.pdf,a.manifest,a.volume)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
