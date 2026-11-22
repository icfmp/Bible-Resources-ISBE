#!/usr/bin/env python3
"""Verify official TEI P5 schema provenance and the compiled Schematron SVRL.

The official RELAX NG check itself is run separately with jing. This script
checks the independent Schematron result, confirms its negative-control
fixture detected a real rule violation, and records audit metadata.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

SCH = "{http://purl.oclc.org/dsdl/schematron}"
SVRL = "{http://purl.oclc.org/dsdl/svrl}"


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def summarize_svrl(path):
    root = ET.parse(path).getroot()
    if root.tag != SVRL + "schematron-output":
        raise ValueError("Not an ISO SVRL Schematron validation result")
    def elements(local_name):
        return root.findall(".//" + SVRL + local_name)
    return {
        "active_patterns": len(elements("active-pattern")),
        "fired_rules": len(elements("fired-rule")),
        "failed_assertions": len(elements("failed-assert")),
        "successful_reports": len(elements("successful-report")),
    }


def check(*, manifest_path, candidate_path, rng_path, schematron_path,
          svrl_path, negative_svrl_path, source_report_path, output_path):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    specs = manifest["official_tei_p5"]
    if specs["version"] != "4.12.0":
        raise ValueError("Unexpected TEI P5 schema version")
    if digest(rng_path) != specs["relax_ng"]["sha256"]:
        raise ValueError("Official RELAX NG bytes differ from pinned SHA-256")
    if digest(schematron_path) != specs["schematron"]["sha256"]:
        raise ValueError("Official Schematron bytes differ from pinned SHA-256")
    candidate_sha = digest(candidate_path)
    fidelity = json.loads(Path(source_report_path).read_text(encoding="utf-8"))
    if fidelity.get("candidate_sha256") != candidate_sha:
        raise ValueError("Official validation input differs from fidelity candidate")
    if fidelity.get("article_parity") != "PASS" or \
            fidelity.get("serialized_profile_check") != "PASS":
        raise ValueError("Source fidelity gates did not pass")
    schema = ET.parse(schematron_path).getroot()
    if schema.tag != SCH + "schema" or schema.get("queryBinding") != "xslt2":
        raise ValueError("Unexpected TEI Schematron dialect")
    patterns = len(schema.findall(SCH + "pattern"))
    if patterns != specs["schematron"]["expected_patterns"]:
        raise ValueError("Official Schematron pattern count changed")
    positive = summarize_svrl(svrl_path)
    negative = summarize_svrl(negative_svrl_path)
    if positive["active_patterns"] < 1 or positive["fired_rules"] < 1:
        raise ValueError("Schematron did not execute any active rules")
    if positive["failed_assertions"] or positive["successful_reports"]:
        raise ValueError("Official Schematron reported candidate violations")
    if negative["failed_assertions"] + negative["successful_reports"] < 1:
        raise ValueError("Official Schematron did not reject invalid control")
    report = {
        "source_fidelity": "PASS",
        "candidate_sha256": candidate_sha,
        "official_tei_p5_version": specs["version"],
        "official_rng_url": specs["relax_ng"]["url"],
        "official_rng_sha256": specs["relax_ng"]["sha256"],
        "official_rng": "PASS (jing run before this check)",
        "official_schematron_url": specs["schematron"]["url"],
        "official_schematron_sha256": specs["schematron"]["sha256"],
        "official_schematron_patterns": patterns,
        "official_schematron": "PASS",
        "official_schematron_svrl": positive,
        "official_schematron_negative_control": negative,
        "negative_control": "PASS",
        "historical_witness_and_redistribution": "NOT_VERIFIED",
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ("manifest", "candidate", "rng", "schematron",
                "svrl", "negative-svrl", "source-report", "output"):
        p.add_argument("--" + arg, required=True, type=Path)
    a = p.parse_args()
    result = check(
        manifest_path=a.manifest, candidate_path=a.candidate,
        rng_path=a.rng, schematron_path=a.schematron,
        svrl_path=a.svrl, negative_svrl_path=a.negative_svrl,
        source_report_path=a.source_report, output_path=a.output,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
