#!/usr/bin/env python3
"""Compare all empty digital ISBE entries to independent 1915 volume OCR.

This is research triage only: OCR hits cannot authorize verbatim transcription,
paragraph reconstruction, automatic deletion, or editorial publication.
"""
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

ARCHIVE_ITEMS = {
    "I": "cu31924008045423",
    "II": "cu31924063473403",
    "III": "cu31924095207126",
    "IV": "cu31924063472827",
    "V": "cu31924063472835",
}
USER_AGENT = "Bible-Resources-ISBE/1.0 (public-domain 1915 bibliography audit)"

def clean(text):
    return re.sub(r"[^A-Z0-9]+", " ", text.upper()).strip()

def search_headword(lines, key):
    """Return OCR line candidates; never equate text mentions with headings."""
    desired = clean(key)
    if not desired:
        return []
    hits = []
    # OCR headings can wrap, so inspect two adjacent lines, but do not report
    # unanchored occurrences as verified article existence.
    for i, line in enumerate(lines):
        line_norm = clean(line)
        if not line_norm:
            continue
        before = clean(lines[i-1]) if i else ""
        after = clean(lines[i+1]) if i+1 < len(lines) else ""
        # Prefer a line where the headword starts the line; ignore OCR prose.
        starts = line_norm == desired or line_norm.startswith(desired + " ")
        if starts:
            hits.append({
                "line_number":i+1,
                "ocr_heading_line":line.strip()[:220],
                "previous_line":lines[i-1].strip()[:120] if i else "",
                "next_line":lines[i+1].strip()[:160] if i+1 < len(lines) else "",
                "candidate_only":True,
            })
        if len(hits) >= 15:
            break
    return hits

def analyze(ledger, ocr_by_volume):
    cases=[]
    for case in ledger["cases"]:
        key=case["source_key"]
        matches={}
        for volume, record in ocr_by_volume.items():
            rows=search_headword(record["lines"],key)
            if rows:
                matches[volume]=rows
        cases.append({
            "source_key":key,
            "paragraph_xml_id":case["paragraph_xml_id"],
            "matches_by_volume":matches,
            "status":"ocr_heading_candidates" if matches else "no_ocr_heading_candidate",
            "printed_page_verified":False,
            "source_transcription_approved":False,
        })
    return cases

def fetch_ocr(volume,item,timeout=90):
    url=f"https://archive.org/download/{item}/{item}_djvu.txt"
    request=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
    with urllib.request.urlopen(request,timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"Unexpected HTTP {response.status} for {volume}")
        raw=response.read(25_000_001)
    if len(raw)>25_000_000 or len(raw)<100_000:
        raise ValueError(f"Unexpected OCR size for {volume}: {len(raw)}")
    text=raw.decode("utf-8",errors="replace")
    if "INTERNATIONAL" not in text.upper():
        raise ValueError(f"No ISBE identity found in OCR {volume}")
    return {
        "volume":volume,"internet_archive_item":item,"url":url,
        "ocr_sha256":hashlib.sha256(raw).hexdigest(),
        "bytes":len(raw),"lines":text.splitlines(),
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--source-directory",type=Path,default=None,
                   help="Use separately downloaded *_djvu.txt files for offline repeatability")
    a=p.parse_args()
    ledger=json.loads(a.ledger.read_text(encoding="utf-8"))
    if len(ledger["cases"])!=31:
        raise SystemExit("Expected 31 empty-source article records")
    ocr={}
    for vol,item in ARCHIVE_ITEMS.items():
        if a.source_directory:
            raw=(a.source_directory/f"{item}_djvu.txt").read_bytes()
            if len(raw)<100_000:
                raise ValueError(f"Too short: {item}")
            record={
                "volume":vol,"internet_archive_item":item,
                "url":f"https://archive.org/details/{item}",
                "ocr_sha256":hashlib.sha256(raw).hexdigest(),
                "bytes":len(raw),"lines":raw.decode("utf-8",errors="replace").splitlines(),
            }
        else:
            record=fetch_ocr(vol,item)
        ocr[vol]=record
        print(f"Volume {vol}: {record['bytes']} OCR bytes; SHA256 {record['ocr_sha256']}")
    cases=analyze(ledger,ocr)
    result={
        "purpose":"Preliminary full-corpus headword comparison; NOT page-image verified",
        "canonical_tei_sha256":ledger["baseline_canonical_tei_sha256"],
        "volumes":[{k:v for k,v in x.items() if k!="lines"} for x in ocr.values()],
        "entries_checked":len(cases),
        "entries_with_candidates":sum(bool(x["matches_by_volume"]) for x in cases),
        "entries_without_candidates":sum(not x["matches_by_volume"] for x in cases),
        "cases":cases,
    }
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("RESULTS", result["entries_with_candidates"],"candidate headwords;",
          result["entries_without_candidates"],"without OCR heading candidate")
    for case in cases:
        vols=",".join(case["matches_by_volume"]) or "(none)"
        count=sum(len(x) for x in case["matches_by_volume"].values())
        print(f"{case['source_key']}: volumes={vols}; candidates={count}")

if __name__=="__main__":
    main()
