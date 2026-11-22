#!/usr/bin/env python3
"""Audit unresolved ISBE links in their containing articles.

The result is a contextual diagnostic, never a source-text correction.
"""
import argparse
from collections import Counter
import json
import unicodedata
from pathlib import Path
import xml.etree.ElementTree as ET

TEI = "http://www.tei-c.org/ns/1.0"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
ENTRY = f"{{{TEI}}}div"
REF = f"{{{TEI}}}ref"


def normalized(s):
    return " ".join(s.split()).strip().casefold()


def folded_letters(text):
    """Search candidate keys ignoring ONLY separators; never auto-approve."""
    text = unicodedata.normalize("NFKC", text).casefold()
    return "".join(c for c in text if c.isalnum())


def classify_candidate(target, visible, known_keys):
    visible_key = normalized(visible)
    matches = known_keys.get(visible_key, [])
    if len(matches) != 1:
        return None
    if normalized(target) == visible_key:
        return None
    return matches[0]


def scan(path):
    root = ET.parse(path).getroot()
    entries = root.findall(f".//{ENTRY}[@type='entry']")
    known = {}
    for a in entries:
        k = a.get("n")
        known.setdefault(normalized(k), []).append(k)
    lexical_index = {}
    for a in entries:
        key = a.get("n")
        lexical_index.setdefault(folded_letters(key), []).append(key)
    records = []
    sections = []
    structure_examples = []
    summary = Counter()
    for article in entries:
        article_key = article.get("n")
        if article_key in ("EDUCATION", "EGYPT", "EBIONISM; EBIONITES", "ANTHROPOMORPHISM"):
            paragraphs = [p for p in article.iter() if p.tag.split("}")[-1] == "p"]
            structure_examples.append({
                "article": article_key,
                "paragraphs": len(paragraphs),
                "paragraph_previews": [
                    {"text": " ".join("".join(p.itertext()).split())[:180],
                     "children": [x.tag.split("}")[-1] for x in list(p)[:7]]}
                    for p in paragraphs[:18]
                ],
            })
        parents = {c: p for p in article.iter() for c in p}
        marked_headings = []
        for candidate in article.iter():
            if candidate.tag.split("}")[-1] not in ("hi", "head"):
                continue
            if candidate.tag.split("}")[-1] == "hi" and candidate.get("rend") != "underline":
                continue
            txt = " ".join("".join(candidate.itertext()).split())
            if txt:
                marked_headings.append({"id": candidate.get(XMLID), "text": txt[:180],
                                        "parent_tag": parents[candidate].tag.split("}")[-1] if candidate in parents else ""})
        for ref in article.iter(REF):
            destination = ref.get("target", "")
            if not destination.startswith("ISBE:"):
                continue
            target = destination[5:]
            visible = "".join(ref.itertext()).strip()
            candidate = classify_candidate(target, visible, known)
            parent = parents.get(ref)
            while parent is not None and parent.tag.split("}")[-1] not in ("p", "item", "ab"):
                parent = parents.get(parent)
            container_text = "".join(parent.itertext()) if parent is not None else ""
            snippet = " ".join(container_text.split())[:450]
            target_matches = lexical_index.get(folded_letters(target), [])
            if candidate:
                kind = "visible_exact_index_candidate"
            elif len(target_matches) == 1:
                kind = "unique_separator_variant_candidate"
            elif len(target_matches) > 1:
                kind = "ambiguous_separator_variant"
            else:
                kind = "requires_review"
            summary[kind] += 1
            is_section_reference = (
                target.strip().casefold().rstrip(".") == "literature"
                or target.lstrip().startswith(tuple(str(i) + "." for i in range(1, 31)))
                or (len(target) > 2 and target[0] in "IVX" and "." in target[:7])
            )
            if is_section_reference:
                needles = normalized(target).strip(".").replace("literature.", "literature")
                possible = [h for h in marked_headings
                            if needles in normalized(h["text"]).strip(".:")]
                sections.append({"source_article": article_key, "target": target,
                                 "visible": visible, "possible_local_headings": possible[:8],
                                 "marked_heading_count": len(marked_headings)})
            records.append({
                "article_key": article_key,
                "ref_id": ref.get(XMLID),
                "original_target": target,
                "displayed_text": visible,
                "candidate_key": candidate,
                "lexical_candidates": target_matches[:20],
                "kind": kind,
                "context": snippet,
            })
    return {"schema_version": 1,
            "status": "review_diagnostics_not_approved_mappings",
            "total_unresolved_occurrences": len(records),
            "category_counts": dict(sorted(summary.items())),
            "article_structure_examples": structure_examples,
            "section_review_samples": sections[:120],
            "section_occurrences_in_review": len(sections),
            "unique_separator_candidates": [
                {"article_key": x["article_key"], "original_target": x["original_target"],
                 "candidate": x["lexical_candidates"][0], "context": x["context"][:170]}
                for x in records if x["kind"] == "unique_separator_variant_candidate"
            ],
            "occurrences": records}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    report = scan(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "occurrences"}, indent=2))


if __name__ == "__main__":
    main()
