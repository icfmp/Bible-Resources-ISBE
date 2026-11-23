#!/usr/bin/env python3
"""Repair an exact displayed Scripture navigation target in a separate TEI.

This is **digital-source metadata consistency**, not original-1915 printed-page
certification. No source article prose, original IDs, CrossWire master or
previous editorial layer is modified. A parallel, image-attested reference can establish book mapping, but never
certifies the wording of an unobserved article's original printed folios.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from scripts.audit_tei_structure import analyze

T = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"
LOCK = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
ET.register_namespace("", "http://www.tei-c.org/ns/1.0")


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def articles(root):
    body = root.find(f"./{T}text/{T}body")
    if root.tag != T + "TEI" or body is None:
        raise ValueError("Not a TEI P5 body")
    rows = {}
    for article in body:
        key = article.get("n")
        if article.tag != T + "div" or not key or key in rows or not article.get(ID):
            raise ValueError("Unstable or missing source article identity")
        rows[key] = article
    return rows


def verified_decisions(spec, candidates):
    if (spec.get("schema_version") != 1
            or spec.get("canonical_source_sha256") != LOCK
            or spec.get("preceding_editorial_layer") != "1915_print_attested_31_plus_6_plus_12_plus_1"
            or spec.get("evidence_level") != "digital_display_parallel_print_mapping_not_taanach_print"
            or spec.get("original_1915_folios_verified") is not False
            or spec.get("publication_permitted") is not False
            or spec.get("independent_human_peer_review") is not False
            or candidates.get("canonical_sha256") != LOCK
            or candidates.get("canonical_modified") is not False):
        raise ValueError("Evidence tier drift or unauthorized printed certification")
    source = {r["ref_xml_id"]: r for r in candidates["cases"]}
    rows = spec.get("decisions")
    if not isinstance(rows, list) or not rows:
        raise ValueError("No explicit source-display navigation decisions")
    seen = set()
    for row in rows:
        rid = row["source_ref_xml_id"]
        source_row = source.get(rid)
        if (rid in seen or source_row is None or row.get("printed_1915_certification") is not False
                or row.get("approved_for_noncanonical_navigation_layer") is not True
                or source_row["disposition"] != "unresolved_no_adequate_print_page"
                or source_row["proposed_cRef"] is not None
                or (row["source_key"], row["source_unit_xml_id"], row["original_visible"], row["original_cRef"])
                != (source_row["source_key"], source_row["unit_xml_id"], source_row["visible"], source_row["original_cRef"])
                or not isinstance(row.get("digital_witness_urls"), list)
                or len(set(row["digital_witness_urls"])) < 2
                or not all(u.startswith("https://") for u in row["digital_witness_urls"])):
            raise ValueError("Missing exact digital source or independent corroboration")
        # A different, image-attested printed article corroborates the
        # book-code mapping. This NEVER certifies the missing article folio.
        parallel = source.get(row.get("parallel_print_attested_ref_xml_id"))
        if (parallel is None
                or parallel["source_key"] != row.get("parallel_print_attested_article")
                or parallel["ref_xml_id"] == rid
                or parallel["disposition"] != "visually_attested_candidate"
                or parallel["visible"] != row["original_visible"]
                or parallel["proposed_cRef"] != row["corrected_cRef"]
                or not parallel.get("source_image_jpeg_sha256")
                or not parallel.get("printed_reading")):
            raise ValueError("Uncorroborated displayed book-to-target mapping")
        label = row["original_visible"]
        explicit = re.findall(r"(?<![A-Za-z0-9])([1-3]?[A-Za-z]+)\s+(\d+):(\d+)(?!\d)", label)
        expected = (str(row["explicit_label_book"]), str(row["explicit_label_chapter"]), str(row["explicit_label_verse"]))
        if (len(explicit) != 1 or explicit[0] != expected
                or row["original_cRef"] == row["corrected_cRef"]
                or not re.fullmatch(r"Bible:[A-Za-z0-9]+\.\d+\.\d+", row["corrected_cRef"])
                or row["corrected_cRef"].rsplit(".", 2)[-2:] != list(expected[-2:])):
            raise ValueError("Navigation target disagrees with explicit displayed chapter/verse")
        seen.add(rid)
    return rows


def apply_changes(root, decisions):
    entries = articles(root)
    changed, operations = set(), []
    for row in decisions:
        key = row["source_key"]
        article = entries.get(key)
        if article is None:
            raise ValueError("Missing article")
        para = [p for p in article.iter(T + "p") if p.get(ID) == row["source_unit_xml_id"]]
        ref = [r for r in article.iter(T + "ref") if r.get(ID) == row["source_ref_xml_id"]]
        if len(para) != 1 or len(ref) != 1 or ref[0] not in list(para[0].iter()):
            raise ValueError("Reference and paragraph IDs are not uniquely linked")
        item = ref[0]
        if (item.get("type") != "scripture" or item.get("cRef") != row["original_cRef"]
                or "".join(item.itertext()) != row["original_visible"]
                or item.get("target") is not None):
            raise ValueError("Digital source visible/reference content changed")
        original = ET.tostring(article, encoding="utf-8")
        item.set("cRef", row["corrected_cRef"])
        revised = ET.tostring(article, encoding="utf-8")
        item.set("cRef", row["original_cRef"])
        if ET.tostring(article, encoding="utf-8") != original:
            raise ValueError("Target correction was not reversible")
        item.set("cRef", row["corrected_cRef"])
        if revised == original or key in changed:
            raise ValueError("No-op or duplicate article operation")
        changed.add(key)
        operations.append({"article_key": key, "unit_xml_id": row["source_unit_xml_id"],
                           "reference_xml_id": row["source_ref_xml_id"],
                           "original_cRef": row["original_cRef"],
                           "corrected_cRef": row["corrected_cRef"],
                           "unchanged_visible": row["original_visible"],
                           "source_article_sha256": sha256(original).hexdigest(),
                           "revised_article_sha256": sha256(revised).hexdigest(),
                           "evidence_level": "digital_display_only_not_1915_print_certified",
                           "reversible": True})
    return changed, operations


def run(source, baseline, prior_report, prior_validator, ledger, candidates, output,
        report, derived_validator, derived_fidelity):
    if digest(source) != LOCK:
        raise ValueError("Canonical CrossWire TEI SHA mismatch")
    preceding = load(prior_report)
    if (preceding.get("revised_sha256") != digest(baseline)
            or preceding.get("article_count") != 9380
            or preceding.get("textual_reference_deltas") != 1
            or preceding.get("publication_permitted") is not False):
        raise ValueError("Previous print-attested 31+6+12+1 witness invalid")
    decisions = verified_decisions(load(ledger), load(candidates))
    root = ET.parse(baseline).getroot()
    entries = articles(root)
    if len(entries) != 9380:
        raise ValueError("Expected 9,380 source articles")
    before = {k: ET.tostring(a, encoding="utf-8") for k, a in entries.items()}
    text = {k: "".join(a.itertext()) for k, a in entries.items()}
    old_ids = [n.get(ID) for a in entries.values() for n in a.iter() if n.get(ID)]
    changed, operations = apply_changes(root, decisions)
    if any("".join(a.itertext()) != text[k] for k, a in entries.items()):
        raise ValueError("Displayed source article text was modified")
    if any(ET.tostring(a, encoding="utf-8") != before[k] for k,a in entries.items() if k not in changed):
        raise ValueError("Unrelated source article drift")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)
    verified = articles(ET.parse(output).getroot())
    new_ids = [n.get(ID) for a in verified.values() for n in a.iter() if n.get(ID)]
    if list(verified) != list(entries) or new_ids != old_ids:
        raise ValueError("Article order or original XML IDs changed")
    for key, a in verified.items():
        if "".join(a.itertext()) != text[key] or (key not in changed and ET.tostring(a, encoding="utf-8") != before[key]):
            raise ValueError("Unexpected serialized content modifications")
    structural = analyze(output)
    if structural["profile_rule_findings"] or structural["duplicate_xml_ids"]:
        raise ValueError("Strict TEI project profile failed")
    result = {"canonical_sha256": LOCK, "preceding_editorial_sha256": digest(baseline),
              "revised_sha256": digest(output), "article_count": len(verified),
              "changed_articles": len(changed), "unchanged_articles": len(verified)-len(changed),
              "navigation_target_changes": len(operations), "xml_ids_preserved": len(old_ids),
              "visible_text_byte_equivalent": True, "original_1915_print_certification": False,
              "publication_permitted": False, "independent_human_peer_review": False,
              "original_sources_unchanged": True, "changes": operations}
    validator = {**load(prior_validator), "expected_candidate_sha256": result["revised_sha256"],
                 "noncanonical_review_only": True, "review_delta_ledger": str(ledger)}
    fidelity = {"candidate_sha256": result["revised_sha256"], "article_parity": "PASS",
                "serialized_profile_check": "PASS", "publication_permitted": False,
                "noncanonical": True, "independent_human_peer_review": False,
                "changed_reference_metadata_only": len(operations)}
    for target, payload in ((report, result), (derived_validator, validator),
                            (derived_fidelity, fidelity)):
        dest = Path(target)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", default="cleaned/en/ISBE.xml")
    p.add_argument("--ledger", default="workspace/reviews/1915-source-display-navigation-deltas-v1.json")
    p.add_argument("--candidates", default="workspace/reviews/1915-scripture-reference-image-triage-v1.json")
    for field in ("baseline", "prior-report", "prior-validator", "output", "report",
                  "derived-validator", "derived-fidelity"):
        p.add_argument("--" + field, required=True)
    args = p.parse_args()
    result = run(args.source, args.baseline, args.prior_report, args.prior_validator,
                 args.ledger, args.candidates, args.output, args.report,
                 args.derived_validator, args.derived_fidelity)
    print(json.dumps({k:v for k,v in result.items() if k != "changes"}, indent=2))


if __name__ == "__main__":
    main()
