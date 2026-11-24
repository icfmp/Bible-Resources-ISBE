#!/usr/bin/env python3
"""Validate an *actual* libSWORD TEIHTMLHREF dictionary hyperlink destination.

Selects a source-audited cross-article reference, renders that source
article through installed diatheke -f HTMLHREF, and requires an actual
sword://<configured-module>/<original-key> link. No text or TEI edits.
"""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit

class HrefReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            attributes=dict(attrs)
            if "href" in attributes:
                self.hrefs.append(attributes["href"])

def links(html):
    p=HrefReader()
    p.feed(html)
    return p.hrefs

def matches_sword_key(href,module_id,key):
    parsed=urlsplit(href)
    return (parsed.scheme.lower()=="sword"
            and parsed.netloc==module_id
            and unquote(parsed.path.lstrip("/"))==key
            and not parsed.query and not parsed.fragment)

def verify(sample,module_id,rendered_html):
    if not sample or not module_id:
        raise ValueError("Missing original audited source link or module identity")
    src,dest=sample["source_article"],sample["destination_article"]
    hrefs=links(rendered_html)
    good=[href for href in hrefs if matches_sword_key(href,module_id,dest)]
    if not good:
        raise ValueError(
            f"Native SWORD renderer cannot navigate {src} to {dest} "
            f"under the actual module {module_id}: {hrefs[:8]!r}"
        )
    if any(urlsplit(href).netloc=="self" for href in hrefs):
        raise ValueError("Native renderer still emitted invalid sword://self work URLs")
    return {
        "source_article":src,
        "destination_article":dest,
        "original_target":sample["original_xml_target"],
        "audited_compiled_target":sample["native_link_target"],
        "sword_module_id":module_id,
        "expected_work_prefixed_tei_target":module_id+":"+dest,
        "native_sword_href":good[0],
        "rendered_anchors_total":len(hrefs),
        "native_sword_dictionary_link_resolves_to_expected_module":True,
        "gui_reader_click_verified":False
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples",required=True)
    parser.add_argument("--module-id",required=True)
    parser.add_argument("--report",required=True)
    args=parser.parse_args()
    sample_report=json.loads(Path(args.samples).read_text(encoding="utf-8"))
    if sample_report.get("sword_module_id")!=args.module_id:
        raise SystemExit("Native sample inventory module ID mismatch")
    candidates=sample_report.get("chosen_samples",[])
    if not candidates:
        raise SystemExit("No source-verified dictionary link selected")
    sample=candidates[0]
    if sample.get("native_link_target")!=args.module_id+":"+sample["destination_article"]:
        raise SystemExit("Native sampled target is not the configured dictionary module")
    rendered=subprocess.run(["diatheke","-b",args.module_id,"-f","HTMLHREF",
                             "-k",sample["source_article"]],
                            check=True,capture_output=True,text=True).stdout
    result=verify(sample,args.module_id,rendered)
    report={
      "schema_version":1,
      "scope":"SWORD_HTMLHREF_actual_rendered_work_key—not_GUI_navigation",
      "native_readback_checked":True,
      "source_sample_report":args.samples,
      "sample_result":result,
      "original_source_modified":False,
    }
    path=Path(args.report)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
