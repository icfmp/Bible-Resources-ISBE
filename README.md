# Bible Resources — ISBE

A reproducible, multilingual editorial workspace for the historical **International Standard Bible Encyclopedia** (James Orr edition), using the CrossWire SWORD ISBE 2.2 module as the digital starting point.

## Current state

- The original CrossWire 2.2 ZIP is preserved unchanged at `sources/crosswire/isbe-2.2/ISBE.zip` with a SHA-256 provenance manifest.
- The complete `mod2imp` export is preserved at `workspace/exports/isbe-2.2.imp`.
- **9,380 entries** have been rebuilt into one TEI XML edition: `cleaned/en/ISBE.xml`.
- `cleaned/en/article-index.json` contains a stable identifier and source-content checksum for each entry.
- `workspace/reports/tei-reconstruction.json` records content integrity and unresolved cross-references.
- Modern English and translations **have not been started**.

## Layout

```text
sources/crosswire/isbe-2.2/      Immutable original SWORD distribution and manifest
workspace/exports/              Verbatim intermediate SWORD IMP export (retained)
cleaned/en/                     Canonical, faithful, indexed TEI reference
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

Reconstruction uses the versioned script `scripts/rebuild_tei.py`, and the `Reconstruct ISBE TEI corpus` GitHub Action. To reproduce locally, install SWORD's `mod2imp` utility, unpack the original ZIP into a private directory and run:

```bash
SWORD_PATH=/path/to/unpacked/sword mod2imp ISBE > workspace/exports/isbe-2.2.imp
python3 scripts/rebuild_tei.py \
  --input workspace/exports/isbe-2.2.imp \
  --output cleaned/en/ISBE.xml \
  --index cleaned/en/article-index.json \
  --report workspace/reports/tei-reconstruction.json
```

The process fails if XML cannot be parsed, article keys are duplicated, the entry count changes unexpectedly, or any extracted article's text differs after serialization.

## Editorial boundaries

The cleaned TEI is a **transcription of the CrossWire digital source**, not a critically verified edition of the printed volumes. It is never modernized in place. All language modernization happens separately under `modern/en/`; translations are derived from a pinned modern-English revision. Preserve semantic IDs across revisions so only altered text units need translation review.

The initial report lists 1,344 unresolved internal-link occurrences and four original title variants. Keep these as open review findings rather than inventing targets or silently correcting historical content.

See [TEI conventions](docs/article-format.md), [workflow](docs/workflow.md), and [source policy](docs/source-policy.md).
