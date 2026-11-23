#!/usr/bin/env python3
"""Full-corpus readback of an actual SWORD dictionary using native mod2imp.

Do NOT claim output parity merely because tei2mod exited successfully. This
validator compares every dictionary key, exact Unicode text, and XML element
structure from the intended importer TEI document with native raw SWORD
module readback. It fails closed on a missing entry or modified data.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

NS="{http://www.tei-c.org/ns/1.0}"
def digest(path):
    h=sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def read_expected(path):
    root=ET.parse(path).getroot()
    body=root.find("./"+NS+"text/"+NS+"body")
    if body is None:
        raise ValueError("Missing expected TEI dictionary body")
    data={}
    for entry in body:
        key=entry.get("n") or entry.get("sortKey")
        if entry.tag!=NS+"entryFree" or key in data or not key:
            raise ValueError("Invalid/duplicate dictionary entry")
        data[key]=entry
    return data

def read_native_imp(path):
    data={}
    key=None
    chunks=[]
    with Path(path).open("r",encoding="utf-8") as f:
        for line in f:
            if line.startswith("$$$"):
                if key is not None:
                    if key in data:
                        raise ValueError("Duplicate native module key")
                    data[key]="".join(chunks)
                key=line[3:].rstrip("\r\n")
                chunks=[]
            elif key is not None:
                chunks.append(line)
            elif line.strip():
                raise ValueError("Unexpected text before first native key")
    if key is not None:
        if key in data:
            raise ValueError("Duplicate final native key")
        data[key]="".join(chunks)
    return data

def structure(node):
    # Exclude whitespace that native SWORD adds solely *outside* entryFree;
    # preserve all in-article strings, nodes and attributes exactly.
    return (node.tag,tuple(sorted(node.attrib.items())),
            node.text or "",
            tuple(structure(c) for c in node),node.tail or "")

def analyze(expected_path,native_path,report_path):
    expected=read_expected(expected_path)
    native=read_native_imp(native_path)
    expected_keys=set(expected)
    native_keys=set(native)
    missing=sorted(expected_keys-native_keys)
    unexpected=sorted(native_keys-expected_keys)
    text_mismatch=[]
    markup_mismatch=[]
    parse_failures=[]
    for key in sorted(expected_keys & native_keys):
        raw=native[key].strip()
        try:
            actual=ET.fromstring(raw)
        except ET.ParseError as e:
            parse_failures.append({"key":key,"error":str(e)})
            continue
        source=expected[key]
        a="".join(actual.itertext())
        b="".join(source.itertext())
        if a!=b:
            text_mismatch.append({
               "key":key,
               "expected_utf8_sha256":sha256(b.encode("utf-8")).hexdigest(),
               "native_utf8_sha256":sha256(a.encode("utf-8")).hexdigest(),
               "expected_characters":len(b),"native_characters":len(a)
            })
        # The importer might preserve the string but change attributes and
        # inline element boundaries; this is substantive and must be logged.
        if structure(actual)[:4]!=structure(source)[:4]:
            markup_mismatch.append(key)
    report={
       "schema_version":1,
       "expected_tei_sha256":digest(expected_path),
       "native_imp_sha256":digest(native_path),
       "expected_keys":len(expected),
       "native_keys":len(native),
       "missing_keys":missing[:50],"missing_key_count":len(missing),
       "unexpected_keys":unexpected[:50],"unexpected_key_count":len(unexpected),
       "malformed_readback":parse_failures[:50],"malformed_count":len(parse_failures),
       "unicode_text_mismatches":text_mismatch[:50],
       "unicode_text_mismatch_count":len(text_mismatch),
       "xml_structure_mismatches":markup_mismatch[:50],
       "xml_structure_mismatch_count":len(markup_mismatch),
       "native_roundtrip_verified":not (
          missing or unexpected or parse_failures or text_mismatch or markup_mismatch),
       "reader_ui_verified":False,
       "rights_cleared":False,
       "publication_permitted":False
    }
    dest=Path(report_path)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-tei",required=True)
    p.add_argument("--native-imp",required=True)
    p.add_argument("--report",required=True)
    args=p.parse_args()
    report=analyze(args.input_tei,args.native_imp,args.report)
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if not report["native_roundtrip_verified"]:
        sys.exit(1)

if __name__=="__main__":
    main()
