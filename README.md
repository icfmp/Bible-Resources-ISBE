# Bible Resources — ISBE

A reproducible, multilingual editorial workspace for the historical **International Standard Bible Encyclopedia** (James Orr edition), using the CrossWire SWORD ISBE 2.2 module as the digital starting point.

## Current state

- The original CrossWire 2.2 ZIP is preserved unchanged at `sources/crosswire/isbe-2.2/ISBE.zip` with a SHA-256 provenance manifest.
- The complete `mod2imp` export is preserved at `workspace/exports/isbe-2.2.imp`.
- **9,380 entries** have been rebuilt into one TEI XML edition: `cleaned/en/ISBE.xml`.
- `cleaned/en/article-index.json` contains a stable identifier and source-content checksum for each entry.
- `workspace/reports/tei-reconstruction.json` records content integrity and unresolved cross-references.
- Modern English and translations **have not been started**.
- The [ISBE TEI P5 structure profile](docs/tei-structure-profile.md) defines the **target** for article structure and biblical references, informed by the source-first standards used in `icfmp/Bible-Resources`.
- The [full-corpus structure inventory](workspace/reports/tei-structure-inventory.json) confirms all 9,380 article XML trees are in the TEI namespace, but also records **93,162 legacy `osisRef` attributes**, **9,380 untyped index labels** and **27 bibliography headings requiring structural review**. The master has **not yet passed an official TEI P5 schema validation**; tracked in [issue #3](https://github.com/icfmp/Bible-Resources-ISBE/issues/3).

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

The CrossWire source contains **6,079 encyclopedia reference occurrences**. The latest verified reconstruction has **5,906 valid internal TEI links**, **29 source references correctly represented as bibliography headings**, and **144 unresolved references converted to non-clickable source-reference segments**. **There are zero active broken `ISBE:` links in the canonical TEI.** From the original 1,344 problematic references, **1,171 have become valid links**, 29 were reclassified as headings, and 144 remain unlinked because no destination can currently be justified; 6 of the resolved links are explicitly documented as less-precise article-level fallbacks. The unlinked references span 130 distinct original targets; they preserve their full visible text, source `xml:id` and original `ISBE:…` string in the `n` attribute. The exact per-occurrence disposition is recorded in `workspace/reports/tei-reconstruction.json`, editorial decisions in `workspace/reviews/accepted-title-aliases.json`, and review candidates in `workspace/reviews/unresolved-links.json` and `workspace/reviews/link-contexts.json`. All 9,380 entries and 22,670,955 source-text characters remain intact. These are integrity-checked TEI results, not independent runtime verification in SWORD readers.

See the [normative ISBE TEI target profile](docs/tei-structure-profile.md), [current format and IDs](docs/article-format.md), [workflow](docs/workflow.md), and [source policy](docs/source-policy.md).
