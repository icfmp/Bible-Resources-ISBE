#!/usr/bin/env python3
"""Select source-attested multilingual and nested-structure GUI sample keys.

This does not certify reader glyph rendering, historical 1915 print fidelity,
or language restoration. It inventories codepoints found in the *locked
corrected digital TEI source*, checks the same characters and nested TEI
structure survive the SWORD importer, and suggests observable GUI fixtures.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

N="{http://www.tei-c.org/ns/1.0}"

def sha(path):
    h=sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda:file.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def classified(char):
    n=ord(char)
    if 0x0370<=n<=0x03FF or 0x1F00<=n<=0x1FFF:
        return "greek"
    if 0x0590<=n<=0x05FF or 0xFB1D<=n<=0xFB4F:
        return "hebrew"
    return None

def entries(path, tag):
    body=ET.parse(path).getroot().find("./"+N+"text/"+N+"body")
    if body is None:
        raise ValueError("Missing TEI body")
    data={}
    for article in body:
        key=article.get("n")
        if article.tag!=N+tag or not key or key in data:
            raise ValueError("Missing, duplicate or invalid source dictionary key")
        data[key]=article
    return data

def analyse(source, adapted, report_path, sample_size=12):
    originals=entries(source,"div")
    imports=entries(adapted,"entryFree")
    if originals.keys()!=imports.keys():
        raise ValueError("Different dictionary entry keys")
    rows={"greek":[],"hebrew":[],"nested":[]}
    count={"greek":0,"hebrew":0,"nested":0}
    for key,item in originals.items():
        other=imports[key]
        a="".join(item.itertext())
        b="".join(other.itertext())
        if a!=b:
            raise ValueError("Source script/text changed for "+key)
        a_nested=sum(1 for n in item.iter(N+"div") if n is not item)
        b_nested=sum(1 for n in other.iter(N+"div"))
        if a_nested!=b_nested:
            raise ValueError("Nested divisions changed for "+key)
        if a_nested:
            count["nested"]+=1
            rows["nested"].append({
                "key":key,"nested_divisions":a_nested,
                "text_length":len(a),
            })
        for script in ("greek","hebrew"):
            offsets=[i for i,c in enumerate(a) if classified(c)==script]
            if offsets:
                count[script]+=1
                # The original unicode is in the source itself. Include
                # codepoints instead of copying historical article passages.
                distinct=list(dict.fromkeys(f"U+{ord(a[i]):04X}" for i in offsets))
                rows[script].append({
                    "key":key,
                    "first_character_offset":offsets[0],
                    "script_codepoint_count":len(offsets),
                    "codepoints_first_twelve":distinct[:12],
                    "appears_near_top_700_chars":offsets[0]<700
                })
    # Prioritize entries where the script is visible without scrolling.
    recommended={}
    for script in ("greek","hebrew"):
        sorted_rows=sorted(rows[script],key=lambda x:(
            not x["appears_near_top_700_chars"],
            x["first_character_offset"],-x["script_codepoint_count"],x["key"]))
        recommended[script]=sorted_rows[:sample_size]
    recommended["nested"]=sorted(rows["nested"],key=lambda x:(
        -x["nested_divisions"],x["key"]))[:sample_size]
    report={
        "schema_version":1,
        "source_sha256":sha(source),
        "import_sha256":sha(adapted),
        "source_article_count":len(originals),
        "greek_character_article_count":count["greek"],
        "hebrew_character_article_count":count["hebrew"],
        "nested_division_article_count":count["nested"],
        "nested_division_count":sum(x["nested_divisions"] for x in rows["nested"]),
        "gui_candidate_samples":recommended,
        "unicode_and_nested_structure_preserved_by_importer":True,
        "actual_gui_greek_rendering_verified":False,
        "actual_gui_hebrew_rendering_verified":False,
        "actual_gui_nested_section_rendering_verified":False,
        "historical_print_language_verified":False,
        "rights_cleared":False,"published":False
    }
    path=Path(report_path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True)
    p.add_argument("--adapted",required=True)
    p.add_argument("--report",required=True)
    p.add_argument("--sample-size",type=int,default=12)
    a=p.parse_args()
    if a.sample_size<1 or a.sample_size>50:
        raise SystemExit("sample-size must be between 1 and 50")
    print(json.dumps(analyse(a.source,a.adapted,a.report,a.sample_size),
                     ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
