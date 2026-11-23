"""Fail-closed decisions for 24 original-1915 source-vs-print fidelity failures.

This is a full decision (pass/fail) on exact historic reproduction, NOT an
exhaustive glyph-level transcription or authorization for automatic edits.
"""
import json
from pathlib import Path
import re

LOCK="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
HEX=re.compile(r"[a-f0-9]{64}\Z")

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate(decisions,prior_visual,print_layer):
    for datum in (decisions,prior_visual,print_layer):
        if datum.get("canonical_tei_sha256")!=LOCK:
            raise ValueError("Canonical 1915 source identity changed")
        if datum.get("publication_permitted") is not False:
            raise ValueError("Historical printed source research is not a publication licence")
    if (decisions.get("schema_version")!=1
            or decisions.get("print_identical_fidelity_approved")!=0
            or decisions.get("print_identical_fidelity_rejected")!=24
            or decisions.get("full_original_1915_print_word_for_word_collation_certified")!=0
            or decisions.get("original_crosswire_unchanged") is not True
            or decisions.get("all_24_original_english_prose_read_through") is not True
            or decisions.get("all_24_full_source_to_original_pdf_text_layer_compared") is not True
            or prior_visual.get("english_prose_read_through_count")!=24
            or print_layer.get("checked_articles")!=24):
        raise ValueError("Unjustified acceptance/release or incomplete original review")
    refs=prior_visual.get("entries")
    readings=print_layer.get("articles")
    cases=decisions.get("decisions")
    if not all(isinstance(x,list) and len(x)==24 for x in (refs,readings,cases)):
        raise ValueError("Original 24 article source population must remain")
    original={x["source_key"]:x for x in refs}
    textlayer={x["source_key"]:x for x in readings}
    if (len(original)!=24 or len(textlayer)!=24 or
            len({x.get("source_key") for x in cases})!=24 or
            set(original)!=set(textlayer) or set(original)!={x.get("source_key") for x in cases}):
        raise ValueError("Missing or repeated article in original-print collation")
    for row in cases:
        key=row["source_key"]
        source=original[key]
        printx=textlayer[key]
        field_pairs=(
            ("source_article_xml_id","source_article_xml_id"),
            ("original_pdf_volume","volume"),
            ("original_pdf_page","pdf_page"),
            ("original_pdf_sha256","pdf_sha256"),
            ("original_page_jpeg_sha256","page_image_sha256"),
            ("complete_digital_article_sha256","canonical_visible_text_sha256"),
        )
        for new,prior in field_pairs:
            if row.get(new)!=source.get(prior):
                raise ValueError("Wrong exact original print/source article identity")
        if (source.get("original_nonlatin_script_visible_in_print") is not True
                or source.get("digitized_source_nonlatin_script_characters")!=0
                or row.get("original_print_nonlatin_glyphs_attested") is not True
                or row.get("digital_visible_original_script_glyph_count")!=0
                or row.get("complete_source_pdf_text_layer_sha256")!=printx.get("pdf_text_layer_region_sha256")
                or row.get("print_identical_fidelity") is not False
                or row.get("audit_decision")!="REJECT_AS_EXACT_1915_PRINT_REPRODUCTION"
                or row.get("automatic_text_change_authorized") is not False
                or row.get("further_original_script_punctuation_reference_collation_needed_to_reconstruct") is not True
                or row.get("scope")!="decisive_source_print_difference_not_exhaustive_transcription"):
            raise ValueError("False full printed transcription, unverified gap, or unauthorized edit")
        for key_name in ("original_page_jpeg_sha256","complete_digital_article_sha256",
                         "complete_source_pdf_text_layer_sha256"):
            if not isinstance(row.get(key_name),str) or not HEX.fullmatch(row[key_name]):
                raise ValueError("Invalid printed source/page fingerprint")
    return {"original_print_fidelity_rejected":24,"original_print_fidelity_approved":0,
            "entire_original_print_glyph_collations_completed":0,
            "canonical_source_unchanged":True,"publication_permitted":False}
