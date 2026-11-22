#!/usr/bin/env python3
"""Audit unresolved ISBE links in their containing articles.

The result is a contextual diagnostic, never a source-text correction.
"""
import argparse
from collections import Counter
import json
import unicodedata
import re
from difflib import get_close_matches, SequenceMatcher
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


def numbered_root(key):
    root, sep, suffix = key.rpartition(" (")
    if sep and suffix.endswith(")") and suffix[:-1].isdigit():
        return root.strip().casefold()
    return None


def scripture_refs(element):
    """Return explicit OSIS reference strings without semantic expansion."""
    if element is None:
        return set()
    refs = set()
    for node in element.iter():
        value = node.get("osisRef")
        if value:
            refs.update(part for part in value.split() if part)
    return refs


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
    comma_headings = {}
    for article in entries:
        key = article.get("n")
        if "," not in key:
            continue
        prefix = key.split(",", 1)[0].strip()
        if len(prefix) >= 3:
            comma_headings.setdefault(normalized(prefix), set()).add(key)
    article_by_key = {a.get("n"): a for a in entries}
    source_keys = list(article_by_key)
    # Candidate discovery is explicitly review-only. A shared word in a
    # longer title does not imply that both entries are equivalent.
    candidate_titles = {}
    for key in source_keys:
        for delimiter in (",", ";", " (", " "):
            if delimiter in key:
                term = key.split(delimiter, 1)[0].strip().casefold()
                if len(term) >= 3:
                    candidate_titles.setdefault(term, set()).add(key)
    numbered_candidates = {}
    for key in (a.get("n") for a in entries):
        stem = re.sub(r"\s+\(\d+\)$", "", key).strip().casefold()
        numbered_candidates.setdefault(stem, set()).add(key)
    numbered_groups = {}
    for a in entries:
        root_name = numbered_root(a.get("n"))
        if root_name is not None:
            numbered_groups.setdefault(root_name, []).append(a)
    numbered_candidate_osis = {
        a.get("n"): scripture_refs(a)
        for group in numbered_groups.values() for a in group
    }
    records = []
    scripture_candidates = []
    local_section_candidates = []
    summary = Counter()
    for article in entries:
        article_key = article.get("n")
        parents = {c: p for p in article.iter() for c in p}
        for ref in article.iter(REF):
            destination = ref.get("target", "")
            if not destination.startswith("ISBE:"):
                continue
            target = destination[5:]
            normalized_target = normalized(target)
            if "literature" in normalized_target or re.match(r"^(?:[IVXLCDM]+|[0-9]+)\\.\\s", target, re.I):
                label = re.sub(r"[:.\\s]+$", "", normalized_target)
                evidence = []
                for paragraph in article.iter():
                    if paragraph.tag.split("}")[-1] != "p":
                        continue
                    lead_text = (paragraph.text or "").strip()
                    if not lead_text and len(paragraph):
                        child = list(paragraph)[0]
                        if child.tag.split("}")[-1] == "hi":
                            lead_text = "".join(child.itertext()).strip()
                    phrase = " ".join(lead_text.split()).casefold()
                    if phrase.startswith(label) and (
                        len(phrase) == len(label) or phrase[len(label)] in " .:-"
                    ):
                        evidence.append({
                            "paragraph_id": paragraph.get(XMLID),
                            "leading_text": lead_text[:160],
                            "paragraph_preview": " ".join("".join(paragraph.itertext()).split())[:230],
                            "child_tags": [x.tag.split("}")[-1] for x in list(paragraph)[:5]]
                        })
                local_section_candidates.append({
                    "article": article_key, "target": target,
                    "ref_id": ref.get(XMLID), "candidate_paragraphs": evidence[:12],
                    "candidates_total": len(evidence)
                })
            visible = "".join(ref.itertext()).strip()
            candidate = classify_candidate(target, visible, known)
            parent = parents.get(ref)
            while parent is not None and parent.tag.split("}")[-1] not in ("p", "item", "ab"):
                parent = parents.get(parent)
            container_text = "".join(parent.itertext()) if parent is not None else ""
            snippet = " ".join(container_text.split())[:450]
            ambiguous_homonyms = numbered_groups.get(normalized(target), ())
            if len(ambiguous_homonyms) > 1:
                local_refs = scripture_refs(parent)
                candidates = []
                for candidate_article in ambiguous_homonyms:
                    candidate_key = candidate_article.get("n")
                    common = sorted(local_refs & numbered_candidate_osis[candidate_key])
                    candidates.append({"article_key": candidate_key, "shared_osis_refs": common})
                positive = [item for item in candidates if item["shared_osis_refs"]]
                if len(positive) == 1:
                    scripture_candidates.append({
                        "source_article": article_key,
                        "ref_id": ref.get(XMLID),
                        "original_target": target,
                        "candidate": positive[0]["article_key"],
                        "candidate_article_excerpt": " ".join(
                            "".join(article_by_key[positive[0]["article_key"]].itertext()).split()
                        )[:900],
                        "exclusive_common_refs": positive[0]["shared_osis_refs"],
                        "all_candidate_scores": [
                            {"article": item["article_key"], "common": len(item["shared_osis_refs"])}
                            for item in candidates
                        ],
                        "context": snippet[:280],
                    })
            comma_prefix_matches = sorted(comma_headings.get(normalized(target), ()))
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
                "comma_prefix_candidates": comma_prefix_matches,
                "numbered_candidates": numbered_matches,
                "lexical_candidates": target_matches[:20],
                "kind": kind,
                "context": snippet,
            })
    return {"schema_version": 1,
            "status": "review_diagnostics_not_approved_mappings",
            "total_unresolved_occurrences": len(records),
            "category_counts": dict(sorted(summary.items())),
            "unresolved_numbered_homonyms": [
                {"source_article": x["article_key"], "original_target": x["original_target"],
                 "ref_id": x["ref_id"], "context": x["context"][:340],
                 "candidates": [
                     {"article_key": a.get("n"),
                      "article_excerpt": " ".join("".join(a.itertext()).split())[:540],
                      "osis_refs": sorted(scripture_refs(a))[:10]}
                     for a in numbered_groups[normalized(x["original_target"])]
                 ]}
                for x in records
                if len(numbered_groups.get(normalized(x["original_target"]), ())) > 1
            ],
            "exclusive_scripture_numbered_candidates": scripture_candidates,
            "local_section_review": local_section_candidates,
            "fuzzy_heading_review": [
                {
                    "target": target,
                    "occurrences": sum(1 for item in records if item["original_target"] == target),
                    "candidates": [
                        {"title": candidate,
                         "ratio": round(SequenceMatcher(
                             None, normalized(target), normalized(candidate)
                         ).ratio(), 3)}
                        for candidate in get_close_matches(
                            target, source_keys, n=4, cutoff=0.72
                        )
                    ],
                }
                for target in sorted(set(x["original_target"] for x in records))
                if get_close_matches(target, source_keys, n=1, cutoff=0.72)
            ],
            "article_heading_candidates": [
                {
                    "target": target,
                    "occurrences": sum(1 for item in records if item["original_target"] == target),
                    "title_candidates": sorted(candidate_titles.get(normalized(target), []))[:25]
                }
                for target in sorted(set(x["original_target"] for x in records))
                if candidate_titles.get(normalized(target))
            ],
            "inverted_definite_article_review": [
                {"article_key": x["article_key"], "original_target": x["original_target"],
                 "candidate": x["comma_prefix_candidates"][0],
                 "context": x["context"][:170]}
                for x in records if len(x["comma_prefix_candidates"]) == 1
                and x["comma_prefix_candidates"][0].split(",", 1)[1].strip().casefold() == "the"
                and not x["alias_candidates"]
            ],
            "unique_comma_prefix_review": [
                {"article_key": x["article_key"], "original_target": x["original_target"],
                 "candidate": x["comma_prefix_candidates"][0], "context": x["context"][:200]}
                for x in records if len(x["comma_prefix_candidates"]) == 1
                and len(x["alias_candidates"]) == 0
            ],
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
