# BRISBE1915 — corrected historical ISBE SWORD edition

## Current state (2026-11-24)

**Published:** [ISBE 1915 0.1.0](https://github.com/icfmp/Bible-Resources-ISBE/releases/tag/isbe-1915-v0.1.0). This is a real, independently compiled SWORD dictionary with **9,380 entries**; it is **not** the original CrossWire 2.2 binary renamed. Public archives were checked after publication. The release assets are authoritative; this repository deliberately does not commit an 11 MB duplicate under `modules/isbe-1915/payload/`.

The separate older release-candidate draft is **unpublished** and retained only as provenance. Its obsolete first SWORD binary with `self:` links is **not** in the published 0.1.0 assets.

The module has **not** yet been imported into the central Bible Resources Pages/SWORD catalogue. This fact is distinct from successful publication in this repository.

## Source identity and preservation

| Record | Value |
| --- | --- |
| Original digital source | CrossWire ISBE 2.2 (`sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip`) |
| Original ZIP SHA-256 | `4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32` |
| Corrected historical master | `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml` (TEI P5, English) |
| Corrected TEI SHA-256 | `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c` |
| Exact native SWORD adapter input SHA-256 | `bdac245cad329fdff8039d0374815ff7086b8a5f8055118f1250461b9d5f17ec` |
| Compiled module ID | `BRISBE1915` (does not overwrite upstream `ISBE`) |
| Format | `ModDrv=zLD`, ZIP compression, TEI, UTF-8, version `0.1.0` |

Historical corrections are documented in the cleaned-source editorial ledger. The original archive and source witness remain unchanged. The adapter changes only the **compiled copy**, not the corrected TEI master.

## Native and reader acceptance

- The generic `scripts/export_tei_dictionary_for_sword.py` exports reviewed TEI article wrappers into SWORD `entryFree` entries. Native `tei2mod` compilation followed by `mod2imp` readback verified **9,380/9,380** keys, with no missing/extra articles and **zero Unicode or XML-structure differences** from the adapted source.
- **5,919** internal dictionary links target `BRISBE1915:<article key>` (rather than invalid `self:` identifiers). Original `#xml:id` targets are preserved as `corresp`.
- **93,164** Bible reference elements expose native `osisRef` targets without altering their original `cRef` fields or printed labels.
- **80** intra-article section references are resolved at their *containing article*, without guaranteed scrolling to the section. Exact source identifiers remain preserved.
- **29** nested `div` elements remain structurally present; selected numbered sections were visually checked.
- Real Xiphos/BibleTime samples display Greek in `CHORBE`, pointed Hebrew in `AMNON`, and numbered nested sections in `ELKOSHITE`. Dictionary hyperlink clicks `ARK → ARK OF BULRUSHES` reach the appropriate Viewer/Mag pane.

**Known limitations:** Xiphos's separate Book View may show “The URL can't be shown”; Scripture-reference navigation in both readers can be incomplete. Source-present scripts and structure are verified within the stated test scope, **not** fully reconstructed against original printed glyphs. The edition has **not** been exhaustively collated against all five 1915 printed volumes. Continue reader diagnosis at [issue #101](https://github.com/icfmp/Bible-Resources-ISBE/issues/101), without editing historical Scripture references to disguise client behavior.

Primary evidence: [native CI](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45347402944), [real-reader link clicks](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45344977265), [six GUI screenshots](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45349111541), and [editorial assessment](../../workspace/reviews/isbe-1915-publication-editorial-assessment.md).

## Immutable public distribution

| Download | Exact SHA-256 |
| --- | --- |
| [`BRISBE1915-0.1.0-SWORD.zip`](https://github.com/icfmp/Bible-Resources-ISBE/releases/download/isbe-1915-v0.1.0/BRISBE1915-0.1.0-SWORD.zip) | `9d41edc06c3ebd916f3aaa5b3b12f2a495b069b36f2cb26b8e0dab4bdac15df7` |
| [`BRISBE1915-0.1.0-SWORD.tar.gz`](https://github.com/icfmp/Bible-Resources-ISBE/releases/download/isbe-1915-v0.1.0/BRISBE1915-0.1.0-SWORD.tar.gz) | `6b7edccc0f27fbcf71595597ddd8794a5db72acd3952fb03e1e4e569e7acf3a5` |
| [`BRISBE1915-0.1.0-source.zip`](https://github.com/icfmp/Bible-Resources-ISBE/releases/download/isbe-1915-v0.1.0/BRISBE1915-0.1.0-source.zip) | `52ac2b3db91b49adab94db2fd6d6d009bf836efe11e993516c33434bb5c56365` |

There is also a checksum text file in the same release. All four public assets and their sizes are recorded in the [publication receipt](../../release/published/isbe-1915-v0.1.0/PUBLICATION_EVIDENCE.json). Never silently replace published 0.1.0 bytes; future changes require separately documented and validated versions.

**Distribution basis:** CrossWire declares its ISBE 2.2 module *Public Domain*, and the project owner accepted that designation along with the historical 1915 edition as sufficient for this publication. This records the decision, without asserting a contributor-by-contributor jurisdictional legal audit. It is not an outstanding release gate.

The legacy draft evidence remains in [release/drafts](../../release/drafts/isbe-1915-v0.1.0-rc.1/), and is historical context rather than the current module state.
