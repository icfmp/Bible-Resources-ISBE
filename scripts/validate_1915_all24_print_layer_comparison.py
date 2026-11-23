#!/usr/bin/env python3
"""Reproduce whole-original-page-PDF-text-layer measurements for all 24 cases.

This proves only that the source-locked PDF OCR layer has been compared over
every physical article region. It does NOT prove correctness of Hebrew,
Greek, Arabic, punctuation, or all printed characters on the scan image.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

LOCK = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
T = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def words(s):
    norm = unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()
    return re.findall(r"[a-z0-9]+",norm)

def grams(s):
    return Counter(zip(s,s[1:],s[2:],s[3:]))

def region_text(pdf_page_text, segments):
    pages=pdf_page_text.split("--- ORIGINAL 1915 PDF PAGE TRANSITION ---")
    combined=[]
    for seg in segments:
        page=seg["page_offset"]
        if not isinstance(page,int) or not 0<=page<len(pages):
            raise ValueError("Original printed continuation page missing")
        lines=pages[page].splitlines()
        a,b=seg["line_first_0_based"],seg["line_last_0_based"]
        split=seg["text_layer_split_column"]
        if not (isinstance(a,int) and isinstance(b,int) and isinstance(split,int)
                and 0<=a<=b<len(lines) and 40<=split<=100):
            raise ValueError("Unsupported physical original-print page segmentation")
        if seg["column"] not in ("left","right"):
            raise ValueError("Unknown original printed text column")
        for ln in lines[a:b+1]:
            side=ln[:split] if seg["column"]=="left" else ln[split:]
            if side.strip():
                combined.append(side.strip())
    return " ".join(combined)

def validate(data,source,witness,visual,output_dir,volume):
    if (data.get("schema_version")!=1 or data.get("canonical_tei_sha256")!=LOCK
            or data.get("publication_permitted") is not False
            or data.get("canonical_source_modified") is not False
            or data.get("full_original_print_glyph_collations_certified")!=0
            or data.get("checked_articles")!=24
            or data.get("whole_digital_article_matched_to_print_text_layer_regions")!=24):
        raise ValueError("Unsupported research or editorial certification")
    if (witness.get("canonical_tei_sha256")!=LOCK or visual.get("canonical_tei_sha256")!=LOCK
            or visual.get("english_prose_read_through_count")!=24):
        raise ValueError("Canonical original/visual witness identity drift")
    vols={row["volume"]:row for row in witness["volumes"]}
    if len(vols)!=5 or volume not in vols:
        raise ValueError("Unknown original historical volume")
    base={r["source_key"]:r for r in visual["entries"]}
    all_rows=data.get("articles")
    if not isinstance(all_rows,list) or len(all_rows)!=24 or len(base)!=24:
        raise ValueError("Must retain original 24 suspect article set")
    if len({row.get("source_key") for row in all_rows})!=24:
        raise ValueError("Duplicate original article case")
    for row in all_rows:
        original=base.get(row.get("source_key"))
        if original is None or row.get("original_volume")!=original["volume"]:
            raise ValueError("Unknown original English/source article")
        for key,old in (("article_xml_id","source_article_xml_id"),
                        ("original_pdf_start_page","pdf_page"),
                        ("original_pdf_sha256","pdf_sha256"),
                        ("original_page_jpeg_sha256","page_image_sha256"),
                        ("canonical_article_visible_text_sha256",
                         "canonical_visible_text_sha256")):
            if row.get(key)!=original.get(old):
                raise ValueError("Historical source article/page SHA metadata drift")
        if (row["original_pdf_sha256"]!=vols[row["original_volume"]]["pdf_sha256"]
                or row.get("whole_article_digital_to_print_pdf_text_layer_compared") is not True
                or row.get("original_print_glyph_level_certified") is not False
                or row.get("original_pdf_text_layer_is_ground_truth") is not False):
            raise ValueError("False historical source or article-completion status")
    body=source.find(f"./{T}text/{T}body")
    if body is None or len(body)!=9380:
        raise ValueError("Canonical TEI source article inventory changed")
    articles={a.get("n"):a for a in body}
    results=[]
    for row in all_rows:
        if row["original_volume"]!=volume:
            continue
        key=row["source_key"]
        article=articles.get(key)
        if article is None or row["article_xml_id"]!=article.get(ID):
            raise ValueError("Canonical original XML ID drift")
        original="".join(article.itertext())
        if sha256(original.encode("utf-8")).hexdigest()!=row["canonical_article_visible_text_sha256"]:
            raise ValueError("Original full article text drift")
        filename=Path(output_dir)/f"{volume}-{key}.txt"
        text=region_text(filename.read_text(encoding="utf-8"),row["physical_segments"])
        if not text.lower().startswith(key.lower()):
            raise ValueError("Wrong original printed article physical region")
        if sha256(text.encode("utf-8")).hexdigest()!=row["pdf_text_layer_region_sha256"]:
            raise ValueError("Research layer content changed: check original 1915 print")
        a,b=words(original),words(text)
        if (len(a)!=row["digital_latin_token_count"]
                or len(b)!=row["print_pdf_text_layer_latin_token_count"]
                or round(len(b)/len(a),4)!=row["print_layer_to_digital_token_ratio"]
                or round(sum((grams(a)&grams(b)).values())/max(1,len(a)-3),4)!=row["source_fourgram_recall"]):
            raise ValueError("Whole original 1915 source/OCR article comparison changed")
        if not 0.8<=len(b)/len(a)<=1.2:
            raise ValueError("Incomplete original printed article extraction")
        results.append(key)
    return {"volume":volume,"whole_original_print_page_text_layer_articles_checked":results,
            "article_count":len(results),
            "original_print_glyph_level_certified":False,
            "publication_permitted":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--volume",required=True)
    p.add_argument("--original-text-directory",required=True,type=Path)
    p.add_argument("--canonical",default="cleaned/en/ISBE.xml",type=Path)
    p.add_argument("--report",default="workspace/reviews/1915-all24-print-layer-whole-article-comparison-v1.json",type=Path)
    p.add_argument("--visual",default="workspace/reviews/1915-article-wide-prose-review-v2.json",type=Path)
    p.add_argument("--manifest",default="sources/print/1915-volume-witnesses.json",type=Path)
    args=p.parse_args()
    if sha256(args.canonical.read_bytes()).hexdigest()!=LOCK:
        raise ValueError("Canonical source ZIP/IMP/TEI drift")
    output=validate(load(args.report),ET.parse(args.canonical).getroot(),
                    load(args.manifest),load(args.visual),
                    args.original_text_directory,args.volume)
    print(json.dumps(output,indent=2))
if __name__=="__main__":
    main()
