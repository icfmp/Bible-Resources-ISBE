#!/usr/bin/env python3
"""Audit unresolved ISBE links in their containing articles.

The result is a contextual diagnostic, never a source-text correction.
"""
import argparse
from collections import Counter
import json
import unicodedata
import re
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


def numbered_markers(article, reference):
    """Show candidate subsection markers for a reference such as NAME (2)."""
    base, separator, suffix = reference.strip().rpartition(" (")
    if not separator or not suffix.endswith(")") or not suffix[:-1].isdigit():
        return []
    needle = "(" + suffix[:-1] + ")"
    evidence = []
    for node in article.iter():
        if node.tag.split("}")[-1] != "p":
            continue
        label = " ".join("".join(node.itertext()).split())
        offset = label.find(needle)
        if offset >= 0:
            evidence.append({
                "paragraph_id": node.get(XMLID),
                "starts_with_marker": label.startswith(needle),
                "offset": offset,
                "excerpt": label[max(0, offset - 60):offset + 230]
            })
    return evidence[:12]


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
    aliases = {}
    for a in entries:
        key = a.get("n")
        for component in key.split(";"):
            component = component.strip()
            if component:
                aliases.setdefault(normalized(component), set()).add(key)
    article_by_key = {a.get("n"): a for a in entries}
    numbered_candidates = {}
    for key in (a.get("n") for a in entries):
        stem = re.sub(r"\s+\(\d+\)$", "", key).strip().casefold()
        numbered_candidates.setdefault(stem, set()).add(key)
    records = []
    summary = Counter()
    for article in entries:
        article_key = article.get("n")
        parents = {c: p for p in article.iter() for c in p}
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
            alias_matches = sorted(aliases.get(normalized(target), ()))
            stripped_target = re.sub(r"\s+\(\d+\)$", "", target).strip().casefold()
            numbered_matches = sorted(numbered_candidates.get(stripped_target, ()))
            target_matches = lexical_index.get(folded_letters(target), [])
            if len(alias_matches) == 1:
                kind = "unique_semicolon_alias_candidate"
            elif len(alias_matches) > 1:
                kind = "ambiguous_semicolon_alias"
            elif candidate:
                kind = "visible_exact_index_candidate"
            elif len(target_matches) == 1:
                kind = "unique_separator_variant_candidate"
            elif len(target_matches) > 1:
                kind = "ambiguous_separator_variant"
            else:
                kind = "requires_review"
            summary[kind] += 1
            records.append({
                "article_key": article_key,
                "ref_id": ref.get(XMLID),
                "original_target": target,
                "displayed_text": visible,
                "candidate_key": candidate,
                "alias_candidates": alias_matches,
                "numbered_candidates": numbered_matches,
                "lexical_candidates": target_matches[:20],
                "kind": kind,
                "context": snippet,
            })
    return {"schema_version": 1,
            "status": "review_diagnostics_not_approved_mappings",
            "total_unresolved_occurrences": len(records),
            "category_counts": dict(sorted(summary.items())),
            "numbered_link_review": [
                {"article_key": x["article_key"], "original_target": x["original_target"],
                 "candidates": x["numbered_candidates"], "context": x["context"][:300],
                 "numbered_markers": numbered_markers(
                     article_by_key[x["numbered_candidates"][0]], x["original_target"]
                 ),
                 "candidate_article_excerpt": " ".join(
                     "".join(article_by_key[x["numbered_candidates"][0]].itertext()).split()
                 )[:1100]}
                for x in records if len(x["numbered_candidates"]) == 1
                and x["original_target"] != x["numbered_candidates"][0]
            ],
            "ambiguous_alias_review": [
                {"article_key": x["article_key"], "original_target": x["original_target"],
                 "candidates": x["alias_candidates"], "context": x["context"][:170]}
                for x in records if x["kind"] == "ambiguous_semicolon_alias"
            ],
            "unique_semicolon_alias_candidates": [
                {"article_key": x["article_key"], "original_target": x["original_target"],
                 "candidate": x["alias_candidates"][0],
                 "context": x["context"][:180]}
                for x in records if x["kind"] == "unique_semicolon_alias_candidate"
            ],
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
