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


def separator_key(text):
    """Ignore editorial separators, retaining letters, digits and apostrophes."""
    return re.sub(r"[\s,;().-]+", "", text.casefold())


def semicolon_alias_index(keys):
    """Recognize source-provided alternative headings, never inferred synonyms."""
    result = {}
    for key in keys:
        for part in key.split(";"):
            alias = part.strip().casefold()
            if alias:
                owners = result.setdefault(alias, [])
                if key not in owners:
                    owners.append(key)
    return result


def resolve_key(raw_key, ids, normalized, separators=None, aliases=None):
    """Resolve only unique case, spacing or terminal-dot variations."""
    if raw_key in ids:
        return raw_key, "exact"
    folded = raw_key.strip().casefold()
    matches = normalized.get(folded, ())
    if len(matches) == 1:
        return matches[0], "case_or_space"
    if len(matches) > 1:
        return None, "ambiguous"
    if folded.endswith("."):
        matches = normalized.get(folded[:-1].rstrip(), ())
        if len(matches) == 1:
            return matches[0], "terminal_period"
        if len(matches) > 1:
            return None, "ambiguous"
    if separators is not None:
        matches = separators.get(separator_key(raw_key), ())
        if len(matches) == 1:
            return matches[0], "unique_separator_variant"
        if len(matches) > 1:
            return None, "ambiguous"
    if aliases is not None:
        candidates = aliases.get(raw_key.strip().casefold(), ())
        if len(candidates) == 1:
            return candidates[0], "explicit_semicolon_title_alias"
        if len(candidates) > 1:
            return None, "ambiguous"
    return None, "not_found"


def normalize_section_label(text):
    """Normalize presentation punctuation only, not words or numbering."""
    return re.sub(r"[:.\s]+$", "", " ".join(text.split())).casefold()


def resolve_local_heading(article, reference):
    """Resolve a source ISBE link to a unique explicit underlined local heading.

    An underlined leading heading or a standalone marked paragraph is accepted.
    Arbitrary inline emphasis and table-of-contents links are excluded.
    """
    parent_of = {child: parent for parent in article.iter() for child in parent}
    target = normalize_section_label(reference)
    if not target:
        return None
    candidates = []
    for el in article.iter():
        if el.tag.split("}")[-1] != "hi":
            continue
        parent = parent_of.get(el)
        if parent is None or parent.tag.split("}")[-1] != "p":
            continue
        if list(parent)[0] is not el or (parent.text or "").strip():
            continue
        standalone_heading = len(list(parent)) == 1 and not (el.tail or "").strip()
        label_text = "".join(el.itertext()).strip()
        numbered_title = bool(re.match(r"^(?:[IVXLCDM]+|[0-9]+)\.\s+", label_text, re.I))
        named_literature_heading = normalize_section_label(label_text) == "literature"
        explicit_heading_prefix = (numbered_title or named_literature_heading) and label_text.endswith((".", ":"))
        if el.get("rend") != "underline" and not standalone_heading and not explicit_heading_prefix:
            continue
        label = normalize_section_label("".join(el.itertext()))
        if label == target:
            candidates.append(el.get(XMLID))
    if len(candidates) == 1 and candidates[0]:
        return candidates[0]
    if len(candidates) > 1:
        return None

    # Some older entries use bare paragraphs for section headings. Match only
    # a unique, short, standalone paragraph whose *entire* content is the title.
    # Table-of-contents entries contain a ref child, so cannot match here.
    plain = []
    for el in article.iter():
        if el.tag.split("}")[-1] != "p" or len(el):
            continue
        label = (el.text or "").strip()
        if not label or len(label) > 180:
            continue
        if normalize_section_label(label) == target:
            plain.append(el.get(XMLID))
    if len(plain) == 1 and plain[0]:
        return plain[0]
    return None


def numbered_root(key):
    root, separator, suffix = key.rpartition(" (")
    if separator and suffix.endswith(")") and suffix[:-1].isdigit():
        return root.strip().casefold()
    return None


def scripture_refs(node):
    """Extract explicit original OSIS reference tokens; do not infer ranges."""
    if node is None:
        return set()
    result = set()
    for child in node.iter():
        value = child.get("osisRef")
        if value:
            result.update(value.split())
    return result


def unique_numbered_paragraph(article, marker):
    """Return a source-paragraph ID only for one matching section marker."""
    prefix = "(" + str(marker) + ")"
    matches = []
    for node in article.iter():
        if node.tag.split("}")[-1] != "p":
            continue
        label = "".join(node.itertext()).lstrip()
        if label.startswith(prefix) and (
            len(label) == len(prefix) or not label[len(prefix)].isalnum()
        ):
            matches.append(node.get(XMLID))
    return matches[0] if len(matches) == 1 and matches[0] else None


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

    normalized = {}
    for key in ids:
        normalized.setdefault(key.strip().casefold(), []).append(key)

    separators = {}
    for key in ids:
        separators.setdefault(separator_key(key), []).append(key)

    aliases = semicolon_alias_index(ids)

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
    resolved_variants = Counter()
    unresolved_details = Counter()
    resolved_local = Counter()
    resolved_numbered = Counter()
    resolved_scripture = Counter()
    resolved_redirect = Counter()
    articles_by_key = {}
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
        articles_by_key[key] = article
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
                resolved_key, reason = resolve_key(link_key, ids, normalized, separators, aliases)
                if resolved_key is not None:
                    element.set("n", target)
                    element.set("target", "#" + ids[resolved_key])
                    if reason != "exact":
                        resolved_variants[(link_key, resolved_key, reason)] += 1
                else:
                    missing_refs[link_key] += 1
                    unresolved_details[(link_key, reason)] += 1

        # The old module sometimes encoded its own section headings as
        # encyclopedia-wide targets. Only rewrite to a locally unique,
        # explicitly underlined heading; leave everything else untouched.
        for element in article.iter():
            target = element.attrib.get("target", "")
            if not target.startswith("ISBE:"):
                continue
            source_key = target[5:]
            heading_id = resolve_local_heading(article, source_key)
            if heading_id:
                element.set("n", target)
                element.set("target", "#" + heading_id)
                missing_refs[source_key] -= 1
                if not missing_refs[source_key]:
                    del missing_refs[source_key]
                unresolved_details[(source_key, "not_found")] -= 1
                if not unresolved_details[(source_key, "not_found")]:
                    del unresolved_details[(source_key, "not_found")]
                resolved_local[(key, source_key, heading_id)] += 1

        manifest.append({"index": number, "key": key, "id": aid,
                         "text_chars": len(original_text),
                         "text_sha256": hashlib.sha256(original_text.encode("utf-8")).hexdigest()})

    # The original ISBE sometimes links to a numbered subsection under an
    # unnumbered article key, e.g. BETHANY (2) -> BETHANY, paragraph "(2)".
    # Anchor only a unique, explicitly numbered paragraph in that exact entry.
    for source_key, source_article in articles_by_key.items():
        for element in source_article.iter():
            target = element.get("target", "")
            if not target.startswith("ISBE:"):
                continue
            source_target = target[5:]
            base, marker_separator, suffix = source_target.rpartition(" (")
            if not marker_separator or not suffix.endswith(")") or not suffix[:-1].isdigit():
                continue
            destination_article = articles_by_key.get(base)
            if destination_article is None:
                continue
            paragraph_id = unique_numbered_paragraph(destination_article, suffix[:-1])
            if paragraph_id is None:
                continue
            element.set("n", target)
            element.set("target", "#" + paragraph_id)
            missing_refs[source_target] -= 1
            if not missing_refs[source_target]:
                del missing_refs[source_target]
            reason_key = (source_target, "not_found")
            if unresolved_details[reason_key] <= 0:
                raise ValueError(f"Unexpected unresolved reason for {source_target}")
            unresolved_details[reason_key] -= 1
            if not unresolved_details[reason_key]:
                del unresolved_details[reason_key]
            resolved_numbered[(source_key, source_target, base, paragraph_id)] += 1

    # Distinct dictionary entries can share one headword (e.g. ABI (1/2)).
    # Resolve only when the referring paragraph and exactly one numbered
    # candidate share explicit, identical OSIS citations. Broad paragraphs
    # (over 20 unique citations) require at least two exclusive matches.
    numbered_groups = {}
    for key in ids:
        base = numbered_root(key)
        if base is not None:
            numbered_groups.setdefault(base, []).append(key)
    candidate_citations = {
        key: scripture_refs(articles_by_key[key])
        for names in numbered_groups.values() for key in names
    }
    for source_key, source_article in articles_by_key.items():
        parents = {c: p for p in source_article.iter() for c in p}
        for element in source_article.iter():
            target = element.get("target", "")
            if not target.startswith("ISBE:"):
                continue
            source_target = target[5:]
            possible = numbered_groups.get(source_target.strip().casefold(), ())
            if len(possible) < 2:
                continue
            context = parents.get(element)
            while context is not None and context.tag.split("}")[-1] not in ("p", "item", "ab"):
                context = parents.get(context)
            cited = scripture_refs(context)
            if not cited:
                continue
            common = {candidate: (cited & candidate_citations[candidate]) for candidate in possible}
            confirmed = [candidate for candidate in possible if common[candidate]]
            if len(confirmed) != 1:
                continue
            selected = confirmed[0]
            references = common[selected]
            if len(cited) > 20 and len(references) < 2:
                continue
            destination = articles_by_key[selected]
            # A parenthetical "which see (2)" explicitly refers to the
            # second numbered paragraph within the candidate, not necessarily
            # a second dictionary entry. Do not discard that distinction.
            tail = (element.tail or "")[:90]
            marker = re.search(r"\bsee\s*\((\d+)\)", tail, flags=re.I)
            selected_id = destination.get(XMLID)
            if marker:
                paragraph_id = unique_numbered_paragraph(destination, marker.group(1))
                if paragraph_id is None:
                    continue
                selected_id = paragraph_id
            element.set("n", target)
            element.set("target", "#" + selected_id)
            missing_refs[source_target] -= 1
            if not missing_refs[source_target]:
                del missing_refs[source_target]
            reason_key = (source_target, "not_found")
            if unresolved_details[reason_key] <= 0:
                raise ValueError(f"Unexpected source reference state for {source_target}")
            unresolved_details[reason_key] -= 1
            if not unresolved_details[reason_key]:
                del unresolved_details[reason_key]
            resolved_scripture[(source_key, source_target, selected, selected_id,
                                tuple(sorted(references)))] += 1

    # When a redirect-style source article has its own title as an alias of
    # two entries, an explicit "See" link cannot mean "open this same article".
    # Select the only other source-attested alias target, never an arbitrary
    # one of several competing destinations.
    for source_key, source_article in articles_by_key.items():
        parents = {c: p for p in source_article.iter() for c in p}
        for element in source_article.iter():
            target = element.get("target", "")
            if not target.startswith("ISBE:"):
                continue
            source_target = target[5:]
            possible = aliases.get(source_target.strip().casefold(), ())
            if len(possible) != 2 or source_key not in possible:
                continue
            destination_key = next(key for key in possible if key != source_key)
            parent = parents.get(element)
            while parent is not None and parent.tag.split("}")[-1] not in ("p", "item", "ab"):
                parent = parents.get(parent)
            if parent is None:
                continue
            paragraph_text = " ".join("".join(parent.itertext()).split())
            if not re.search(r"\\bsee\\b", paragraph_text, re.I):
                continue
            element.set("n", target)
            element.set("target", "#" + ids[destination_key])
            missing_refs[source_target] -= 1
            if not missing_refs[source_target]:
                del missing_refs[source_target]
            reason_key = (source_target, "ambiguous")
            if unresolved_details[reason_key] <= 0:
                raise ValueError(f"Unexpected ambiguous-alias state for {source_target}")
            unresolved_details[reason_key] -= 1
            if not unresolved_details[reason_key]:
                del unresolved_details[reason_key]
            resolved_redirect[(source_key, source_target, destination_key)] += 1

    report = {"source_entries": len(records), "tei_entries": len(body),
              "indexed_content_nodes": nodes, "source_text_characters": text_chars,
              "other_root_tags": dict(unsupported),
              "source_title_variants": title_variants,
              "resolved_variant_links": [
                  {"original": original, "resolved_to": mapped, "rule": rule, "occurrences": n}
                  for (original, mapped, rule), n in sorted(resolved_variants.items())
              ],
              "resolved_variant_occurrences": sum(resolved_variants.values()),
              "resolved_local_section_links": [
                  {"article_key": article_key, "original": original,
                   "local_heading_id": heading_id, "occurrences": count}
                  for (article_key, original, heading_id), count in sorted(resolved_local.items())
              ],
              "resolved_local_section_occurrences": sum(resolved_local.values()),
              "resolved_numbered_section_links": [
                  {"article_key": source_key, "original": original,
                   "target_article": target_article, "paragraph_id": paragraph_id,
                   "occurrences": count}
                  for (source_key, original, target_article, paragraph_id), count
                  in sorted(resolved_numbered.items())
              ],
              "resolved_numbered_section_occurrences": sum(resolved_numbered.values()),
              "resolved_scripture_disambiguation_links": [
                  {"source_article": source, "original": original,
                   "destination_article": chosen, "destination_id": destination_id,
                   "exclusive_osis_references": list(references), "occurrences": count}
                  for (source, original, chosen, destination_id, references), count
                  in sorted(resolved_scripture.items())
              ],
              "resolved_scripture_disambiguation_occurrences": sum(resolved_scripture.values()),
              "resolved_redirect_alias_links": [
                  {"article_key": source, "original": original,
                   "destination_article": chosen, "occurrences": count}
                  for (source, original, chosen), count in sorted(resolved_redirect.items())
              ],
              "resolved_redirect_alias_occurrences": sum(resolved_redirect.values()),
              "unresolved_link_diagnostics": [
                  {"original": key, "reason": reason, "occurrences": n}
                  for (key, reason), n in sorted(unresolved_details.items())
              ],
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
    all_ids = set()
    for node in round_trip.iter():
        xml_id = node.get(XMLID)
        if not xml_id:
            continue
        if xml_id in all_ids:
            raise ValueError(f"Duplicate TEI xml:id: {xml_id}")
        all_ids.add(xml_id)
    unresolved_seen = 0
    resolved_seen = 0
    for node in round_trip.iter():
        target = node.get("target", "")
        original = node.get("n", "")
        if target.startswith("ISBE:"):
            unresolved_seen += 1
        if original.startswith("ISBE:") and target.startswith("#"):
            resolved_seen += 1
            if target[1:] not in all_ids:
                raise ValueError(f"Broken resolved ISBE link: {original} -> {target}")
    if unresolved_seen != report["unresolved_link_occurrences"]:
        raise ValueError("Serialized TEI unresolved link total differs from report")
    report["resolved_internal_links_validated"] = resolved_seen
    report["xml_id_uniqueness"] = "validated"

    args.index.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
