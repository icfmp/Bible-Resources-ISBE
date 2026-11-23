#!/usr/bin/env python3
"""Apply individually reviewed printed Scripture text-and-target deltas to a NEW TEI.

This layer follows the already reviewed 31 restorations, six text deltas,
and twelve metadata-only Scripture target corrections. It must never edit
the CrossWire witness or any of the preceding generated editorial layers.
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


def text_digest(value):
    return sha256(value.encode("utf-8")).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def articles(root):
    if root.tag != T + "TEI":
        raise ValueError("Expected TEI P5 document")
    body = root.find(f"./{T}text/{T}body")
    if body is None:
        raise ValueError("Missing TEI body")
    result = {}
    for entry in body:
        key = entry.get("n")
        if not key or key in result or not entry.get(ID):
            raise ValueError("Invalid or duplicated source article")
        result[key] = entry
    return result


def validate_decisions(spec, evidence, manifest):
    """Evidence is a read-only source-image ledger, not a substitute for print."""
    if (spec.get("schema_version") != 1
            or spec.get("canonical_source_sha256") != LOCK
            or spec.get("publication_permitted") is not False
            or spec.get("independent_human_peer_review") is not False
            or spec.get("previous_layer")
               != "1915_source_image_attested_twelve_scripture_navigation_targets"):
        raise ValueError("Unrecognized or publishable editorial decision ledger")
    if (evidence.get("canonical_sha256") != LOCK
            or evidence.get("publication_permitted") is not False
            or evidence.get("canonical_modified") is not False
            or manifest.get("canonical_tei_sha256") != LOCK):
        raise ValueError("Historical primary-source evidence drift")
    rows = spec.get("decisions")
    if not isinstance(rows, list) or not rows:
        raise ValueError("No exact print-backed editorial decisions")
    source = {v["volume"]: v for v in manifest["volumes"]}
    seen = set()
    for row in rows:
        if row.get("approved_for_separate_editorial_tei") is not True:
            raise ValueError("Editorial delta is not explicitly approved")
        if row.get("operation") != "replace_continuation_scripture_reference":
            raise ValueError("Unsupported editorial operation")
        for field in ("source_key", "source_unit_xml_id", "source_ref_xml_id",
                      "preceding_ref_xml_id", "original_visible",
                      "corrected_visible", "original_cRef", "corrected_cRef",
                      "print_reading", "rationale"):
            if not isinstance(row.get(field), str) or not row[field]:
                raise ValueError("Incomplete exact-source editorial operation")
        identity = (row["source_key"], row["source_ref_xml_id"])
        if identity in seen:
            raise ValueError("Repeated source reference delta")
        seen.add(identity)
        if (row["original_visible"] == row["corrected_visible"]
                or row["original_cRef"] == row["corrected_cRef"]
                or not re.fullmatch(r"Bible:[A-Za-z0-9]+\.\d+\.\d+",
                                    row["corrected_cRef"])
                or not re.fullmatch(r"[a-f0-9]{64}", row.get("source_unit_text_sha256", ""))):
            raise ValueError("Invalid textual or metadata change")
        vol = source.get(row.get("print_volume"))
        if (vol is None or row.get("print_pdf_sha256") != vol["pdf_sha256"]
                or not isinstance(row.get("print_pdf_page_1_based"), int)
                or not 1 <= row["print_pdf_page_1_based"] <= vol["pages"]
                or not re.fullmatch(r"[a-f0-9]{64}", row.get("print_jpeg_sha256", ""))
                or not isinstance(row.get("source_image_job_id"), int)
                or not isinstance(row.get("source_image_workflow_run"), int)):
            raise ValueError("No complete SHA-pinned source-page evidence")
        matches = [r for r in evidence["cases"]
                   if r["source_key"] == row["source_key"]
                   and r["ref_xml_id"] == row["preceding_ref_xml_id"]
                   and r["print_volume"] == row["print_volume"]]
        if len(matches) != 1:
            raise ValueError("Unknown first Scripture reference in source evidence")
        proof = matches[0]
        if (proof["disposition"] != "visually_attested_candidate"
                or proof["pdf_page_1_based"] != row["print_pdf_page_1_based"]
                or proof["source_pdf_sha256"] != row["print_pdf_sha256"]
                or proof["source_image_jpeg_sha256"] != row["print_jpeg_sha256"]
                or proof["source_image_job_id"] != str(row["source_image_job_id"])
                or proof["source_image_workflow_run"]
                   != str(row["source_image_workflow_run"])
                or proof["unit_xml_id"] != row["source_unit_xml_id"]
                or proof["visible"] != row["preceding_ref_visible"]
                or proof["proposed_cRef"] != row["preceding_ref_cRef"]
                or not proof["printed_reading"].startswith(row["print_reading"] + " (")):
            raise ValueError("Text change lacks precise original printed-page proof")
    return rows


def apply_deltas(root, decisions):
    items = articles(root)
    changed = set()
    records = []
    for row in decisions:
        key = row["source_key"]
        entry = items.get(key)
        if entry is None:
            raise ValueError("Missing historical source article")
        matches = [p for p in entry.iter(T + "p")
                   if p.get(ID) == row["source_unit_xml_id"]]
        if len(matches) != 1:
            raise ValueError("Exact source paragraph identity mismatch")
        paragraph = matches[0]
        if text_digest("".join(paragraph.itertext())) != row["source_unit_text_sha256"]:
            raise ValueError("Original paragraph text digest drift")
        refs = list(paragraph)
        matches = [i for i, child in enumerate(refs)
                   if child.get(ID) == row["source_ref_xml_id"]]
        if len(matches) != 1 or matches[0] == 0:
            raise ValueError("Ambiguous continuation reference or missing predecessor")
        pos = matches[0]
        before_ref, ref = refs[pos-1], refs[pos]
        if (before_ref.tag != T + "ref" or ref.tag != T + "ref"
                or before_ref.get(ID) != row["preceding_ref_xml_id"]
                or before_ref.text != row["preceding_ref_visible"]
                or before_ref.get("cRef") != row["preceding_ref_cRef"]
                or before_ref.tail != row["preceding_ref_tail"]
                or ref.get("type") != "scripture" or len(ref)
                or ref.text != row["original_visible"]
                or ref.get("cRef") != row["original_cRef"]):
            raise ValueError("Original continuation reference text/target/sequence drift")
        original_xml = ET.tostring(entry, encoding="utf-8")
        ref.text = row["corrected_visible"]
        ref.set("cRef", row["corrected_cRef"])
        after_unit_text = "".join(paragraph.itertext())
        if not after_unit_text or text_digest(after_unit_text) == row["source_unit_text_sha256"]:
            raise ValueError("Malformed resulting paragraph")
        # Reverting only the two edited fields MUST exactly restore the prior
        # article serialization, proving that no other markup or text changed.
        ref.text, ref.attrib["cRef"] = row["original_visible"], row["original_cRef"]
        if ET.tostring(entry, encoding="utf-8") != original_xml:
            raise ValueError("Unreviewed structure or visible text altered")
        ref.text, ref.attrib["cRef"] = row["corrected_visible"], row["corrected_cRef"]
        changed.add(key)
        records.append({
            "article_key": key,
            "paragraph_xml_id": row["source_unit_xml_id"],
            "ref_xml_id": row["source_ref_xml_id"],
            "before_visible": row["original_visible"],
            "after_visible": row["corrected_visible"],
            "before_cRef": row["original_cRef"],
            "after_cRef": row["corrected_cRef"],
            "original_paragraph_sha256": row["source_unit_text_sha256"],
            "revised_paragraph_sha256": text_digest(after_unit_text),
            "pdf_sha256": row["print_pdf_sha256"],
            "pdf_page": row["print_pdf_page_1_based"],
            "jpeg_sha256": row["print_jpeg_sha256"],
            "reversible": True,
        })
    return changed, records


def run(source, baseline, previous_report, previous_validator,
        ledger_path, output, report, derived_validator, derived_fidelity):
    if digest(source) != LOCK:
        raise ValueError("Original CrossWire canonical TEI drift")
    previous = load(previous_report)
    baseline_digest = digest(baseline)
    if (previous.get("revised_sha256") != baseline_digest
            or previous.get("canonical_sha256") != LOCK
            or previous.get("scripture_targets_corrected") != 12
            or previous.get("article_count") != 9380
            or previous.get("visible_text_byte_equivalent") is not True
            or previous.get("publication_permitted") is not False):
        raise ValueError("Wrong previously approved 31+6+12 separate baseline")
    validator = load(previous_validator)
    if validator.get("expected_candidate_sha256") != baseline_digest:
        raise ValueError("Previous editorial TEI validator does not match")
    ledger = load(ledger_path)
    decisions = validate_decisions(
        ledger, load(ledger["source_image_ledger"]),
        load(ledger["original_1915_witness_manifest"]))
    root = ET.parse(baseline).getroot()
    a = articles(root)
    if len(a) != 9380:
        raise ValueError("Unexpected historical ISBE article population")
    before = {k: ET.tostring(item, encoding="utf-8") for k, item in a.items()}
    before_ids = [n.get(ID) for item in a.values()
                  for n in item.iter() if n.get(ID)]
    changed, records = apply_deltas(root, decisions)
    if len(records) != len(decisions):
        raise ValueError("Lost or duplicated approved textual delta")
    if any(ET.tostring(item, encoding="utf-8") != before[k]
           for k, item in a.items() if k not in changed):
        raise ValueError("An unrelated article was modified")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)
    after = articles(ET.parse(output).getroot())
    after_ids = [n.get(ID) for item in after.values()
                 for n in item.iter() if n.get(ID)]
    if list(after) != list(a) or after_ids != before_ids:
        raise ValueError("Article ordering or stable XML IDs changed")
    if any(ET.tostring(item, encoding="utf-8") != before[k]
           for k, item in after.items() if k not in changed):
        raise ValueError("Unrelated serialized article changed")
    structure = analyze(output)
    if structure["profile_rule_findings"] or structure["duplicate_xml_ids"]:
        raise ValueError("TEI structural profile failed")
    result = {
        "canonical_sha256": LOCK, "previous_editorial_sha256": baseline_digest,
        "revised_sha256": digest(output), "article_count": len(after),
        "changed_articles": len(changed), "unchanged_articles": len(after)-len(changed),
        "textual_reference_deltas": len(records), "original_xml_ids_preserved": len(after_ids),
        "preceding_editorial_layer_unchanged": True, "original_crosswire_unchanged": True,
        "noncanonical": True, "publication_permitted": False,
        "independent_human_peer_review": False, "changes": records
    }
    derived = {**validator, "expected_candidate_sha256": result["revised_sha256"],
               "noncanonical_review_only": True,
               "review_delta_ledger": str(ledger_path)}
    fidelity = {"candidate_sha256": result["revised_sha256"],
                "article_parity": "PASS", "serialized_profile_check": "PASS",
                "publication_permitted": False, "noncanonical": True,
                "independent_human_peer_review": False,
                "changed_reference_text_and_metadata": len(records)}
    for path, data in ((report, result), (derived_validator, derived),
                       (derived_fidelity, fidelity)):
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", default="cleaned/en/ISBE.xml")
    p.add_argument("--baseline", required=True)
    p.add_argument("--previous-report", required=True)
    p.add_argument("--previous-validator", required=True)
    p.add_argument("--ledger", default="workspace/reviews/1915-approved-reference-text-deltas-v1.json")
    for name in ("output", "report", "derived-validator", "derived-fidelity"):
        p.add_argument("--" + name, required=True)
    args = p.parse_args()
    result = run(args.source, args.baseline, args.previous_report,
                 args.previous_validator, args.ledger, args.output, args.report,
                 args.derived_validator, args.derived_fidelity)
    print(json.dumps({k: v for k, v in result.items() if k != "changes"}, indent=2))
    for row in result["changes"]:
        print("PRINT_TEXT_REFERENCE", row["article_key"], row["ref_xml_id"],
              row["before_visible"], "->", row["after_visible"],
              row["before_cRef"], "->", row["after_cRef"])


if __name__ == "__main__":
    main()
