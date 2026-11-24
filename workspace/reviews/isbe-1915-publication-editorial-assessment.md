# ISBE 1915 — scoped editorial release assessment (2026-11-24)

This report documents what was **actually verified** before publishing the corrected historical source. It does not pretend that every article has been manually collated against all printed 1915 volumes.

## Sources and immutability

- Original unmodified CrossWire 2.2 archive SHA-256: `4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32`.
- Original CrossWire-derived canonical TEI witness SHA-256: `a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25`.
- Corrected reviewed historical TEI master SHA-256: `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.
- Source-locked native SWORD adapter import SHA-256: `bdac245cad329fdff8039d0374815ff7086b8a5f8055118f1250461b9d5f17ec`.
- No original or corrected historical article text was rewritten, removed or normalized in this final audit.

## Comprehensive *automated* paratext screening, not comprehensive manual collation

[Source-locked scan #45349111567](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45349111567) applied the same reusable paratext scanner independently to **all 9,380 articles** in both the original digital witness and the cleaned historical master:

| Digital text witness | Articles scanned | TEI text units scanned | Specific digital-origin paratext candidates |
| --- | ---: | ---: | ---: |
| Original CrossWire digital TEI | 9,380 | 75,857 | **0** |
| Corrected historical TEI master | 9,380 | 75,859 | **0** |

The separate broader **lexical** profile of the unedited CrossWire source matched **21 text units** (24 word-level occurrences). All 21 cases have an existing [source-locked manual classification ledger](editorial-notices-reviewed-v1.json); they are historical scholarship about scribes/transcription or ordinary English uses such as *scanned every thought*. All 21 were **retained**. No deletion was approved or necessary. The word *transcriber* in a historical criticism discussion is not evidence of an intrusive modern digitization notice.

These are **finite pattern-based detection methods**. A rare notice not matching the patterns might still be present; the results do not justify a claim that the corpus has been manually inspected paragraph by paragraph for every possible extraneous word.

## Independent native and real-reader review

- The adapted source and actual SWORD `mod2imp` native roundtrip agree on **all 9,380 article keys**, with zero extra/missing entries and zero text or XML structure differences. The original article/section `#xml:id` selectors are preserved in `corresp` in the generated adapter.
- **5,919** native article-reference targets and **93,164** biblical `osisRef` fields were audited. **80** section-level targets necessarily navigate to their containing articles in SWORD rather than exact intra-article positions, while the original selector is preserved.
- Real article-to-article click `ARK → ARK OF BULRUSHES` works in the BibleTime Mag and Xiphos dictionary Viewer; **Xiphos Book View** still shows an error. These observations are reader-specific and are not historical text errors.
- Six real GUI screenshots of `CHORBE` (Greek), `AMNON` (pointed Hebrew) and `ELKOSHITE` (nested sections) were inspected for **both** clients, [run #45349111541](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45349111541). The source-attested characters and numbered subdivisions are visible. This is representative sample review, **not** complete printed glyph collation.
- Historically empty entries have been restored through source-attested print evidence under earlier approved editorial deltas. The unchanged corrected master and its reconstruction/official TEI P5 checks remain independently verified.

## Publication decision boundary

The project owner has accepted the Public Domain basis of the 1915 ISBE as declared by CrossWire and has explicitly authorized publication. No new independent legal research or additional owner sign-off is required for this already authorized release. This review finds **no source-authenticity issue requiring an unreviewable deletion**. The edition is suitable for an initial **source-qualified 0.1.0 public release**, with the following limitations stated to readers:

1. A corrected historical digital source, **not** a comprehensive facsimile or full print collation of the original five volumes.
2. Greek/Hebrew glyphs are displayed for tested attested digital-source samples; unrepresented original print glyphs are not assumed restored.
3. Browser/reader-dependent interactive Bible-reference destinations and Xiphos Book View navigation remain partly unreliable.
4. The 80 nested/section anchors retain original selectors but native navigation generally targets the containing article.

Do not remove Greek, Hebrew, headings, verse references, printed scholar credits or manuscript-critical remarks merely to hide a reader bug. Future improvements require independent evidence, versioned editorial deltas and a new curated release revision.
