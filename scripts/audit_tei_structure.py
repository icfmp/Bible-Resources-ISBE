#!/usr/bin/env python3
"""Read-only TEI structural inventory; not an official TEI schema validator.

The report describes existing markup, namespaces and risk patterns. It makes
no editorial changes and cannot certify P5, source parity or reader rendering.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

TEI = "http://www.tei-c.org/ns/1.0"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"


def expanded_name(tag):
    if not isinstance(tag, str):
        return str(tag)
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def namespace(tag):
    return tag[1:].split("}", 1)[0] if isinstance(tag, str) and tag.startswith("{") else ""


def analyze(path):
    path = Path(path)
    root = ET.parse(path).getroot()
    body = root.find(f"./{{{TEI}}}text/{{{TEI}}}body")
    if root.tag != f"{{{TEI}}}TEI" or body is None:
        raise ValueError("Expected a TEI root with a namespaced text/body")
    counts = Counter()
    source_tag = Counter()
    source_namespace = Counter()
    attrs = defaultdict(Counter)
    attr_examples = {}
    rend = Counter()
    children = Counter()
    paragraph_child = Counter()
    article_structures = Counter()
    samples = defaultdict(list)
    ids = set()
    duplicates = []
    link_classes = Counter()
    notes_by_tag = Counter()
    unqualified_examples = []
    suspicious = defaultdict(list)
    profile_counts = Counter()
    profile_examples = defaultdict(list)
    def flag(code, key):
        profile_counts[code] += 1
        if len(profile_examples[code]) < 8:
            profile_examples[code].append(key)
    if root.get("{http://www.w3.org/XML/1998/namespace}lang") != "en":
        flag("document_language_missing_or_incorrect", "(document)")
    if root.find(f"./{{{TEI}}}teiHeader/{{{TEI}}}revisionDesc") is None:
        flag("revision_history_missing", "(header)")
    if root.find(f"./{{{TEI}}}teiHeader/{{{TEI}}}encodingDesc/{{{TEI}}}refsDecl") is None:
        flag("canonical_scripture_reference_declaration_missing", "(header)")
    articles = list(body)
    seen_source_keys = set()
    for article in articles:
        if article.tag != f"{{{TEI}}}div" or article.get("type") != "entry":
            raise ValueError("Unexpected top-level article structure")
        key = article.get("n")
        if not key:
            raise ValueError("Article without source SWORD key")
        if key in seen_source_keys:
            raise ValueError(f"Duplicate source SWORD key {key!r}")
        seen_source_keys.add(key)
        immediate = tuple(expanded_name(c.tag) for c in article)
        article_structures["first=" + (immediate[0] if immediate else "(none)")] += 1
        article_structures["direct_children=" + str(len(immediate))] += 1
        if not immediate or immediate[0] != "head":
            suspicious["missing_synthetic_head"].append(key)
            flag("index_head_missing", key)
        elif article[0].get("type") != "index":
            flag("index_head_not_typed", key)
        for position, child in enumerate(article):
            if position and expanded_name(child.tag) == "head":
                flag("head_after_body_content_requires_section_division", key)
        for node in article.iter():
            tag = expanded_name(node.tag)
            ns = namespace(node.tag)
            source_tag[tag] += 1
            source_namespace[ns or "(none)"] += 1
            if ns != TEI:
                flag("body_element_outside_tei_namespace", key)
            attrs[tag].update(expanded_name(a) for a in node.attrib if a != XMLID)
            if len(samples[tag]) < 5 and node is not article and node is not article[0]:
                samples[tag].append(key)
            uid = node.get(XMLID)
            if uid:
                if uid in ids:
                    duplicates.append({"id": uid, "entry": key})
                ids.add(uid)
            if ns != TEI and len(unqualified_examples) < 25:
                unqualified_examples.append({"entry": key, "tag": tag, "namespace": ns or "(none)"})
            if tag == "hi":
                rend[node.get("rend", "(missing)")] += 1
            if tag in ("note", "bibl", "listBibl"):
                notes_by_tag[tag] += 1
            if tag == "p":
                paragraph_child.update(expanded_name(c.tag) for c in node)
                if not (node.text or "").strip() and not len(node):
                    counts["empty_paragraphs"] += 1
            if tag == "ref":
                if node.get("osisRef") is not None:
                    flag("legacy_crosswire_osisRef_attribute", key)
                if not node.get("type"):
                    flag("untyped_reference", key)
                if node.get("target") and node.get("cRef"):
                    flag("reference_has_both_target_and_cRef", key)
                target = node.get("target", "")
                if node.get("osisRef") is not None:
                    link_classes["source_osisRef"] += 1
                if node.get("cRef") is not None:
                    link_classes["tei_cRef"] += 1
                if target.startswith("#"):
                    link_classes["internal_target"] += 1
                elif target.startswith("ISBE:"):
                    link_classes["active_original_isbe_target"] += 1
                elif target:
                    link_classes["other_target"] += 1
                elif not node.get("osisRef") and not node.get("cRef"):
                    link_classes["no_recognized_target"] += 1
                if node.get("osisRef") and target:
                    counts["ref_has_both_target_and_osisRef"] += 1
            if tag == "seg" and node.get("type") == "unlinked-source-reference":
                link_classes["inert_original_isbe_reference"] += 1
            for child in node:
                children[tag + " > " + expanded_name(child.tag)] += 1
    for item in body:
        if not item.get(XMLID):
            suspicious["article_without_id"].append(item.get("n", "(missing)"))
    stats = {
        "source_xml_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "schema_validation": "NOT_PERFORMED",
        "entry_count": len(articles),
        "unique_xml_ids": len(ids),
        "duplicate_xml_ids": duplicates[:50],
        "elements_by_local_name": dict(source_tag.most_common()),
        "elements_by_namespace": dict(source_namespace.most_common()),
        "attributes_by_element": {k: dict(v.most_common()) for k, v in sorted(attrs.items())},
        "inline_rendering_values": dict(rend.most_common()),
        "parent_child_pairs": dict(children.most_common()),
        "paragraph_direct_children": dict(paragraph_child.most_common()),
        "link_classes": dict(link_classes.most_common()),
        "notes_and_bibliography_tags": dict(notes_by_tag.most_common()),
        "empty_paragraph_count": counts["empty_paragraphs"],
        "dual_target_reference_count": counts["ref_has_both_target_and_osisRef"],
        "article_structure_summary": {k: v for k,v in article_structures.items() if k.startswith("first=")},
        "example_article_keys_by_element": dict(samples),
        "unqualified_element_examples": unqualified_examples,
        "structural_anomaly_examples": dict(suspicious),
        "profile_status": ("candidate_subset_conformant" if not profile_counts
                           else "migration_required"),
        "profile_rule_findings": {
            k: {"count": v, "example_entries": profile_examples[k]}
            for k, v in profile_counts.most_common()
        },
        "profile_check_only": "ISBE subset, NOT official TEI P5 schema validation",
    }
    return stats


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("tei", type=Path)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--strict-profile", action="store_true",
                   help="Fail if any ISBE target-profile conformance finding remains")
    args = p.parse_args()
    report = analyze(args.tei)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "profile_status": report["profile_status"],
        "profile_rule_findings": report["profile_rule_findings"],
        "entry_count": report["entry_count"],
        "elements_by_local_name": report["elements_by_local_name"],
        "elements_by_namespace": report["elements_by_namespace"],
        "link_classes": report["link_classes"],
    }, indent=2))
    if args.strict_profile and report["profile_rule_findings"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
