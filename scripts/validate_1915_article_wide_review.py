#!/usr/bin/env python3
"""Validate source-locked 1915 article-wide image-review evidence.

This only checks digital source identities and historical page provenance.
It cannot read a printed image in CI or certify a scholarly collation.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

T = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"
LOCK = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
HEX = re.compile(r"[0-9a-f]{64}\Z")
NONLATIN = re.compile(r"[\u0370-\u03ff\u0590-\u06ff]")

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate(spec, manifest, root):
    if spec.get("schema_version") != 1 or spec.get("canonical_tei_sha256") != LOCK:
        raise ValueError("Wrong original digital source")
    if manifest.get("canonical_tei_sha256") != LOCK:
        raise ValueError("Historical scan manifest drift")
    for flag in ("full_historical_collation_certified", "publication_permitted",
                 "canonical_source_modified", "editorial_changes_approved"):
        if spec.get(flag) is not False:
            raise ValueError("Unjustified editing, scholarly or release approval")
    volumes = {v["volume"]: v for v in manifest.get("volumes", [])}
    if len(volumes) != 5:
        raise ValueError("Need all five original 1915 printed volumes")
    body = root.find(f"./{T}text/{T}body")
    if body is None:
        raise ValueError("No TEI body")
    articles = {a.get("n"): a for a in body}
    if len(articles) != 9380:
        raise ValueError("Digital article population changed")
    rows = spec.get("entries")
    if not isinstance(rows, list) or len(rows) != 24:
        raise ValueError("Unexpected research candidate population")
    seen = set()
    reviewed = one_page = continuation = 0
    for row in rows:
        key = row.get("source_key")
        if key not in articles or key in seen:
            raise ValueError("Unknown or duplicate source article")
        seen.add(key)
        article = articles[key]
        if row.get("source_article_xml_id") != article.get(ID):
            raise ValueError("Original article XML identity changed")
        prose = "".join(article.itertext())
        if (row.get("canonical_visible_text_sha256") != hashlib.sha256(
                prose.encode("utf-8")).hexdigest()
                or row.get("canonical_visible_text_characters") != len(prose)):
            raise ValueError("Original article visible text changed")
        if row.get("digitized_source_nonlatin_script_characters") != len(NONLATIN.findall(prose)):
            raise ValueError("False digital script inventory")
        vol = volumes.get(row.get("volume"))
        page = row.get("pdf_page")
        if (not vol or row.get("pdf_sha256") != vol["pdf_sha256"]
                or not isinstance(page, int) or page < 1 or page > vol["pages"]):
            raise ValueError("Wrong original printed volume or page")
        digest = row.get("page_image_sha256")
        if not isinstance(digest, str) or not HEX.fullmatch(digest):
            raise ValueError("Invalid page JPEG digest")
        for flag in ("original_script_punctuation_and_markup_verified",
                     "full_word_for_word_print_collation_certified"):
            if row.get(flag) is not False:
                raise ValueError("Full historic print certification is not earned")
        if row.get("original_nonlatin_script_visible_in_print") is not True:
            raise ValueError("The image review scope was changed")
        english = row.get("english_prose_linewise_comparison_completed")
        whole = row.get("source_text_read_through_entire_article")
        if not isinstance(english, bool) or english != whole:
            raise ValueError("Incorrect English-prose review state")
        if whole:
            reviewed += 1
            if (not row.get("review_note") or
                    row.get("evidence_scope") != "whole_article_english_prose_pass"):
                raise ValueError("Missing bounded visual review note")
        elif row.get("evidence_scope") != "earlier_start_page_spotcheck_only":
            raise ValueError("Spot-check incorrectly promoted to article-wide")
        same_page = row.get("printed_article_end_observed_on_same_page")
        pending = row.get("pending_continuation_pdf_pages")
        visited = row.get("verified_continuation_pages", [])
        if (not isinstance(same_page, bool) or not isinstance(pending, list)
                or not isinstance(visited, list) or len(pending) + len(visited) > 3
                or any(not isinstance(p, int) or p <= page or
                       p > vol["pages"] for p in pending)):
            raise ValueError("Bad continuation metadata")
        visited_numbers = []
        for v in visited:
            if not isinstance(v, dict):
                raise ValueError("Malformed original continuation image")
            p, img = v.get("pdf_page"), v.get("image_sha256")
            if (not isinstance(p, int) or not page < p <= vol["pages"]
                    or not isinstance(img, str) or not HEX.fullmatch(img)
                    or not isinstance(v.get("research_run"), str)
                    or not v["research_run"].startswith("https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/")):
                raise ValueError("Unattested original printed continuation")
            visited_numbers.append(p)
        if (len(visited_numbers) != len(set(visited_numbers)) or
                set(visited_numbers) & set(pending)):
            raise ValueError("Duplicate printed continuation-page claim")
        if same_page:
            one_page += 1
            if pending or visited:
                raise ValueError("False continuation")
        else:
            continuation += 1
            if not pending and not visited or whole and pending:
                raise ValueError("Incomplete physical continuation is not a full English-prose review")
        phrases = set()
        for obs in row.get("observations", []):
            exact = obs.get("digital_exact")
            if (not isinstance(exact,str) or len(exact)<5 or
                    prose.count(exact) != 1 or exact in phrases or
                    not obs.get("print_excerpt") or not obs.get("classification")):
                raise ValueError("Unfounded exact digital/print excerpt")
            phrases.add(exact)
        if not isinstance(row.get("remaining_work"),list) or len(row["remaining_work"])<2:
            raise ValueError("Unfinished visual review must remain explicit")
    if (reviewed, one_page, continuation) != (12,23,1):
        raise ValueError("Review coverage changed without a new evidence version")
    return {"candidates":len(rows),"article_body_one_original_page":one_page,
            "english_prose_reviewed":reviewed,"articles_with_printed_continuation":continuation,\n            "unexamined_continuation_pages":sum(len(r.get("pending_continuation_pdf_pages", [])) for r in rows),
            "full_print_collations_certified":0}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger",type=Path,default=Path(
        "workspace/reviews/1915-article-wide-prose-review-v1.json"))
    p.add_argument("--canonical",type=Path,default=Path("cleaned/en/ISBE.xml"))
    p.add_argument("--manifest",type=Path,default=Path("sources/print/1915-volume-witnesses.json"))
    a=p.parse_args()
    if hashlib.sha256(a.canonical.read_bytes()).hexdigest()!=LOCK:
        raise ValueError("Canonical TEI SHA-256 mismatch")
    print(json.dumps(validate(load(a.ledger),load(a.manifest),
                              ET.parse(a.canonical).getroot()),indent=2))

if __name__ == "__main__":
    main()
