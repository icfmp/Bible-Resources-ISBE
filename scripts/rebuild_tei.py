#!/usr/bin/env python3
"""Rebuild a verifiable, article-indexed TEI edition from SWORD mod2imp output.

The original SWORD ZIP and the raw IMP export are separate immutable inputs.
This script does not modernize, correct, or translate the article text.
"""
import argparse
import hashlib
import html.entities
import json
import re
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

TEI = "http://www.tei-c.org/ns/1.0"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
ET.register_namespace("", TEI)
ENTRY = re.compile(r"(?m)^\$\$\$(.*?)\r?$")
ENTITY = re.compile(r"&([A-Za-z][A-Za-z0-9]+);")
PREDEFINED = {"amp", "lt", "gt", "quot", "apos"}


def title_id(key):
    return "isbe-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]


def normalize_entities(xml):
    def replace(match):
        name = match.group(1)
        if name in PREDEFINED:
            return match.group(0)
        entity = html.entities.html5.get(name + ";")
        if entity is None:
            raise ValueError(f"Unknown named entity &{name};")
        return entity
    return ENTITY.sub(replace, xml)


def entries_from_imp(text):
    matches = list(ENTRY.finditer(text))
    if not matches:
        raise ValueError("No $$$ records in SWORD export")
    if text[:matches[0].start()].strip():
        raise ValueError("Unexpected non-whitespace before first entry")
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        key = match.group(1).strip()
        if not key:
            raise ValueError(f"Empty SWORD entry key at record {i+1}")
        yield key, text[match.end():end].strip()


def build(imp):
    records = list(entries_from_imp(imp))
    ids = {}
    for key, _ in records:
        if key in ids:
            raise ValueError(f"Duplicate entry key: {key}")
        aid = title_id(key)
        if aid in ids.values():
            raise ValueError(f"Article ID collision: {key}")
        ids[key] = aid

    root = ET.Element(f"{{{TEI}}}TEI")
    header = ET.SubElement(root, f"{{{TEI}}}teiHeader")
    fd = ET.SubElement(header, f"{{{TEI}}}fileDesc")
    ts = ET.SubElement(fd, f"{{{TEI}}}titleStmt")
    ET.SubElement(ts, f"{{{TEI}}}title").text = "International Standard Bible Encyclopedia — faithful CrossWire 2.2 extraction"
    pub = ET.SubElement(fd, f"{{{TEI}}}publicationStmt")
    ET.SubElement(pub, f"{{{TEI}}}p").text = "Unpublished working transcription; check source provenance and permissions before release."
    src = ET.SubElement(fd, f"{{{TEI}}}sourceDesc")
    ET.SubElement(src, f"{{{TEI}}}p").text = "CrossWire SWORD ISBE 2.2 (2009-09-07), historic James Orr edition."
    text = ET.SubElement(root, f"{{{TEI}}}text")
    body = ET.SubElement(text, f"{{{TEI}}}body")

    unsupported = Counter()
    missing_refs = Counter()
    title_variants = []
    text_chars = 0
    nodes = 0
    manifest = []
    for number, (key, fragment) in enumerate(records, 1):
        try:
            source = ET.fromstring(normalize_entities(fragment))
        except (ET.ParseError, ValueError) as exc:
            raise ValueError(f"Invalid XML in article #{number}, {key!r}: {exc}") from exc
        root_tag = source.tag.split("}")[-1]
        if root_tag != "entryFree":
            unsupported[root_tag] += 1
        if source.attrib.get("n") not in (None, key):
            title_variants.append({"key": key, "source_title": source.attrib["n"]})

        original_text = "".join(source.itertext())
        text_chars += len(original_text)
        aid = ids[key]
        article = ET.SubElement(body, f"{{{TEI}}}div", {"type": "entry", XMLID: aid, "n": key})
        heading = ET.SubElement(article, f"{{{TEI}}}head", {XMLID: aid + "-head"})
        heading.text = key
        heading.tail = source.text
        # Preserve every content node and its text (including tails).
        for child in list(source):
            source.remove(child)
            article.append(child)
        reconstructed_text = (heading.tail or "") + "".join("".join(ch.itertext()) + (ch.tail or "") for ch in list(article)[1:])
        # Element.itertext includes tail on the last node, so compare excluding
        # the synthetic head using a temporary neutral root.
        probe = ET.Element("probe")
        probe.text = heading.tail
        for child in list(article)[1:]:
            article.remove(child)
            probe.append(child)
        if "".join(probe.itertext()) != original_text:
            raise ValueError(f"Text mismatch after normalization: {key}")
        # Move children back in their original order after the content audit.
        for child in list(probe):
            probe.remove(child)
            article.append(child)

        for j, element in enumerate(article.iter(), 1):
            if element is article or element is heading:
                continue
            nodes += 1
            if XMLID in element.attrib:
                raise ValueError(f"Unexpected pre-existing xml:id in {key}: {element.attrib[XMLID]}")
            element.set(XMLID, f"{aid}-n{j:06d}")
            # The source uses ISBE:KEY to link to other entries.
            target = element.attrib.get("target", "")
            if target.startswith("ISBE:"):
                link_key = target[5:]
                if link_key in ids:
                    element.set("n", target)
                    element.set("target", "#" + ids[link_key])
                else:
                    missing_refs[link_key] += 1
        manifest.append({"index": number, "key": key, "id": aid,
                         "text_chars": len(original_text),
                         "text_sha256": hashlib.sha256(original_text.encode("utf-8")).hexdigest()})

    report = {"source_entries": len(records), "tei_entries": len(body),
              "indexed_content_nodes": nodes, "source_text_characters": text_chars,
              "other_root_tags": dict(unsupported),
              "source_title_variants": title_variants,
              "unresolved_isbe_links": dict(missing_refs),
              "unresolved_link_occurrences": sum(missing_refs.values()),
              "text_integrity": "validated for every entry"}
    return root, manifest, report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--index", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--expected-entries", type=int, default=9380)
    args = p.parse_args()
    raw = args.input.read_bytes().decode("utf-8", errors="strict")
    root, index, report = build(raw)
    if report["source_entries"] != args.expected_entries:
        raise ValueError(f"Entry count differs from expected: {report['source_entries']}")
    for path in (args.output, args.index, args.report):
        path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(args.output, encoding="utf-8", xml_declaration=True)
    # Validate serialized output too, not just in-memory XML.
    round_trip = ET.parse(args.output)
    articles = round_trip.findall(f".//{{{TEI}}}div[@type='entry']")
    if len(articles) != len(index):
        raise ValueError("Serialized TEI article count differs from input")
    for article, item in zip(articles, index):
        children = list(article)
        if not children or children[0].tag != f"{{{TEI}}}head":
            raise ValueError("Serialized TEI article missing heading")
        # Content includes the heading tail but not the synthetic heading text.
        source_text = (children[0].tail or "") + "".join(
            ("".join(ch.itertext()) + (ch.tail or "")) for ch in children[1:])
        actual_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        if actual_hash != item["text_sha256"]:
            raise ValueError(f"Serialized TEI changed article text: {item['key']}")
    args.index.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
