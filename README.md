# Bible Resources — ISBE

A reproducible, multilingual editorial workspace for the historical **International Standard Bible Encyclopedia** (James Orr edition), using the CrossWire SWORD ISBE 2.2 module as the digital starting point.

## Current state

**Source storage (Bible-Resources layout):** the preserved CrossWire 2.2 original resides at `sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip` (duplicated only for compatibility with the existing `sources/crosswire/` path); the reproducibly corrected **historical** English TEI lives at `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml`. The original `cleaned/en/ISBE.xml` remains a byte-locked **source-faithful CrossWire witness**, *not* the historical cleaned editorial master. See [source layout](sources/README.md) and [edition evidence](sources/cleaned/encyclopedias/en/isbe-1915/editorial/README.md). Edited source remains a working asset; pending rights review blocks any distribution/release.


- The exact original CrossWire ISBE 2.2 ZIP is preserved unchanged at `sources/crosswire/isbe-2.2/ISBE.zip`, with a SHA-256 provenance manifest.
- The original `mod2imp` export is preserved at `workspace/exports/isbe-2.2.imp`.
- **9,380 entries** form the canonical, fully typed **TEI P5 4.12.0** working master at `cleaned/en/ISBE.xml`.
- The canonical master is the exact source-faithful candidate SHA-256 `a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25`; per-article text, original 185,657 XML IDs, 93,162 Bible references and 5,906 active internal links are proved unchanged by the migration.
- **31 source-empty entries have been recovered in a separate, non-published 1915 editorial TEI**: 20 substantive articles and 11 redirects, with original printed-page references, source-image digests, source-locked editorial decisions, and a second AI-assisted visual reading. The canonical source-faithful `cleaned/en/ISBE.xml` remains unchanged. See [recovered entries](docs/1915-recovered-entries.md) and [merged PR #42](https://github.com/icfmp/Bible-Resources-ISBE/pull/42).
- Both pinned official TEI P5 RELAX NG and ISO Schematron validation (120 patterns, 175,075 fired rules, zero violations) passed on serialized XML. Mandatory project-profile checks and negative controls are enforced by CI.
- `cleaned/en/article-index.json` keeps the original stable source-key, ID and content checksums. Source reconstruction diagnostics and separate schema/parity evidence are in `workspace/reports/`.
- Modern English and translations **have not been started**. The 31 recovered entries have received a documented second **AI-assisted** facsimile reading, **not independent human scholarly peer review**. Full-corpus print comparison, copyright/redistribution clearance and native SWORD/two-reader release testing remain open. TEI validity is not publication authorization.
- Details: [TEI P5 profile](docs/tei-structure-profile.md), [source-locked migration proof](docs/tei-p5-candidate-migration.md), [issue #3](https://github.com/icfmp/Bible-Resources-ISBE/issues/3).

## Layout

```text
sources/crosswire/isbe-2.2/      Immutable original SWORD distribution and manifest
workspace/exports/              Verbatim intermediate SWORD IMP export (retained)
cleaned/en/                     Canonical, CrossWire-faithful TEI witness (immutable)
sources/original/               Original CrossWire ZIP with provenance
sources/cleaned/                Complete corrected historical ISBE TEI master
modern/en/                      Future modern-English TEI editorial master
translations/{fr,de,es,it}/      Future TEI translations with matching IDs
workspace/reports/              Import and quality-control reports
workspace/changes/              Future revision-diff reports
workspace/reviews/              Editorial decision records
scripts/                        Reusable import and validation utilities
tests/                          Automated tests
docs/                           Repository-wide working rules
```

## Rebuild

The official reproducible route begins with the **preserved SWORD IMP**, not the current normalized master. The workflow `.github/workflows/rebuild-tei.yml` rebuilds a temporary legacy TEI witness using `scripts/rebuild_tei.py`, checks its source SHA-256, runs `scripts/normalize_tei_p5.py` into a separate candidate, proves every original article/node/reference and identifier, then checks the exact candidate SHA-256. Only after passing the strict ISBE profile **and both official TEI schema gates** is the canonical master replaced.

The official schema validator, shared between candidate, canonical CI and rebuild, is `scripts/validate_official_tei_p5.py`; the locked upstream bytes and toolchain are documented in `workspace/changes/tei-p5-candidate-v1.json`. Use the [reproducible migration commands](docs/tei-p5-candidate-migration.md). **Never invoke `scripts/rebuild_tei.py` with `--output cleaned/en/ISBE.xml` directly:** its output is the historical intermediate, not the canonical P5 master.

The ongoing `validate.yml` and structural inventory workflow fail on source/format drift, missing identifiers, damaged references or an unreviewed change to canonical XML. The original source and the signed-off transformed bytes remain independently verifiable.

## Editorial boundaries

The legacy `cleaned/en/ISBE.xml` is a **source-faithful transcription of CrossWire** for original parity tests. The *historical corrected working source* is separately maintained and SHA-locked under `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml` and is likewise never modernized in place. All language modernization happens separately under `modern/en/`; translations are derived from a pinned modern-English revision. Preserve semantic IDs across revisions so only altered text units need translation review.

The CrossWire source contains **6,079 encyclopedia reference occurrences**. The latest verified reconstruction has **5,906 valid internal TEI links**, **29 source references represented by bibliography structures (27 headings and 2 lead paragraphs)**, and **144 unresolved references converted to non-clickable source-reference segments**. **There are zero active broken `ISBE:` links in the canonical TEI.** From the original 1,344 problematic references, **1,171 have become valid links**, 29 were reclassified as bibliography labels (27 headings, 2 paragraph leads), and 144 remain unlinked because no destination can currently be justified; 6 of the resolved links are explicitly documented as less-precise article-level fallbacks. The unlinked references span 130 distinct original targets; they preserve their full visible text, source `xml:id` and original `ISBE:…` string in the `n` attribute. The exact per-occurrence disposition is recorded in `workspace/reports/tei-reconstruction.json`, editorial decisions in `workspace/reviews/accepted-title-aliases.json`, and review candidates in `workspace/reviews/unresolved-links.json` and `workspace/reviews/link-contexts.json`. All 9,380 entries and 22,670,955 source-text characters remain intact. These are integrity-checked TEI results, not independent runtime verification in SWORD readers.

See the [normative ISBE TEI target profile](docs/tei-structure-profile.md), [current format and IDs](docs/article-format.md), [workflow](docs/workflow.md), and [source policy](docs/source-policy.md).
