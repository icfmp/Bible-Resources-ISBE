# Bible Resources — ISBE

Source-first editorial workspace for the **International Standard Bible Encyclopedia**, James Orr's historical 1915 edition, starting from the CrossWire SWORD 2.2 module.

## Definitive directory layout

```text
sources/
  original/encyclopedias/en/isbe-crosswire-2.2/
    ISBE.zip                      Immutable CrossWire 2.2 SWORD ZIP
    PROVENANCE.json               Source identity and provenance
    ACQUISITION_MANIFEST.json     Original download/rights declaration
  cleaned/encyclopedias/en/isbe-1915/
    ISBE.xml                      Corrected historical English TEI P5 master
    CLEANUP_MANIFEST.json         Original/output SHA and validation evidence
    editorial/README.md           Reversible, source-attested corrections

modules/
  isbe-1915/metadata.json         Planned curated SWORD module, NOT compiled
  isbe-1915/EDITORIAL.md          Module-building and rights gates

workspace/
  witnesses/crosswire-2.2/
    ISBE.xml                      Unedited CrossWire digital-text witness (TEI)
    article-index.json            Stable original keys/IDs/word checksums
  witnesses/print/
    1915-volume-witnesses.json   Metadata and hashes of five printed PDF scans
  exports/isbe-2.2.imp            Reproducible SWORD source IMP extraction
  reviews/                        Editorial evidence and unresolved candidates
  changes/                        Historical source migration proof
  reports/                        Fidelity and structure validation

scripts/                            Generic reconstruction, audits and validation
tests/                              Regression and negative controls
docs/                               Historical editorial/source documentation
release/drafts/                     Source-only GitHub release draft evidence
```

There is deliberately **no root `cleaned/`, `modern/`, `translations/`, or duplicate `sources/crosswire/`**: the original CrossWire ZIP is preserved once, and all other witnesses are explicitly distinguished from edited sources.

## Source identities and validation

- **Original SWORD ZIP:** 9,987,447 bytes, SHA-256 `4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32`.
- **Reconstructed digital CrossWire TEI witness:** SHA-256 `a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25`; 9,380 entries, 185,657 stable original XML IDs, 93,162 Bible references, and 5,906 active internal article links.
- **Historically corrected TEI:** 37,062,851 bytes, SHA-256 `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`. The corrections include 31 recovered CrossWire-empty entries and separately documented historical source-backed text/cross-reference deltas. The preserved CrossWire witness and original stay unchanged.
- **Standards:** TEI P5 4.12.0, pinned official RELAX NG and ISO Schematron, negative controls and reproducible article/identifier checks. **A valid TEI file is not automatically a literal print facsimile.** Some original-language Greek and Hebrew material remains absent, with audit decisions explicitly retained.

### Source checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/persist_1915_cleaned_master.py --verify-only
python3 scripts/persist_1915_cleaned_master.py --assemble
```

The full `--assemble` workflow requires the official TEI P5 schema toolchain (including `jing`). The permanent [source-retention CI](.github/workflows/validate-retained-isbe-sources.yml) reconstructs and byte-compares the historical cleaned source from pinned evidence. The standard [CI checks](.github/workflows/validate.yml) verify the digital witness and index.

## Modern English, translations and BRSI

The future modern English edition **will be a distinct real resource**, e.g. `sources/cleaned/encyclopedias/en/isbe-modern/ISBE.xml`, with its own revision and validation. Future translations likewise belong under `sources/cleaned/encyclopedias/<language>/isbe-modern/`, not empty placeholder directories. They must preserve or explicitly map stable article IDs, so [BRSI](https://github.com/icfmp/Bible-Resources-Semantic-Index) can link biblical identities independently of presentation language.

Modernization must derive from **`sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml`**, not from the uncorrected technical CrossWire witness. See [workflows](docs/workflow.md) and [TEI structure profile](docs/tei-structure-profile.md).

## Publication and rights

The initial source-only historical TEI candidate exists as an **unpublished GitHub release draft**, not a public released source archive or compiled SWORD module. The `modules/isbe-1915/` directory currently has only explicit staging metadata: there is no corrected compiled `payload/` or Xiphos/two-reader acceptance. CrossWire labels its upstream distribution *Public Domain*, but exact digitization/translation rights and named 1915 contributors in France/EU still require independent review under [issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1). The wider editorial/print review remains [issue #9](https://github.com/icfmp/Bible-Resources-ISBE/issues/9). No publication is authorized by source retention or technical CI.
