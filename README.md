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

Reconstruction uses the versioned script `scripts/rebuild_tei.py`, and the `Reconstruct ISBE TEI corpus` GitHub Action. The reproducible raw SWORD IMP export is already preserved. A routine rebuild requires only Python:

```bash
python3 scripts/rebuild_tei.py \
  --accepted-aliases workspace/reviews/accepted-title-aliases.json \
  --input workspace/exports/isbe-2.2.imp \
  --output cleaned/en/ISBE.xml \
  --index cleaned/en/article-index.json \
  --report workspace/reports/tei-reconstruction.json
```

The process fails if XML cannot be parsed, article keys or XML IDs are duplicated, the entry count changes unexpectedly, any extracted article text differs after serialization, or any rewritten internal target is missing. The total number of original SWORD encyclopedia links is also checked.

## Editorial boundaries

The cleaned TEI is a **transcription of the CrossWire digital source**, not a critically verified edition of the printed volumes. It is never modernized in place. All language modernization happens separately under `modern/en/`; translations are derived from a pinned modern-English revision. Preserve semantic IDs across revisions so only altered text units need translation review.

The CrossWire source contains **6,079 encyclopedia reference occurrences**. The latest verified reconstruction has **5,898 valid TEI fragment destinations**, **29 source links reclassified as bibliography headings**, and **152 unresolved occurrences across 137 distinct source targets**. Of the 1,344 references initially without a working reconstructed destination, **1,163 are now navigable** and **29 were identified as incorrectly encoded headings**. Of the navigable links, **6 intentionally use an article-level fallback where the requested numbered subsection could not be verified**; they are explicitly marked as imprecise in the review data and reconstruction report. All original target strings remain recoverable in `n` on repaired links or reclassified headings. Evidence is recorded in `workspace/reports/tei-reconstruction.json`, editorial decisions in `workspace/reviews/accepted-title-aliases.json`, and remaining cases in `workspace/reviews/unresolved-links.json` and `workspace/reviews/link-contexts.json`. These are TEI integrity results, not an independent runtime test of CrossWire readers.

See [TEI conventions](docs/article-format.md), [workflow](docs/workflow.md), and [source policy](docs/source-policy.md).
