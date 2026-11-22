#!/usr/bin/env python3
"""Build a source-locked TEI P5 candidate, leaving the faithful master unchanged.

This is a mechanical migration with independently checked, serialized fidelity.
A successful run is NOT official TEI RELAX NG/Schematron certification.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

from audit_tei_structure import analyze

TEI = "http://www.tei-c.org/ns/1.0"
XML = "http://www.w3.org/XML/1998/namespace"
XMLID = "{" + XML + "}id"
XMLLANG = "{" + XML + "}lang"
Q = lambda tag: "{" + TEI + "}" + tag
ET.register_namespace("", TEI)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def walk_original(article):
    """All original article nodes have stable IDs; wrappers must not."""
    nodes = list(article.iter())
    if any(node.get(XMLID) is None for node in nodes):
        raise ValueError("An original article node has no xml:id")
    ids = [node.get(XMLID) for node in nodes]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate original article xml:id")
    return nodes


def original_indexed_text(article):
    """Exclude the synthetic headword but retain its original source tail."""
    children = list(article)
    if not children or children[0].tag != Q("head"):
        raise ValueError("Article does not start with a head")
    return (children[0].tail or "") + "".join(
        "".join(child.itertext()) for child in children[1:]
    )


def survey(root):
    body = root.find("./" + Q("text") + "/" + Q("body"))
    if root.tag != Q("TEI") or body is None:
        raise ValueError("Not an ISBE TEI document")
    articles = list(body)
    result = Counter(articles=len(articles))
    ids = {}
    for article in articles:
        if article.tag != Q("div") or article.get("type") != "entry":
            raise ValueError("Unexpected top-level article")
        for node in walk_original(article):
            uid = node.get(XMLID)
            if uid in ids:
                raise ValueError("Duplicate xml:id: " + uid)
            ids[uid] = node
            if node.tag == Q("ref"):
                if node.get("osisRef") is not None:
                    result["scripture_refs"] += 1
                elif node.get("target", "").startswith("#"):
                    result["internal_refs"] += 1
                else:
                    raise ValueError("Unexpected link semantics: " + uid)
            if node.tag == Q("seg") and node.get("type") == "unlinked-source-reference":
                result["unlinked_refs"] += 1
            if node.tag == Q("head") and node.get("type") == "bibliography":
                result["bibliography_heads"] += 1
    result["existing_xml_ids"] = len(ids)
    result["source_links"] = (
        result["internal_refs"] + result["unlinked_refs"] + result["bibliography_heads"] + 2
    )
    # Two source references were reclassified as bibliography leads, in addition
    # to the 27 full-head replacements; they are <hi rend=bibliography-heading>.
    # Count those rather than encoding that source detail as an unexplained constant.
    result["bibliography_leads"] = sum(
        node.tag == Q("hi") and node.get("rend") == "bibliography-heading"
        for article in articles for node in article.iter()
    )
    result["source_links"] = (
        result["internal_refs"] + result["unlinked_refs"] +
        result["bibliography_heads"] + result["bibliography_leads"]
    )
    return articles, ids, result


def normalize(root, counts):
    header = root.find(Q("teiHeader"))
    if header is None or header.find(Q("fileDesc")) is None:
        raise ValueError("Missing original TEI fileDesc")
    if root.get(XMLLANG) is not None or header.find(Q("encodingDesc")) is not None \
            or header.find(Q("revisionDesc")) is not None:
        raise ValueError("Unexpected pre-existing target metadata; review needed")
    root.set(XMLLANG, "en")
    enc = ET.SubElement(header, Q("encodingDesc"))
    decl = ET.SubElement(enc, Q("refsDecl"), {"n": "Bible"})
    ET.SubElement(decl, Q("p")).text = (
        "Scripture cRef values beginning with Bible: are copied character-for-"
        "character from CrossWire ISBE 2.2 ref/@osisRef. The Bible: prefix "
        "identifies the source's OSIS/SWORD Bible reference space; no external "
        "Bible edition, URI resolver or expanded target is asserted."
    )
    rev = ET.SubElement(header, Q("revisionDesc"))
    ET.SubElement(rev, Q("change"), {"when": "2026-11-22"}).text = (
        "Mechanical TEI P5 candidate derived from the immutable, checksum-"
        "pinned faithful CrossWire reconstruction; original is retained."
    )
    articles, targets, _ = survey(root)
    wrappers = 0
    for article in articles:
        children = list(article)
        if not children or children[0].tag != Q("head") \
                or children[0].text != article.get("n") \
                or children[0].get("type") is not None:
            raise ValueError("Synthetic headword does not match source key")
        children[0].set("type", "index")
        for node in article.iter():
            if node.tag != Q("ref"):
                continue
            if node.get("type") is not None:
                raise ValueError("An original ref already has a type")
            osis = node.attrib.pop("osisRef", None)
            dest = node.get("target", "")
            if osis is not None:
                if dest or node.get("cRef") is not None:
                    raise ValueError("CrossWire scripture ref has conflicting destinations")
                node.set("cRef", osis)
                node.set("type", "scripture")
            elif dest.startswith("#"):
                target = targets.get(dest[1:])
                if target is None:
                    raise ValueError("Broken source target: " + dest)
                node.set("type", "article" if target.tag == Q("div") and
                         target.get("type") == "entry" else "section")
            else:
                raise ValueError("Unknown reference kind")
        # Preserve each original node and every text/tail byte; only add
        # structurally neutral wrappers at the 27 already-attested heads.
        new_children = []
        bibliography = None
        for child in children:
            if child is not children[0] and child.tag == Q("head"):
                if child.get("type") != "bibliography":
                    raise ValueError("Unexpected source heading after headword")
                bibliography = ET.Element(Q("div"), {"type": "bibliography"})
                new_children.append(bibliography)
                wrappers += 1
            if bibliography is None:
                new_children.append(child)
            else:
                bibliography.append(child)
        article[:] = new_children
    if wrappers != counts["bibliography_heads"]:
        raise ValueError("Bibliography wrapper coverage changed")
    return wrappers


def prove_parity(original, candidate, index):
    old_articles, old_ids, old_counts = survey(original)
    new_articles = list(candidate.find("./" + Q("text") + "/" + Q("body")))
    if len(old_articles) != len(new_articles) or len(index) != len(old_articles):
        raise ValueError("Article coverage changed")
    if ET.tostring(original.find(Q("teiHeader")).find(Q("fileDesc"))) != \
            ET.tostring(candidate.find(Q("teiHeader")).find(Q("fileDesc"))):
        raise ValueError("Original fileDesc metadata changed")
    counted = Counter()
    for old, new, item in zip(old_articles, new_articles, index):
        if old.get(XMLID) != new.get(XMLID) or old.get("n") != new.get("n") \
                or item["key"] != old.get("n") or item["id"] != old.get(XMLID):
            raise ValueError("Article identity/order changed")
        old_text, new_text = original_indexed_text(old), original_indexed_text(new)
        if old_text != new_text or "".join(old.itertext()) != "".join(new.itertext()):
            raise ValueError("Article wording or whitespace changed: " + item["key"])
        if hashlib.sha256(new_text.encode("utf-8")).hexdigest() != item["text_sha256"]:
            raise ValueError("Source index text checksum changed: " + item["key"])
        old_nodes = walk_original(old)
        new_nodes = [node for node in new.iter() if node.get(XMLID) is not None]
        if [node.get(XMLID) for node in old_nodes] != \
                [node.get(XMLID) for node in new_nodes]:
            raise ValueError("An original node ID or order changed: " + item["key"])
        old_parents = {child: parent for parent in old.iter() for child in parent}
        new_parents = {child: parent for parent in new.iter() for child in parent}
        old_after_bib = False
        for previous, current in zip(old_nodes, new_nodes):
            if previous.tag != current.tag or previous.text != current.text \
                    or previous.tail != current.tail:
                raise ValueError("Original node markup/text changed: " + previous.get(XMLID))
            attrs = dict(previous.attrib)
            if previous is list(old)[0]:
                attrs["type"] = "index"
            if previous.tag == Q("ref"):
                if "osisRef" in attrs:
                    attrs["cRef"] = attrs.pop("osisRef")
                    attrs["type"] = "scripture"
                    counted["scripture_refs"] += 1
                else:
                    target = old_ids[attrs["target"][1:]]
                    attrs["type"] = "article" if target.tag == Q("div") \
                            and target.get("type") == "entry" else "section"
                    counted["internal_refs"] += 1
            if attrs != current.attrib:
                raise ValueError("Non-allowlisted attribute change: " + previous.get(XMLID))
            old_parent = old_parents.get(previous)
            new_parent = new_parents.get(current)
            if old_parent is None:
                if new_parent is not None:
                    raise ValueError("Article nesting changed")
            elif old_parent is old:
                if previous.tag == Q("head") and previous.get("type") == "bibliography":
                    old_after_bib = True
                if old_after_bib and previous is not list(old)[0]:
                    if new_parent.tag != Q("div") or new_parent.get("type") != "bibliography" \
                            or new_parents.get(new_parent) is not new:
                        raise ValueError("Unapproved bibliography nesting")
                elif new_parent is not new:
                    raise ValueError("Unapproved paragraph nesting")
            elif new_parent.get(XMLID) != old_parent.get(XMLID):
                raise ValueError("Unexpected original parent change")
        wrappers = [node for node in new.iter() if node.tag == Q("div") and
                    node.get("type") == "bibliography"]
        count_source_heads = sum(child.tag == Q("head") and
                                 child.get("type") == "bibliography" for child in old)
        if len(wrappers) != count_source_heads:
            raise ValueError("Bibliography wrappers do not match authored headings")
        for wrapper in wrappers:
            if wrapper.get(XMLID) is not None or list(wrapper)[0].tag != Q("head") \
                    or list(wrapper)[0].get("type") != "bibliography":
                raise ValueError("Invented bibliography ID or invalid content")
        counted["bibliography_wrappers"] += len(wrappers)
        counted["articles"] += 1
    all_original_ids = set(old_ids)
    all_candidate_ids = [node.get(XMLID) for article in new_articles
                         for node in article.iter() if node.get(XMLID)]
    if len(all_candidate_ids) != len(all_original_ids) or \
            set(all_candidate_ids) != all_original_ids:
        raise ValueError("Global xml:id coverage changed")
    for name in ("scripture_refs", "internal_refs"):
        if counted[name] != old_counts[name]:
            raise ValueError("Reference coverage changed: " + name)
    return dict(counted)


def build_candidate(source, output, index_path, manifest_path, report_path):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("version") != 1:
        raise ValueError("Unsupported migration manifest")
    if Path(source).resolve() == Path(output).resolve():
        raise ValueError("Must write a distinct candidate, never the master")
    expected_sha = manifest["source_sha256"]
    actual_sha = sha256(source)
    if actual_sha != expected_sha:
        raise ValueError("Source SHA-256 changed: " + actual_sha)
    original = ET.parse(source).getroot()
    _, _, counts = survey(original)
    for key, expected in manifest["expected"].items():
        if counts[key] != expected:
            raise ValueError("Pinned source inventory changed: " + key)
    index = json.loads(Path(index_path).read_text(encoding="utf-8"))
    candidate = ET.fromstring(ET.tostring(original, encoding="utf-8"))
    wrapper_count = normalize(candidate, counts)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".isbe-candidate-", suffix=".xml", dir=output.parent)
    try:
        with os.fdopen(fd, "wb") as output_file:
            ET.ElementTree(candidate).write(output_file, encoding="utf-8", xml_declaration=True)
        # All checks run against the serialized bytes, not only in-memory trees.
        serialized = ET.parse(name).getroot()
        changes = prove_parity(original, serialized, index)
        profile = analyze(name)
        if profile["profile_rule_findings"] or profile["duplicate_xml_ids"]:
            raise ValueError("Candidate fails ISBE target-profile checks: " +
                             str(profile["profile_rule_findings"]))
        if profile["entry_count"] != counts["articles"]:
            raise ValueError("Candidate article count changed after serialization")
        result = {
            "transformation_version": 1,
            "source_sha256": actual_sha,
            "candidate_sha256": sha256(name),
            "article_parity": "PASS",
            "all_original_nodes_text_attributes_ids_and_order": "PASS",
            "original_fileDesc_metadata": "PASS",
            "source_index_text_sha256_all_articles": "PASS",
            "serialized_profile_check": "PASS",
            "official_tei_schema_validation": "NOT_PERFORMED",
            "source_inventory": dict(counts),
            "transformation_counts": changes,
            "bibliography_wrappers": wrapper_count,
        }
        os.replace(name, output)
        report_path = Path(report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
        return result
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--index", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(build_candidate(args.input, args.output, args.index,
                                     args.manifest, args.report), indent=2))


if __name__ == "__main__":
    main()
