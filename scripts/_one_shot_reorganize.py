#!/usr/bin/env python3
"""ONE-SHOT structural migration of the ISBE workspace.

Not an ongoing import/normalizer. Move exact tracked Git content unchanged,
retarget all script/test/workflow/doc paths, and create a truthful nonpublished
module *record* (NO fabricated SWORD compiled payload).
Delete this script and its workflow after the migration passes all checks.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_SHA="4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32"
WITNESS_SHA="a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25"
CLEANED_SHA="5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c"

def sh(*args):
    subprocess.run(["git",*args],check=True,cwd=ROOT)

def digest(path):
    h=hashlib.sha256()
    with (ROOT/path).open("rb") as f:
        for block in iter(lambda:f.read(2**20),b""):
            h.update(block)
    return h.hexdigest()

def relocate(old,new):
    source=ROOT/old
    destination=ROOT/new
    if not source.is_file() or destination.exists():
        raise RuntimeError("Unsafe source file rename: "+old+" -> "+new)
    destination.parent.mkdir(parents=True,exist_ok=True)
    sh("mv",old,new)

def dump(path,obj):
    p=ROOT/path
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def main():
    original="sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip"
    cleaned="sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml"
    if (digest(original)!=ORIGINAL_SHA or
        digest("sources/crosswire/isbe-2.2/ISBE.zip")!=ORIGINAL_SHA or
        digest("cleaned/en/ISBE.xml")!=WITNESS_SHA or
        digest(cleaned)!=CLEANED_SHA):
        raise RuntimeError("STOP: source archive, digital witness or corrected TEI drifted")

    # Consolidate the single original source; the two duplicate ZIPs are
    # already the same Git blob. The original acquisition manifest is kept
    # intact under its canonical original-source home.
    relocate("sources/crosswire/isbe-2.2/MANIFEST.json",
             "sources/original/encyclopedias/en/isbe-crosswire-2.2/ACQUISITION_MANIFEST.json")
    sh("rm","sources/crosswire/isbe-2.2/ISBE.zip",
            "sources/crosswire/isbe-2.2/.gitkeep")

    # A reconstructed CrossWire TEI is an INTERMEDIATE, not the approved
    # cleaned editorial master and not a byte-original publisher file.
    relocate("cleaned/en/ISBE.xml",
             "workspace/witnesses/crosswire-2.2/ISBE.xml")
    relocate("cleaned/en/article-index.json",
             "workspace/witnesses/crosswire-2.2/article-index.json")

    # The five printed facsimiles are independent *remote* witnesses: only
    # the SHA-locked volume catalogue is in Git, not the actual PDF scans.
    relocate("sources/print/1915-volume-witnesses.json",
             "workspace/witnesses/print/1915-volume-witnesses.json")

    # Empty language directories were misleading; add actual translated or
    # modernized source files under sources/cleaned only when they exist.
    sh("rm","modern/en/.gitkeep",*[f"translations/{x}/.gitkeep"
                                  for x in ("de","es","fr","it")])

    # Exact, ordered old->new path replacements. Rewrite external doc links
    # only for repository-relative paths: no XML, ZIP, IMP or source data is
    # reserialized, so the original and corrected text SHA remain identical.
    changes=[
      ("sources/crosswire/isbe-2.2/MANIFEST.json",
       "sources/original/encyclopedias/en/isbe-crosswire-2.2/ACQUISITION_MANIFEST.json"),
      ("sources/crosswire/isbe-2.2/",
       "sources/original/encyclopedias/en/isbe-crosswire-2.2/"),
      ("sources/crosswire/isbe-2.2",
       "sources/original/encyclopedias/en/isbe-crosswire-2.2"),
      ("sources/crosswire/",
       "sources/original/encyclopedias/en/isbe-crosswire-2.2/"),
      ("sources/print/1915-volume-witnesses.json",
       "workspace/witnesses/print/1915-volume-witnesses.json"),
      ("sources/print/","workspace/witnesses/print/"),
      ("cleaned/en/ISBE.xml","workspace/witnesses/crosswire-2.2/ISBE.xml"),
      ("cleaned/en/article-index.json","workspace/witnesses/crosswire-2.2/article-index.json"),
      ("cleaned/en/","workspace/witnesses/crosswire-2.2/"),
      ("modern/en/ISBE.xml","sources/cleaned/encyclopedias/en/isbe-modern/ISBE.xml"),
      ("modern/en/","sources/cleaned/encyclopedias/en/isbe-modern/"),
      ("translations/<lang>/ISBE.xml",
       "sources/cleaned/encyclopedias/<lang>/isbe-modern/ISBE.xml"),
      ("translations/{fr,de,es,it}/",
       "sources/cleaned/encyclopedias/{fr,de,es,it}/isbe-modern/"),
    ]
    touched=[]
    repo_files=subprocess.check_output(
      ["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
    for name in repo_files:
        if not name or name in (
            "scripts/_one_shot_reorganize.py",
            ".github/workflows/_one-shot-reorganize-isbe.yml"):
            continue
        p=ROOT/name
        if not p.exists() or not p.is_file() or p.stat().st_size>1500000:
            continue
        if not p.suffix.lower() in (".py",".md",".yml",".yaml",".json",".txt",".toml",".sh"):
            continue
        s=p.read_text(encoding="utf-8")
        new=s
        for old,dest in changes:
            new=new.replace(old,dest)
        if new!=s:
            p.write_text(new,encoding="utf-8")
            touched.append(name)
    # Legacy sources sometimes assemble path components rather than writing
    # a literal repo-relative string; migrate those explicit call sites too.
    special=ROOT/"scripts/audit_1915_prose_evidence.py"
    current=special.read_text(encoding="utf-8")
    previous='root / "sources" / "print" / "1915-volume-witnesses.json"'
    replacement='root / "workspace" / "witnesses" / "print" / "1915-volume-witnesses.json"'
    if current.count(previous)!=1:
        raise RuntimeError("Expected exact old print-metadata composed path once")
    old_xml='root / "cleaned" / "en" / "ISBE.xml"'
    new_xml='root / "workspace" / "witnesses" / "crosswire-2.2" / "ISBE.xml"'
    if current.count(old_xml)!=1:
        raise RuntimeError("Expected composed original TEI path exactly once")
    special.write_text(current.replace(previous,replacement).replace(old_xml,new_xml),
                       encoding="utf-8")

    test=ROOT/"tests/test_persist_1915_cleaned_master.py"
    content=test.read_text(encoding="utf-8")
    obsolete='self.assertNotEqual(master.SOURCE_ZIP,master.ORIGINAL_DIR/"ISBE.zip")'
    correct='self.assertEqual(master.SOURCE_ZIP,master.ORIGINAL_DIR/"ISBE.zip")'
    if content.count(obsolete)!=1:
        raise RuntimeError("Expected old duplicate-original assertion once")
    test.write_text(content.replace(obsolete,correct),encoding="utf-8")

    # Real entity module candidate metadata, NOT a fabricated compiled module.
    dump("modules/isbe-1915/metadata.json",{
      "schema_version":1,
      "id":"isbe-1915",
      "canonical_edition_id":"isbe-orr-1915-crosswire-corrected",
      "category":"encyclopedia",
      "language":"en",
      "planned_sword_id":"BRISBE1915",
      "title":{"en":"International Standard Bible Encyclopedia (1915, corrected working text)"},
      "version":"0.1.0-rc.1",
      "upstreams":[{"provider":"crosswire","module_id":"ISBE","last_integrated_version":"2.2"}],
      "origin":{
        "original_archive":"sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip",
        "original_archive_sha256":ORIGINAL_SHA,
        "canonical_witness":"workspace/witnesses/crosswire-2.2/ISBE.xml",
        "canonical_witness_sha256":WITNESS_SHA,
        "cleaned_master":"sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml",
        "cleaned_master_sha256":CLEANED_SHA,
        "entries":9380
      },
      "quality":{
        "status":"source_validated_not_compiled",
        "native_sword_readback":"not_performed",
        "two_reader_acceptance":"not_performed",
        "original_print_full_collation_certified":False
      },
      "rights":{
        "upstream_declared_license":"Public Domain",
        "redistribution_allowed":False,
        "derivatives_cleared":False,
        "review_status":"pending_original_author_and_eu_france_rights_assessment",
        "tracking_issue":"https://github.com/icfmp/Bible-Resources-ISBE/issues/1"
      },
      "distribution":{
        "payload_present":False,
        "status":"not_built",
        "release_published":False,
        "draft_source_release_only":True
      }
    })
    (ROOT/"modules/README.md").write_text(
      "# Curated SWORD modules\n\n"
      "This follows Bible-Resources' \`modules/<resource-id>/\` layout. "
      "A complete module requires its independently verified \`payload/\` "
      "(\`mods.d/\` and \`modules/\` binary files), metadata, editorial "
      "evidence, reader acceptance and approved rights. **Do not mistake "
      "a module staging directory for a compiled or published SWORD module.**\n\n"
      "- [ISBE 1915](isbe-1915/EDITORIAL.md) is currently a **source-validated "
      "candidate only**, not a built SWORD package. No invented payload "
      "or approved redistribution claim has been committed.\n",
      encoding="utf-8")
    (ROOT/"modules/isbe-1915/EDITORIAL.md").write_text(
      "# ISBE 1915 module staging — not compiled or released\n\n"
      "The complete original source and cleaned historic English TEI are "
      "stored under \`sources/original/encyclopedias/en/isbe-crosswire-2.2/\` "
      "and \`sources/cleaned/encyclopedias/en/isbe-1915/\`. Their SHA and "
      "provenance are pinned in [metadata](metadata.json). The original "
      "CrossWire-faithful TEI and its article index are **intermediate "
      "witnesses** under \`workspace/witnesses/crosswire-2.2/\`.\n\n"
      "CrossWire's existing original zLD module is **not** an editable "
      "or verified native SWORD rebuild of the corrected historical text. "
      "Do not duplicate that upstream compiled payload into this module "
      "directory or relabel it as our corrected 1915 edition.\n\n"
      "Next gates before creating a real \`payload/\`: establish verified "
      "TEI-to-SWORD lexical dictionary compilation, complete 9,380-entry "
      "round-trip with article keys/references/markup, test Xiphos and "
      "another independent reader, and resolve the source-specific "
      "[redistribution rights issue #1]"
      "(https://github.com/icfmp/Bible-Resources-ISBE/issues/1). "
      "No public release authorization follows from the draft TEI source "
      "release. Modernization belongs to a separate future source edition.\n",
      encoding="utf-8")
    (ROOT/"workspace/witnesses/README.md").write_text(
      "# Intermediate source witnesses\n\n"
      "\`crosswire-2.2/ISBE.xml\` and \`article-index.json\` are a "
      "**source-faithful reconstructed digital witness**, *not* the "
      "historical edited or modern English source, and not a publisher "
      "original*. The TEI bytes remain pinned to SHA-256 "
      f"\`{WITNESS_SHA}\`.\n\n"
      "\`print/1915-volume-witnesses.json\` records the SHA-locked five "
      "original printed PDF witnesses used for research. Those PDF files "
      "are **not present in Git**; their text layers are not a reliable "
      "critical transcription. Original source ZIP and edited master "
      "are stored under \`sources/original/\` and \`sources/cleaned/\`.\n",
      encoding="utf-8")
    (ROOT/"sources/original/encyclopedias/en/isbe-crosswire-2.2/README.md").write_text(
      "# Original CrossWire ISBE 2.2\n\n"
      "The unchanged upstream SWORD original is \`ISBE.zip\`, "
      "SHA-256 \`"+ORIGINAL_SHA+"\`. The exact original acquisition "
      "metadata is retained in \`ACQUISITION_MANIFEST.json\`; source "
      "identity is also recorded in \`PROVENANCE.json\`. This directory "
      "does not contain our corrected TEI. All changes are recorded "
      "separately under \`sources/cleaned/\`.\n",
      encoding="utf-8")

    if any(digest(path)!=value for path,value in (
      (original,ORIGINAL_SHA),
      ("workspace/witnesses/crosswire-2.2/ISBE.xml",WITNESS_SHA),
      (cleaned,CLEANED_SHA))):
        raise RuntimeError("A source blob was changed by the move")
    if not (ROOT/"workspace/witnesses/crosswire-2.2/article-index.json").is_file():
        raise RuntimeError("Article index lost")
    forbidden=("cleaned/en/","sources/crosswire/",
               "sources/print/","modern/en/")
    remaining=[]
    for name in subprocess.check_output(
            ["git","ls-files","-z"],cwd=ROOT).decode().split("\0"):
        if not name:continue
        p=ROOT/name
        if not p.exists() or not p.is_file() or p.stat().st_size>1500000:continue
        if not p.suffix in (".py",".md",".yml",".yaml",".json",".txt"):continue
        if name.startswith("scripts/_one_shot") or name.startswith(".github/workflows/_one-shot"):continue
        content=p.read_text(encoding="utf-8")
        for old in forbidden:
            if old in content:
                remaining.append((name,old))
    if remaining:
        raise RuntimeError("Obsolete source paths remain: "+str(remaining[:30]))
    print("MIGRATED",len(touched),"tracked documentation/script/test/metadata files")
    print("EXACT SOURCE SHAS:",ORIGINAL_SHA,WITNESS_SHA,CLEANED_SHA)

if __name__=="__main__":
    main()
