#!/usr/bin/env python3
"""Apply exact, image-attested 1915 prose corrections to a NEW editorial TEI.

This is NOT a full article collation or a source edit. The immutable CrossWire
canonical witness and each preceding noncanonical editorial stage remain intact.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.audit_tei_structure import analyze
from scripts.audit_1915_article_ocr_word_counts import LOCK

T = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"
ET.register_namespace("", "http://www.tei-c.org/ns/1.0")


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def text_digest(text):
    return sha256(text.encode("utf-8")).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def entries(root):
    if root.tag != T + "TEI":
        raise ValueError("Not a TEI P5 witness")
    body = root.find(f"./{T}text/{T}body")
    if body is None or len(body) != 9380:
        raise ValueError("Unexpected canonical article inventory")
    result = {}
    for article in body:
        key = article.get("n")
        if not key or key in result or not article.get(ID):
            raise ValueError("Missing or duplicated source article ID")
        result[key] = article
    return result


def validate_decisions(spec, evidence, manifest):
    if (spec.get("schema_version") != 1
            or spec.get("canonical_tei_sha256") != LOCK
            or spec.get("evidence_ledger")
                != "workspace/reviews/1915-low-overlap-prose-image-spotchecks-v2.json"
            or spec.get("previous_layer")
                != "1915_display_only_target_corrected_noncanonical"
            or spec.get("source_faithful_canonical_modified") is not False
            or spec.get("full_article_collation_certified") is not False
            or spec.get("independent_human_peer_review") is not False
            or spec.get("publication_permitted") is not False):
        raise ValueError("Unrecognized or falsely certified editorial layer")
    if (evidence.get("schema_version") != 1
            or evidence.get("canonical_tei_sha256") != LOCK
            or evidence.get("full_article_collation_completed") is not False
            or evidence.get("redistribution_authorized") is not False
            or manifest.get("canonical_tei_sha256") != LOCK):
        raise ValueError("Print/source evidence is untrusted")
    volumes = {v["volume"]: v for v in manifest.get("volumes", [])}
    image_cases = {r["source_key"]: r for r in evidence.get("entries", [])}
    if len(volumes) != 5 or len(image_cases) != 13:
        raise ValueError("Expected the five print sources and thirteen visual observations")
    decisions = spec.get("decisions")
    if (not isinstance(decisions, list) or len(decisions) != 8
            or len({r.get("source_key") for r in decisions}) != len(decisions)):
        raise ValueError("Eight independent, uniquely located editorial decisions required")
    for row in decisions:
        key = row.get("source_key")
        proof = image_cases.get(key)
        if (proof is None or row.get("operation") != "replace_text_span"
                or row.get("approved_for_separate_1915_tei") is not True
                or row.get("source_article_xml_id") != proof["source_article_xml_id"]
                or row.get("print_volume") != proof["volume"]
                or row.get("pdf_page_1_based") != proof["pdf_page_1_based"]
                or row.get("printed_folio") != proof["printed_folio"]
                or row.get("original_pdf_sha256") != proof["original_pdf_sha256"]
                or row.get("research_jpeg_sha256") != proof["research_jpeg_sha256"]
                or row["original_pdf_sha256"]
                    != volumes[proof["volume"]]["pdf_sha256"]
                or not isinstance(row.get("source_unit_xml_id"), str)
                or not row["source_unit_xml_id"].startswith(
                    proof["source_article_xml_id"] + "-n")
                or not isinstance(row.get("rationale"), str)
                or len(row["rationale"]) < 45
                or proof["full_article_prose_verified"] is not False
                or proof["correction_authorized"] is not False):
            raise ValueError("Proposed correction lacks exact original image provenance")
        matches = [f for f in proof["fragments"]
                   if f["digital_source_exact"] == row.get("original_visible")
                   and f["printed_visible_reading"] == row.get("corrected_visible")
                   and f["classification"] == row.get("review_classification")]
        if len(matches) != 1 or row["original_visible"] == row["corrected_visible"]:
            raise ValueError("Exact printed/digital phrase pair was not visually attested")
    return decisions


def apply_operations(root, decisions):
    articles = entries(root)
    records = []
    changed = set()
    for row in decisions:
        key = row["source_key"]
        article = articles.get(key)
        if article is None or article.get(ID) != row["source_article_xml_id"]:
            raise ValueError("Source article identity mismatch")
        paragraphs = [p for p in article.iter(T + "p")
                      if p.get(ID) == row["source_unit_xml_id"]]
        if len(paragraphs) != 1:
            raise ValueError("Missing or ambiguous original paragraph identity")
        paragraph = paragraphs[0]
        original = row["original_visible"]
        corrected = row["corrected_visible"]
        old_text = "".join(paragraph.itertext())
        if old_text.count(original) != 1:
            raise ValueError("Exact digital reading absent or duplicated in paragraph")
        slots = []
        for node in paragraph.iter():
            if node.text and original in node.text:
                slots.append((node, "text"))
            if node is not paragraph and node.tail and original in node.tail:
                slots.append((node, "tail"))
        if len(slots) != 1:
            raise ValueError("Print correction crosses markup or multiple text slots")
        node, field = slots[0]
        old_xml = ET.tostring(article, encoding="utf-8")
        value = getattr(node, field)
        if value.count(original) != 1:
            raise ValueError("Digital reading not unique inside XML slot")
        setattr(node, field, value.replace(original, corrected, 1))
        revised_text = "".join(paragraph.itertext())
        if (revised_text.count(corrected) != 1
                or revised_text == old_text):
            raise ValueError("Reviewed replacement did not preserve exact source context")
        # One-operation reversibility, including all markup and metadata.
        setattr(node, field, value)
        if ET.tostring(article, encoding="utf-8") != old_xml:
            raise ValueError("Non-reversible editorial mutation")
        setattr(node, field, value.replace(original, corrected, 1))
        records.append({
            "source_key": key,
            "source_article_xml_id": row["source_article_xml_id"],
            "source_unit_xml_id": row["source_unit_xml_id"],
            "original_visible": original, "corrected_visible": corrected,
            "original_unit_sha256": text_digest(old_text),
            "revised_unit_sha256": text_digest(revised_text),
            "pdf_page_1_based": row["pdf_page_1_based"],
            "print_pdf_sha256": row["original_pdf_sha256"],
            "print_jpeg_sha256": row["research_jpeg_sha256"],
            "reversible": True,
        })
        changed.add(key)
    return changed, records


def run(source, baseline, prior_report, prior_validator, ledger, output,
        report, derived_validator, derived_fidelity):
    source, baseline, output = map(Path, (source, baseline, output))
    if len({p.resolve() for p in (source, baseline, output)}) != 3:
        raise ValueError("Source, prior edition and derived edition must be distinct")
    if digest(source) != LOCK:
        raise ValueError("Canonical immutable source drift")
    prior = load(prior_report)
    prior_sha = digest(baseline)
    if (prior.get("revised_sha256") != prior_sha
            or prior.get("article_count") != 9380
            or prior.get("navigation_target_changes") != 1
            or prior.get("visible_text_byte_equivalent") is not True
            or prior.get("publication_permitted") is not False):
        raise ValueError("Previous distinct 1915 editorial stage is not verified")
    old_manifest = load(prior_validator)
    if (old_manifest.get("expected_candidate_sha256") != prior_sha
            or old_manifest.get("noncanonical_review_only") is not True):
        raise ValueError("Previous editorial source lock does not match")
    spec = load(ledger)
    decisions = validate_decisions(
        spec, load(spec["evidence_ledger"]),
        load("workspace/witnesses/print/1915-volume-witnesses.json"))
    root = ET.parse(baseline).getroot()
    articles = entries(root)
    old_articles = {key: ET.tostring(article, encoding="utf-8")
                    for key, article in articles.items()}
    old_ids = [node.get(ID) for article in articles.values()
               for node in article.iter() if node.get(ID)]
    changed, changes = apply_operations(root, decisions)
    if any(ET.tostring(article, encoding="utf-8") != old_articles[key]
           for key, article in articles.items() if key not in changed):
        raise ValueError("Unreviewed in-memory source change")
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)
    revised = entries(ET.parse(output).getroot())
    ids_after = [node.get(ID) for article in revised.values()
                 for node in article.iter() if node.get(ID)]
    if list(revised) != list(articles) or ids_after != old_ids:
        raise ValueError("Original article order or XML IDs changed")
    if any(ET.tostring(article, encoding="utf-8") != old_articles[key]
           for key, article in revised.items() if key not in changed):
        raise ValueError("Unreviewed serialized source change")
    check = analyze(output)
    if check["profile_rule_findings"] or check["duplicate_xml_ids"]:
        raise ValueError("Strict TEI structure validation failed")
    result = {
        "canonical_sha256": LOCK, "previous_editorial_sha256": prior_sha,
        "revised_sha256": digest(output), "article_count": len(revised),
        "corrected_prose_fragments": len(changes),
        "corrected_articles": len(changed),
        "unchanged_articles": len(revised) - len(changed),
        "original_xml_ids_preserved": len(ids_after),
        "original_crosswire_unchanged": True,
        "full_article_collation_certified": False,
        "independent_human_peer_review": False,
        "publication_permitted": False,
        "changes": changes,
    }
    derived = {**old_manifest,
               "expected_candidate_sha256": result["revised_sha256"],
               "noncanonical_review_only": True,
               "review_delta_ledger": str(ledger)}
    fidelity = {
        "candidate_sha256": result["revised_sha256"],
        "article_parity": "PASS", "serialized_profile_check": "PASS",
        "publication_permitted": False, "noncanonical": True,
        "independent_human_peer_review": False,
        "changed_print_attested_prose_spans": len(changes),
    }
    for path, data in ((report, result), (derived_validator, derived),
                       (derived_fidelity, fidelity)):
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", default="workspace/witnesses/crosswire-2.2/ISBE.xml")
    p.add_argument("--ledger", default=
                   "workspace/reviews/1915-approved-low-overlap-prose-deltas-v1.json")
    for name in ("baseline", "prior-report", "prior-validator", "output",
                 "report", "derived-validator", "derived-fidelity"):
        p.add_argument("--" + name, required=True)
    a = p.parse_args()
    result = run(a.source, a.baseline, a.prior_report, a.prior_validator,
                 a.ledger, a.output, a.report, a.derived_validator,
                 a.derived_fidelity)
    print(json.dumps({k: v for k, v in result.items() if k != "changes"},
                     indent=2))


if __name__ == "__main__":
    main()
