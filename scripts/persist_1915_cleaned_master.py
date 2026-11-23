#!/usr/bin/env python3
"""Rebuild and retain the original ISBE 2.2 ZIP and validated 1915 edited TEI.

Inputs and outputs are different artifacts. The original ZIP, source-faithful
canonical TEI and reproducibility evidence are *never* overwritten.
No SWORD publication or redistribution licence is claimed.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

SOURCE_ZIP = Path("sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip")
SOURCE_MANIFEST = Path("sources/original/encyclopedias/en/isbe-crosswire-2.2/ACQUISITION_MANIFEST.json")
CANONICAL = Path("workspace/witnesses/crosswire-2.2/ISBE.xml")
INDEX = Path("workspace/witnesses/crosswire-2.2/article-index.json")
ORIGINAL_DIR = Path("sources/original/encyclopedias/en/isbe-crosswire-2.2")
CLEANED_DIR = Path("sources/cleaned/encyclopedias/en/isbe-1915")
TMP = Path("workspace/tmp/isbe-retained-master")
CANONICAL_SHA = "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
ORIGINAL_ZIP_SHA = "4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32"
EXPECTED_CLEANED_SHA = "5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c"

def digest(path):
    h=sha256()
    with Path(path).open("rb") as f:
        while chunk:=f.read(1024*1024):
            h.update(chunk)
    return h.hexdigest()

def check_source():
    manifest=json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if (manifest.get("archive_sha256")!=ORIGINAL_ZIP_SHA or
        manifest.get("archive_bytes")!=SOURCE_ZIP.stat().st_size or
        digest(SOURCE_ZIP)!=ORIGINAL_ZIP_SHA or
        digest(CANONICAL)!=CANONICAL_SHA):
        raise ValueError("Unverified or modified immutable CrossWire source")
    return manifest

def run(script,*args):
    print("RUN",script,flush=True)
    # The existing evidence-locked builders use 'from scripts.*' imports;
    # invoke these via the same -m module entrypoint as their verified CI.
    script_path=Path(script)
    module_builders={
        "apply_1915_scripture_targets.py",
        "apply_1915_reference_text_deltas.py",
        "apply_display_verified_scripture_targets.py",
        "apply_1915_low_overlap_prose_deltas.py",
        "apply_1915_additional_prose_deltas.py",
        "apply_1915_printed_apocrypha_refs.py",
    }
    command=([sys.executable,"-m","scripts."+script_path.stem]
             if script_path.name in module_builders else [sys.executable,script])
    subprocess.run([*command,*map(str,args)],check=True)

def stages():
    # This is the same ordered, original-source-locked chain used in
    # validate-1915-textual-reference-deltas.yml, with the same original
    # evidence ledgers, full-corpus assertions and negative controls.
    run("scripts/finalize_1915_recovery.py",
        "--output", TMP/"approved-base.xml",
        "--report", TMP/"base-report.json",
        "--validator-manifest", TMP/"base-validator.json",
        "--fidelity-report", TMP/"base-fidelity.json")
    run("scripts/apply_1915_print_deltas.py",
        "--source",CANONICAL,
        "--baseline",TMP/"approved-base.xml",
        "--baseline-report",TMP/"base-report.json",
        "--baseline-manifest",TMP/"base-validator.json",
        "--ledger","workspace/reviews/1915-approved-print-deltas-v1.json",
        "--output",TMP/"previous-editorial.xml",
        "--report",TMP/"previous-report.json",
        "--derived-manifest",TMP/"previous-validator.json",
        "--fidelity",TMP/"previous-fidelity.json")
    run("scripts/apply_1915_scripture_targets.py",
        "--baseline",TMP/"previous-editorial.xml",
        "--previous-report",TMP/"previous-report.json",
        "--previous-validator",TMP/"previous-validator.json",
        "--output",TMP/"target-corrected.xml",
        "--report",TMP/"target-corrections.json",
        "--derived-validator",TMP/"target-validator.json",
        "--derived-fidelity",TMP/"target-fidelity.json")
    run("scripts/apply_1915_reference_text_deltas.py",
        "--baseline",TMP/"target-corrected.xml",
        "--previous-report",TMP/"target-corrections.json",
        "--previous-validator",TMP/"target-validator.json",
        "--output",TMP/"reference-text.xml",
        "--report",TMP/"reference-text-report.json",
        "--derived-validator",TMP/"reference-text-validator.json",
        "--derived-fidelity",TMP/"reference-text-fidelity.json")
    run("scripts/apply_display_verified_scripture_targets.py",
        "--baseline",TMP/"reference-text.xml",
        "--prior-report",TMP/"reference-text-report.json",
        "--prior-validator",TMP/"reference-text-validator.json",
        "--output",TMP/"taanach.xml",
        "--report",TMP/"taanach-report.json",
        "--derived-validator",TMP/"taanach-validator.json",
        "--derived-fidelity",TMP/"taanach-fidelity.json")
    run("scripts/apply_1915_low_overlap_prose_deltas.py",
        "--baseline",TMP/"taanach.xml",
        "--prior-report",TMP/"taanach-report.json",
        "--prior-validator",TMP/"taanach-validator.json",
        "--output",TMP/"prose.xml",
        "--report",TMP/"prose-report.json",
        "--derived-validator",TMP/"prose-validator.json",
        "--derived-fidelity",TMP/"prose-fidelity.json")
    run("scripts/apply_1915_additional_prose_deltas.py",
        "--source",CANONICAL,
        "--prior",TMP/"prose.xml",
        "--prior-report",TMP/"prose-report.json",
        "--prior-validator",TMP/"prose-validator.json",
        "--ledger","workspace/reviews/1915-additional-exact-print-deltas-v1.json",
        "--output",TMP/"additional-prose.xml",
        "--report",TMP/"additional-prose-report.json",
        "--derived-manifest",TMP/"additional-prose-validator.json",
        "--derived-fidelity",TMP/"additional-prose-fidelity.json")
    run("scripts/apply_1915_printed_apocrypha_refs.py",
        "--source",CANONICAL,
        "--prior",TMP/"additional-prose.xml",
        "--prior-report",TMP/"additional-prose-report.json",
        "--prior-validator",TMP/"additional-prose-validator.json",
        "--ledger","workspace/reviews/1915-gainsay-additions-esther-reference-v1.json",
        "--output",TMP/"final.xml",
        "--report",TMP/"final-report.json",
        "--derived-validator",TMP/"final-validator.json",
        "--derived-fidelity",TMP/"final-fidelity.json")
    if digest(TMP/"final.xml")!=EXPECTED_CLEANED_SHA:
        raise ValueError("Verified edited TEI SHA mismatch; do not publish a stale or changed source")
    run("scripts/validate_official_tei_p5.py",
        "--candidate",TMP/"final.xml",
        "--source-report",TMP/"final-fidelity.json",
        "--manifest",TMP/"final-validator.json",
        "--output",TMP/"official-validation.json")
    official=json.loads((TMP/"official-validation.json").read_text(encoding="utf-8"))
    fidelity=json.loads((TMP/"final-fidelity.json").read_text(encoding="utf-8"))
    if (official.get("candidate_sha256")!=EXPECTED_CLEANED_SHA or
        official.get("official_rng")!="PASS (jing run before this check)" or
        official.get("official_schematron")!="PASS" or
        official.get("source_fidelity")!="PASS" or
        fidelity.get("candidate_sha256")!=EXPECTED_CLEANED_SHA or
        fidelity.get("article_parity")!="PASS" or
        fidelity.get("publication_permitted") is not False):
        raise ValueError("Full editorial source was not independently validated")
    return official

def write_json(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def persist(source_manifest,validation):
    ORIGINAL_DIR.mkdir(parents=True,exist_ok=True)
    CLEANED_DIR.mkdir(parents=True,exist_ok=True)
    original=ORIGINAL_DIR/"ISBE.zip"
    edited=CLEANED_DIR/"ISBE.xml"
    if SOURCE_ZIP.resolve() != original.resolve():
        shutil.copyfile(SOURCE_ZIP,original)
    shutil.copyfile(TMP/"final.xml",edited)
    if digest(original)!=ORIGINAL_ZIP_SHA or digest(edited)!=EXPECTED_CLEANED_SHA:
        raise ValueError("Retained files differ from independently verified inputs")
    write_json(ORIGINAL_DIR/"PROVENANCE.json",{
        "format":"SWORD raw module ZIP","work":"International Standard Bible Encyclopedia",
        "module":"ISBE","module_version":"2.2","source":"CrossWire original unchanged",
        "source_path":SOURCE_ZIP.as_posix(),
        "original_url":source_manifest["download_url"],
        "bytes":source_manifest["archive_bytes"],
        "sha256":ORIGINAL_ZIP_SHA,
        "source_manifest_path":SOURCE_MANIFEST.as_posix(),
        "redistribution_review":"PENDING_INDEPENDENT_REVIEW",
        "edition_reconstruction_is_not_original":True
    })
    write_json(CLEANED_DIR/"CLEANUP_MANIFEST.json",{
        "kind":"working_cleaned_editorial_TEI_not_released",
        "resource":"ISBE","historical_print_edition":"Orr/Howard-Severance 1915",
        "original_module_sha256":ORIGINAL_ZIP_SHA,
        "source_faithful_canonical_path":CANONICAL.as_posix(),
        "source_faithful_canonical_sha256":CANONICAL_SHA,
        "source_article_index_path":INDEX.as_posix(),
        "source_article_index_sha256":digest(INDEX),
        "cleaned_file":"ISBE.xml",
        "cleaned_bytes":edited.stat().st_size,
        "cleaned_sha256":EXPECTED_CLEANED_SHA,
        "article_count":9380,
        "stable_article_ids":"Preserved from original source-faithful TEI",
        "approved_source_text_restorations":31,
        "editorial_evidence":[
            "workspace/reviews/1915-second-pass-visual-approval-v1.json",
            "workspace/reviews/1915-approved-print-deltas-v1.json",
            "workspace/reviews/1915-gainsay-additions-esther-reference-v1.json",
            "workspace/reviews/1915-additional-exact-print-deltas-v1.json",
            "workspace/reviews/1915-approved-low-overlap-prose-deltas-v1.json",
            "workspace/reviews/1915-approved-reference-text-deltas-v1.json",
        ],
        "rebuild_script":"scripts/persist_1915_cleaned_master.py",
        "official_tei_p5":"4.12.0",
        "schema_validation":"PASS",
        "fidelity_gate":"PASS: source-backed deltas only",
        "original_print_full_collation_certified":False,
        "modernized":False,
        "publication_permitted":False,
        "rights_redistribution_cleared":False,
        "source_crosswire_unchanged":True
    })
    return original,edited

def verify_saved():
    manifest=json.loads((CLEANED_DIR/"CLEANUP_MANIFEST.json").read_text(encoding="utf-8"))
    provenance=json.loads((ORIGINAL_DIR/"PROVENANCE.json").read_text(encoding="utf-8"))
    if (digest(ORIGINAL_DIR/"ISBE.zip")!=ORIGINAL_ZIP_SHA or
        digest(CLEANED_DIR/"ISBE.xml")!=EXPECTED_CLEANED_SHA or
        manifest.get("cleaned_sha256")!=EXPECTED_CLEANED_SHA or
        manifest.get("original_module_sha256")!=ORIGINAL_ZIP_SHA or
        provenance.get("sha256")!=ORIGINAL_ZIP_SHA or
        manifest.get("publication_permitted") is not False or
        manifest.get("rights_redistribution_cleared") is not False):
        raise ValueError("Staged sources or source evidence drifted")
    return True

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only",action="store_true")
    parser.add_argument("--assemble",action="store_true")
    args=parser.parse_args()
    if args.verify_only:
        check_source();verify_saved();print("PASS: exact original and corrected master SHA-256 locks");return
    if not args.assemble:
        parser.error("Supply --assemble or --verify-only")
    manifest=check_source()
    TMP.mkdir(parents=True,exist_ok=True)
    validation=stages()
    original,edited=persist(manifest,validation)
    verify_saved()
    print(json.dumps({"original":str(original),"original_sha256":digest(original),
                      "cleaned":str(edited),"cleaned_sha256":digest(edited),
                      "rights_redistribution_cleared":False,"published":False},indent=2))
if __name__=="__main__":
    main()
