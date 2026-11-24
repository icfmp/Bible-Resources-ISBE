# BRISBE1915 — publicly released corrected historical SWORD dictionary

**Current status (2026-11-24):** The corrected ISBE 1915 module is **publicly released as [0.1.0](https://github.com/icfmp/Bible-Resources-ISBE/releases/tag/isbe-1915-v0.1.0)**. The 9,380-entry native binary, source ZIP and checksums were independently verified after public publication. The repository keeps its original and edited TEI masters, but intentionally does **not** duplicate the 11 MB release binary under `modules/isbe-1915/payload/`. Full Xiphos Book View, Scripture destination navigation and complete historical printed-edition collation are **not certified**. The project owner explicitly accepted publication with the documented source and reader scope. See [source verification](SOURCE_VALIDATION.json) and [build #45256959636](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45256959636).

## Source identity

- Original unmodified CrossWire 2.2: `sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip`, SHA-256 `4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32`.
- Corrected historical **English** TEI P5: `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml`, SHA-256 `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.
- Unique curated SWORD identity: `BRISBE1915`, deliberately different from upstream CrossWire `ISBE` so installed modules do not overwrite each other.
- SWORD config: `ModDrv=zLD`, `CompressType=ZIP`, `SourceType=TEI`, `Encoding=UTF-8`, `Version=0.1.0`.
- **Latest archived SWORD importer TEI SHA-256** `bdac245cad329fdff8039d0374815ff7086b8a5f8055118f1250461b9d5f17ec` (source-locked explicit work-ID links), validated and privately staged in [run #45346863700](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45346863700). The earlier adapter SHA `6d5262d69ca13724a9a9a3bcd8cd23e957aefddfeeb0be20a7ce59e2d97fa745` remains a documented predecessor.

## Build and verification

The generic `scripts/export_tei_dictionary_for_sword.py` translates the reviewed historical TEI P5 `div type="entry"` wrappers into SWORD's supported `entryFree` dictionary format without modifying the corrected source master. Native SWORD's `tei2mod` compiles the result, and the generic `scripts/validate_sword_dictionary_roundtrip.py` compares the **entire** `mod2imp` native readback against the exact imported source.

**Result:** 9,380 source keys, 9,380 native keys, **zero missing, extra, malformed, text-different, or XML-structure-different entries** in the raw native SWORD readback. This is a genuine corrected-edition binary, **not** the old CrossWire 2.2 binary relabeled as our module. The **latest archived unpublished draft candidate** is `BRISBE1915-native-workid-draft.tar.gz`, SHA-256 `6b7edccc0f27fbcf71595597ddd8794a5db72acd3952fb03e1e4e569e7acf3a5` (see [`DRAFT_EVIDENCE.md`](../../release/drafts/isbe-1915-v0.1.0-rc.1/DRAFT_EVIDENCE.md)). The earlier asset `BRISBE1915-native-candidate-NOT-FOR-PUBLICATION.tar.gz` with SHA-256 `6993937ffcdba83348dc0f0cc510613a42f85d3e4c5423f19355a1cf65ee9c9b` is also retained in the draft for historical comparison; **only the new asset contains the corrected SWORD work-ID links**. This is not a public release. The historic original remains unchanged.

**Link adapter (explicit transformation of compiled copy, not source):**

- 5,919 internal TEI `#xml:id` references become native SWORD `BRISBE1915:<original article key>` targets. Their exact original selectors are preserved in `corresp`.
- 93,164 biblical reference elements acquire a SWORD `osisRef` equal to their original source `cRef`; original reference markup and displayed text remain unchanged.
- 80 links to a *section* within another article now address its parent article, without guaranteed precise intra-article scroll targeting. This loss is documented; source selectors remain intact.
- 29 nested `div` elements are retained without destructive flattening; actual GUI rendering/interaction with these structures still needs review.
- The diatheke CLI rendered four representative articles in `plain`, `HTML` and `HTMLHREF`. The general `HTML` filter produced no anchors; SWORD's purpose-built `HTMLHREF` filter rendered **63 anchors** (41 AARON, 8 ABIDE, 10 GAINSAY, 4 ZEBIDAH), confirming generated hyperlink markup. **Actual GUI click-navigation in Xiphos or BibleTime is still not verified** ([run #45259095383](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45259095383)).
- Historical 1915 Greek/Hebrew text missing in the source remains missing. The original full printed work has **not** been critically collated.

## Remaining publication gates

Independent **exact AARON headword lookup and article display** have been visually verified in [Xiphos](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45279693011) and [BibleTime](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45280079561) (second attempt; [GUI screenshot artifact](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45280079561/artifacts/14869951086)). BibleTime uses the isolated standard `~/.sword` module root. This is **not** full reader acceptance: actual clicked hyperlinks, section-level navigation, Greek/Hebrew display and nested structures still require review. See [issue #79](https://github.com/icfmp/Bible-Resources-ISBE/issues/79). The official native full-corpus readback is a technical prerequisite, not a substitute for actual GUI tests.

**Owner's public-domain distribution decision (2026-11-24):** CrossWire declares the module `Public Domain`, and the project owner accepts that designation together with the historical 1915 edition as sufficient for ISBE distribution planning. Further independent legal review is **not a gate**. This documents the owner's chosen basis, not a claim that separate contributor-by-contributor jurisdictional research was completed. See [provenance issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1) and [publication gates](../../release/drafts/isbe-1915-v0.1.0-rc.1/PUBLICATION_GATES.md). The **unpublished GitHub release draft still holds both corrected TEI and the compiled SWORD candidate**. The public repository does not contain a `payload/` directory; the draft's status reflects unfinished reader and editorial acceptance, not a rights prohibition.

For an eventual real `modules/isbe-1915/payload/` and public SWORD release, record actual module ZIP byte and metadata checksums, full native readback, Xiphos/BibleTime evidence, the documented maintainer public-domain decision, owner approval of the release and reproducible build/rollback. Avoid weakening these gates merely to make CI green.

## Corrected real-reader navigation and release candidate (2026-11-24)

The [source-preserving PR #95](https://github.com/icfmp/Bible-Resources-ISBE/pull/95) corrected 5,919 native SWORD crosslinks from `self:<key>` to `BRISBE1915:<key>`, preserving the exact original `#xml:id` selector in `corresp`. The compiled HTMLHREF layer now renders a resolvable `sword://BRISBE1915/ARK+OF+BULRUSHES` link; 9,380 native records are identical in visible text and XML structure to the adapted source.

Actual [Xiphos/BibleTime GUI clicks](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45344977265) show the correct linked article `ARK OF BULRUSHES` in **Xiphos's dictionary Viewer** and **BibleTime's Mag pane**. Xiphos's separate *Book View* still shows “The URL can't be shown”. The earlier separate Scripture-reference navigation limitations also remain. Neither behavior justifies changing the original historical source.

[PR #96](https://github.com/icfmp/Bible-Resources-ISBE/pull/96) rebuilt and stored the **new** 11,731,030-byte compiled candidate in the same GitHub release draft with its checksums and reports, without publishing it. The owner has accepted the CrossWire Public Domain basis; outstanding gates are editorial/reader acceptance and explicit approval of actual release artifacts, not a new rights audit.

## Verified public release (2026-11-24)

[Public GitHub release 0.1.0](https://github.com/icfmp/Bible-Resources-ISBE/releases/tag/isbe-1915-v0.1.0), published `2026-11-24T07:47:40Z` via [successful release run #45350683511](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45350683511), contains **exactly four** approved downloadable assets. The recommended, standard SWORD installation ZIP `BRISBE1915-0.1.0-SWORD.zip` is **11,734,786 bytes**, SHA-256 `9d41edc06c3ebd916f3aaa5b3b12f2a495b069b36f2cb26b8e0dab4bdac15df7`. The equivalent tarball SHA-256 is `6b7edccc0f27fbcf71595597ddd8794a5db72acd3952fb03e1e4e569e7acf3a5`. The source ZIP SHA-256 is `52ac2b3db91b49adab94db2fd6d6d009bf836efe11e993516c33434bb5c56365`.

This release uses **only the corrected real SWORD `BRISBE1915:` crosslinks**. The old draft candidate with `self:` URLs remains in the **separate, unpublished historical draft** as provenance, not in the public download. Publication does not retroactively certify the upstream transcription as a complete photographic/print collation. See `release/published/isbe-1915-v0.1.0/PUBLICATION_EVIDENCE.json` and `workspace/reviews/isbe-1915-publication-editorial-assessment.md`.
