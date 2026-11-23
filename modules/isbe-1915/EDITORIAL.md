# BRISBE1915 — compiled SWORD dictionary candidate (not published)

**Current status:** A real ZIP-compressed SWORD zLD dictionary has been built and independently read back through libSWORD, but is **not** a public release, does **not** have an installed `payload/` in this public repository, and has **not** passed separate Xiphos + BibleTime GUI acceptance. See [source verification](SOURCE_VALIDATION.json) and [build #45256959636](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45256959636).

## Source identity

- Original unmodified CrossWire 2.2: `sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip`, SHA-256 `4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32`.
- Corrected historical **English** TEI P5: `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml`, SHA-256 `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.
- Unique curated SWORD identity: `BRISBE1915`, deliberately different from upstream CrossWire `ISBE` so installed modules do not overwrite each other.
- SWORD config: `ModDrv=zLD`, `CompressType=ZIP`, `SourceType=TEI`, `Encoding=UTF-8`, `Version=0.1.0`.
- Exact importer TEI SHA-256 `6d5262d69ca13724a9a9a3bcd8cd23e957aefddfeeb0be20a7ce59e2d97fa745` at [successful source-and-native build #45256959636](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45256959636).

## Build and verification

The generic `scripts/export_tei_dictionary_for_sword.py` translates the reviewed historical TEI P5 `div type="entry"` wrappers into SWORD's supported `entryFree` dictionary format without modifying the corrected source master. Native SWORD's `tei2mod` compiles the result, and the generic `scripts/validate_sword_dictionary_roundtrip.py` compares the **entire** `mod2imp` native readback against the exact imported source.

**Result:** 9,380 source keys, 9,380 native keys, **zero missing, extra, malformed, text-different, or XML-structure-different entries** in the raw native SWORD readback. This is a genuine corrected-edition binary, **not** the old CrossWire 2.2 binary relabeled as our module. The compiled candidate tarball SHA-256 is `e7d07e75d58ef0ce158dc39290cf942d096253364657227d5ff885793a67bf37`. The historic original remains unchanged.

**Link adapter (explicit transformation of compiled copy, not source):**

- 5,919 internal TEI `#xml:id` references become native SWORD `self:<original article key>` targets. Their exact original selectors are preserved in `corresp`.
- 93,164 biblical reference elements acquire a SWORD `osisRef` equal to their original source `cRef`; original reference markup and displayed text remain unchanged.
- 80 links to a *section* within another article now address its parent article, without guaranteed precise intra-article scroll targeting. This loss is documented; source selectors remain intact.
- 29 nested `div` elements are retained without destructive flattening; actual GUI rendering/interaction with these structures still needs review.
- The diatheke CLI rendered four representative articles in `plain`, `HTML` and `HTMLHREF`. The general `HTML` filter produced no anchors; SWORD's purpose-built `HTMLHREF` filter rendered **63 anchors** (41 AARON, 8 ABIDE, 10 GAINSAY, 4 ZEBIDAH), confirming generated hyperlink markup. **Actual GUI click-navigation in Xiphos or BibleTime is still not verified** ([run #45259095383](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45259095383)).
- Historical 1915 Greek/Hebrew text missing in the source remains missing. The original full printed work has **not** been critically collated.

## Remaining publication gates

The candidate requires independent **Xiphos and second-reader interactive navigation/rendering tests**, especially Greek/Hebrew display, hyperlinks and nested sections, before anyone may call it reader-approved. The official native full-corpus readback is a technical prerequisite, not a substitute for actual GUI tests.

The [copyright/provenance issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1) is independently open. CrossWire's own module declares Public Domain, but French/EU separately attributed 1915 articles and the exact original digitization layers remain under assessment. Existing source-only GitHub release is an unpublished draft; the compiled SWORD module is **not yet authorized for public distribution**. A private GitHub release draft is a preparation artifact, **not** release publication.

For an eventual real `modules/isbe-1915/payload/` and public SWORD release, record actual module ZIP byte and metadata checksums, full native readback, Xiphos/BibleTime evidence, exact rights determination, owner approval and reproducible build/rollback. Avoid weakening these gates merely to make CI green.
