# ISBE 1915 v0.1.0-rc.1 — publication readiness

**Status: unpublished draft; technical and editorial acceptance remain open.** The source-pinned draft contains the corrected TEI and compiled SWORD candidate. This is a state report, not a claim that the binary has passed final reader acceptance.

## Maintainer decision on public-domain distribution — 2026-11-24

The project owner expressly accepts the **Public Domain** status declared by CrossWire for ISBE 2.2 and the historical **1915** edition as a sufficient basis to proceed. **No further legal/copyright investigation or independent jurisdiction-by-jurisdiction clearance is required as an ISBE publication gate.** This ends the project's discretionary additional rights review, previously imposed by the maintainer's assistant rather than by the owner.

Evidence retained for provenance: CrossWire's module configuration declares `DistributionLicense=Public Domain`, and the 1915 historical edition is identified and preserved. The owner acceptance is a **project distribution decision**, not a representation that an independent France/EU contributor-by-contributor legal review was performed. Keep that distinction in metadata. Never rewrite source provenance or rights statements silently.

## Verified technical preparation

- [x] Immutable original CrossWire 2.2 ZIP with SHA-256 and upstream provenance.
- [x] Corrected source-locked TEI P5, **9,380 entries**, validated by official schemas and reproducible from preserved evidence.
- [x] Native `BRISBE1915` SWORD zLD ZIP compilation and complete `mod2imp` readback: 9,380 keys, no missing/extra, zero Unicode text or XML structure mismatches.
- [x] Source-to-SWORD mapping audited: **5,919** internal dictionary references and **93,164** biblical references, with **80** documented losses of intra-article scroll precision; original selectors retained.
- [x] Exact **AARON** headword and corresponding article visibly opened independently in Xiphos and BibleTime ([Xiphos evidence](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45279693011); [BibleTime evidence](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45280079561)).
- [x] Actual verse-reference click attempts captured in both readers ([PR #89](https://github.com/icfmp/Bible-Resources-ISBE/pull/89), [PR #92](https://github.com/icfmp/Bible-Resources-ISBE/pull/92)), with **unsuccessful end-to-end Bible passage-body navigation** transparently documented.
- [x] Original and corrected historical sources are preserved separately. The compiled candidate remains in an **unpublished** GitHub release draft, not in a public SWORD catalogue or installed `modules/isbe-1915/payload/`.
- [x] Newly corrected **work-ID SWORD binary** privately archived as `BRISBE1915-native-workid-draft.tar.gz` with pinned SHA-256 `6b7edccc0f27fbcf71595597ddd8794a5db72acd3952fb03e1e4e569e7acf3a5`, while older draft binary remains available for comparison. Verified by [draft run #45346863700](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45346863700).

## Remaining work before release

- [x] Review actual article-to-article hyperlink navigation in independent SWORD readers: `ARK` → `ARK OF BULRUSHES` opens the destination in BibleTime Mag and Xiphos dictionary Viewer; **Xiphos Book View still fails**, requiring separate acceptance or resolution (PR #95, run #45344977265).
- [ ] Resolve or explicitly accept and document Xiphos Book View dictionary link failure and client-specific Scripture link limitations (Xiphos `passagestudy.jsp`, BibleTime new tab shows Genesis 1 body while requested reference is Exodus 6:20).
- [ ] Inspect source-attested Greek/Hebrew characters, nested divisions, paragraph layout and the 80 section-navigation limitations; do not change historical text to conceal reader defects.
- [ ] Complete enough editorial review of the historical edition under [#9](https://github.com/icfmp/Bible-Resources-ISBE/issues/9) to accurately describe its quality and limitations; do not claim full printed-1915 collation.
- [ ] Obtain project-owner approval of **the actual release** once its content, limitations and artifacts are ready. Public publication remains a separate action, not an automatic consequence of accepting the public-domain basis.

## Provenance and tracking

- CrossWire module: https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=ISBE
- Original import/provenance and recorded owner decision: [issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1)
- Reader acceptance: [issue #79](https://github.com/icfmp/Bible-Resources-ISBE/issues/79)
- Editorial review: [issue #9](https://github.com/icfmp/Bible-Resources-ISBE/issues/9)

**No automatic publication:** CI verifies data, not approval of a specific release. Do not auto-toggle a draft to public or upload a public binary without the project owner's release decision.
