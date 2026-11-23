#!/usr/bin/env python3
"""Audit cumulative 1915 printed-image English-prose read-throughs without claiming exact print certification.

v1 remains immutable. v2 records the 12 additional full-English passes only;
the original CrossWire TEI, print-page witnesses and all v1 assertions are
source-locked. No image OCR, print-text repair or publication occurs here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from scripts.validate_1915_article_wide_review import (
    LOCK, load, validate as validate_v1, T
)

DEFAULT_V1 = Path("workspace/reviews/1915-article-wide-prose-review-v1.json")
DEFAULT_V2 = Path("workspace/reviews/1915-article-wide-prose-review-v2.json")
DEFAULT_MANIFEST = Path("sources/print/1915-volume-witnesses.json")
DEFAULT_CANONICAL = Path("cleaned/en/ISBE.xml")

def git_blob_sha1(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()

def validate_extension(previous, current, source_root, manifest, previous_bytes):
    baseline = validate_v1(previous, manifest, source_root)
    if baseline["english_prose_reviewed"] != 12:
        raise ValueError("An unexpected previously reviewed article inventory")
    if (current.get("schema_version") != 2
            or current.get("canonical_tei_sha256") != LOCK
            or current.get("previous_review_path") != str(DEFAULT_V1)
            or current.get("previous_review_git_blob_sha1") != git_blob_sha1(previous_bytes)
            or current.get("english_prose_read_through_count") != 24):
        raise ValueError("Original source or prior review chain changed")
    for flag in ("full_historical_collation_certified", "publication_permitted",
                 "canonical_source_modified", "editorial_changes_approved"):
        if current.get(flag) is not False:
            raise ValueError("No source change, complete print collation or publication approved")
    for stable in ("source_images_research_run", "source_images_continuation_run"):
        if current.get(stable) != previous.get(stable):
            raise ValueError("Historical page-image research provenance was rewritten")
    old = previous.get("entries")
    new = current.get("entries")
    if not isinstance(new, list) or len(new) != 24 or not isinstance(old, list) or len(old) != 24:
        raise ValueError("All original 24 cases must be preserved")
    bykey = {row["source_key"]: row for row in old}
    if len(bykey) != 24 or [row["source_key"] for row in new] != [row["source_key"] for row in old]:
        raise ValueError("Original source case order or identity changed")
    body = source_root.find(f"./{T}text/{T}body")
    articles = {a.get("n"):a for a in body}
    allowed_updates = {"english_prose_linewise_comparison_completed",
                       "source_text_read_through_entire_article", "evidence_scope",
                       "review_note", "remaining_work", "new_article_wide_findings"}
    newly_reviewed = 0
    snippet_count = 0
    for item in new:
        prior = bykey[item["source_key"]]
        for field, value in prior.items():
            if field not in allowed_updates and item.get(field) != value:
                raise ValueError("Prior source text, page image or status was altered")
        extra = set(item) - set(prior) - allowed_updates
        if extra:
            raise ValueError("Unreviewed extra fields inserted")
        if prior["english_prose_linewise_comparison_completed"]:
            if item != prior:
                raise ValueError("Previous completed pass must remain immutable")
            continue
        if (item.get("english_prose_linewise_comparison_completed") is not True
                or item.get("source_text_read_through_entire_article") is not True
                or item.get("evidence_scope") != "whole_article_english_prose_pass"
                or not isinstance(item.get("review_note"),str)
                or len(item["review_note"]) < 100
                or not isinstance(item.get("remaining_work"),list)
                or len(item["remaining_work"]) < 2):
            raise ValueError("New completed English-prose visual review is incomplete")
        if item.get("full_word_for_word_print_collation_certified") is not False or item.get("original_script_punctuation_and_markup_verified") is not False:
            raise ValueError("English review cannot become whole historical print certification")
        findings = item.get("new_article_wide_findings",[])
        if not isinstance(findings,list) or len(findings)>6:
            raise ValueError("Evidence finding list exceeds a bounded review")
        prose = "".join(articles[item["source_key"]].itertext())
        seen = set()
        for finding in findings:
            exact = finding.get("digital_exact")
            printed = finding.get("print_reading")
            kind = finding.get("kind")
            if (not isinstance(exact,str) or len(exact)<8 or prose.count(exact)!=1
                    or exact in seen or not isinstance(printed,str) or len(printed)<5
                    or not isinstance(kind,str) or len(kind)<8
                    or finding.get("text_correction_approved") is not False):
                raise ValueError("Invented or silently approved digital/print reading")
            seen.add(exact)
            snippet_count += 1
        newly_reviewed += 1
    if newly_reviewed != 12 or snippet_count != 5:
        raise ValueError("Unexpected unreviewed English-prose completions or print snippets")
    return {
        "canonical_articles":len(articles),
        "review_candidates":len(new),
        "previously_reviewed_english":12,
        "newly_reviewed_english":newly_reviewed,
        "reviewed_english_total":24,
        "new_excerpt_observations":snippet_count,
        "complete_original_script_punctuation_reference_collations":0,
        "publication_permitted":False,
        "source_unchanged":True,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--previous",type=Path,default=DEFAULT_V1)
    p.add_argument("--current",type=Path,default=DEFAULT_V2)
    p.add_argument("--manifest",type=Path,default=DEFAULT_MANIFEST)
    p.add_argument("--canonical",type=Path,default=DEFAULT_CANONICAL)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    canonical=a.canonical.read_bytes()
    if hashlib.sha256(canonical).hexdigest()!=LOCK:
        raise ValueError("Canonical source SHA-256 has drifted")
    out=validate_extension(load(a.previous),load(a.current),
                           ET.fromstring(canonical),load(a.manifest),
                           a.previous.read_bytes())
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
