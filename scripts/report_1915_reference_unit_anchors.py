#!/usr/bin/env python3
"""Extract exact immutable TEI parent/ref anchors for 1915 review candidates."""
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.audit_scripture_ref_display import scan

TEI="{http://www.tei-c.org/ns/1.0}"
ID="{http://www.w3.org/XML/1998/namespace}id"
LOCK="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"

def anchors(path):
    audit=scan(path)
    if audit["input_sha256"]!=LOCK or audit["candidate_count"]!=13:
        raise ValueError("Canonical TEI or exact reference candidate population drift")
    root=ET.parse(path).getroot()
    parent={child:node for node in root.iter() for child in node}
    nodes={node.get(ID):node for node in root.iter() if node.get(ID)}
    rows=[]
    for c in audit["cases"]:
        node=nodes[c["ref_xml_id"]]
        par=parent.get(node)
        if par is None or par.tag!=TEI+"p" or not par.get(ID):
            raise ValueError("Reference does not have expected direct p parent")
        full="".join(par.itertext())
        rows.append({**c,"source_unit_xml_id":par.get(ID),
                     "source_unit_text_sha256":sha256(full.encode()).hexdigest(),
                     "source_ref_text":node.text,"source_ref_tail":node.tail,
                     "ref_type":node.get("type"),
                     "source_unit_text":full})
    return rows

def main():
    rows=anchors(Path("cleaned/en/ISBE.xml"))
    Path("workspace/tmp").mkdir(parents=True,exist_ok=True)
    Path("workspace/tmp/1915-scripture-ref-anchors.json").write_text(
        json.dumps({"canonical_sha256":LOCK,"cases":rows},ensure_ascii=False,indent=2)+"\n"
    )
    for row in rows:
        print("SOURCE_ANCHOR",json.dumps({
            k:row[k] for k in ("article_key","ref_xml_id","source_unit_xml_id",
                              "source_ref_text","source_ref_tail","ref_type")
        },ensure_ascii=False))
if __name__=="__main__":
    main()
