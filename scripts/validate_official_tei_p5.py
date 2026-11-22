#!/usr/bin/env python3
"""Validate a serialized ISBE candidate against the pinned official TEI P5 release.

Requires curl, jing, Java and Saxon HE (Ubuntu: apt install jing).
Uses the exact schema bytes and compiler commit recorded in the source lock.
Runs both positive corpus checks and negative controls; fails closed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from check_tei_p5_svrl import check as record_official_check

INVALID_RNG = """<?xml version="1.0" encoding="utf-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader><fileDesc><titleStmt><title>Invalid control</title></titleStmt>
    <publicationStmt><p>Test</p></publicationStmt>
    <sourceDesc><p>Test</p></sourceDesc></fileDesc></teiHeader>
  <text><body><p type="not-valid-on-p">Bad</p></body></text>
</TEI>
"""

INVALID_SCHEMATRON = """<?xml version="1.0" encoding="utf-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:lang="en">
  <teiHeader><fileDesc><titleStmt><title>Invalid control</title></titleStmt>
    <publicationStmt><p>Test</p></publicationStmt>
    <sourceDesc><p>Test</p></sourceDesc></fileDesc></teiHeader>
  <text><body><div type="entry" xml:id="isbe-control" n="CONTROL">
    <head type="index">CONTROL</head>
    <p><ref target="#isbe-control" cRef="Bible:Gen.1.1">Gen 1:1</ref></p>
  </div></body></text>
</TEI>
"""

def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as inp:
        for chunk in iter(lambda: inp.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def command(*args):
    print("Running:", " ".join(str(x) for x in args), flush=True)
    subprocess.run([str(x) for x in args], check=True)


def get(url, dest, expected=None):
    command("curl", "--fail", "--location", "--silent", "--show-error",
            "--retry", "2", url, "-o", dest)
    if expected and digest(dest) != expected:
        raise ValueError(f"Downloaded schema SHA-256 mismatch: {url}")


def saxon(source, sheet, output):
    command("java", "-cp", "/usr/share/java/Saxon-HE.jar",
            "net.sf.saxon.Transform", "-s:" + str(source),
            "-xsl:" + str(sheet), "-o:" + str(output))


def validate(candidate, fidelity_report, manifest_file, output):
    candidate, fidelity_report, manifest_file, output = map(
        Path, (candidate, fidelity_report, manifest_file, output))
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    spec = manifest["official_tei_p5"]
    if spec["version"] != "4.12.0":
        raise ValueError("Unapproved TEI version")
    if digest(candidate) != manifest["expected_candidate_sha256"]:
        raise ValueError("Candidate bytes differ from pinned validated digest")
    compiler = spec["compiler"]
    commit = compiler["commit"]
    if not (len(commit) == 40 and all(c in "0123456789abcdef" for c in commit)):
        raise ValueError("Compiler must be pinned to a full commit")
    with tempfile.TemporaryDirectory(prefix="isbe-tei-p5-") as folder:
        temp = Path(folder)
        rng = temp / "tei_all.rng"
        sch = temp / "tei_all.isosch"
        get(spec["relax_ng"]["url"], rng, spec["relax_ng"]["sha256"])
        get(spec["schematron"]["url"], sch, spec["schematron"]["sha256"])
        command("jing", rng, candidate)
        invalid_rng = temp / "invalid-rng.xml"
        invalid_rng.write_text(INVALID_RNG, encoding="utf-8")
        negative = subprocess.run(["jing", str(rng), str(invalid_rng)])
        if negative.returncode == 0:
            raise ValueError("Pinned RELAX NG did not reject invalid paragraph")
        print("Official RELAX NG: corpus PASS and invalid control rejected", flush=True)
        iso = temp / "iso"
        iso.mkdir()
        names = compiler["files"]
        expected_names = [
            "iso_dsdl_include.xsl", "iso_abstract_expand.xsl",
            "iso_svrl_for_xslt2.xsl", "iso_schematron_skeleton_for_saxon.xsl",
        ]
        if names != expected_names:
            raise ValueError("Unexpected Schematron compiler sources")
        for name in names:
            url = ("https://raw.githubusercontent.com/Schematron/schematron/" +
                   commit + "/trunk/schematron/code/" + name)
            get(url, iso / name)
        included = iso / "included.sch"
        expanded = iso / "expanded.sch"
        compiled = iso / "validator.xsl"
        result = iso / "result.svrl"
        bad_result = iso / "negative.svrl"
        saxon(sch, iso / names[0], included)
        saxon(included, iso / names[1], expanded)
        saxon(expanded, iso / names[2], compiled)
        saxon(candidate, compiled, result)
        invalid_sch = iso / "invalid-sch.xml"
        invalid_sch.write_text(INVALID_SCHEMATRON, encoding="utf-8")
        saxon(invalid_sch, compiled, bad_result)
        output.parent.mkdir(parents=True, exist_ok=True)
        summary = record_official_check(
            manifest_path=manifest_file, candidate_path=candidate,
            rng_path=rng, schematron_path=sch,
            svrl_path=result, negative_svrl_path=bad_result,
            source_report_path=fidelity_report, output_path=output,
        )
        summary["relax_ng_negative_control"] = "PASS"
        output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--source-report", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    validate(a.candidate, a.source_report, a.manifest, a.output)


if __name__ == "__main__":
    main()
