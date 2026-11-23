# ISBE historical English editorial provenance

**This is a working edition, not an independently certified facsimile or an authorized public release.** Source text is historical English; English modernization is a separate downstream `sources/cleaned/encyclopedias/en/isbe-modern/` task.

The authoritative corrected `../ISBE.xml` is built from the original source-faithful 9,380-entry `workspace/witnesses/crosswire-2.2/ISBE.xml` with the exact source-locked correction sequence:

1. **31 printed historical entries recovered** — `scripts/finalize_1915_recovery.py`, `workspace/reviews/1915-second-pass-visual-approval-v1.json`; 20 full articles and 11 redirects.
2. **Six print-attested wording corrections** — `scripts/apply_1915_print_deltas.py`; `workspace/reviews/1915-approved-print-deltas-v1.json`.
3. **Twelve printed-verse target corrections** — `scripts/apply_1915_scripture_targets.py`; source-image reviewed candidates.
4. **Verified text-plus-reference correction** — `scripts/apply_1915_reference_text_deltas.py`, `workspace/reviews/1915-approved-reference-text-deltas-v1.json`.
5. **Separate source-display Taanach navigation correction** — `scripts/apply_display_verified_scripture_targets.py`; digital witness evidence does **not** imply printed-original certification.
6. **Eight original printed English prose corrections** — `scripts/apply_1915_low_overlap_prose_deltas.py`, `workspace/reviews/1915-approved-low-overlap-prose-deltas-v1.json`.
7. **Sixteen further exact printed corrections** — `scripts/apply_1915_additional_prose_deltas.py`, `workspace/reviews/1915-additional-exact-print-deltas-v1.json`.
8. **Additions to Esther 13:9 printed reference restoration** — `scripts/apply_1915_printed_apocrypha_refs.py`, `workspace/reviews/1915-gainsay-additions-esther-reference-v1.json`.

All operations retain full source evidence, fail on source/ledger drift, and preserve original source data. In particular, the corrected TEI **must** equal SHA-256 `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`, which passed pinned official TEI P5 4.12.0 RELAX NG and ISO Schematron with no violations (validation workflow [45217614531](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45217614531)). The new managed build retests this, checks the exact resulting hash, and refuses nondeterministic changes.

**Outstanding:** 24 article decisions reject exact original printed fidelity but do not restore all Greek/Hebrew glyphs (PR #75). Full critical reconstruction, all 9,380 printed articles, independent human editorial peer review and redistribution rights are not certified. Source original and faithful CrossWire intermediate remain separate. Issue #1 controls permission to release, issue #9 tracks content audit.
