# BRISBE1915 — International Standard Bible Encyclopedia 1915 SWORD v0.1.0 RC1

**Status: GitHub release DRAFT, NOT published. Redistribution rights and independent GUI-reader acceptance are pending.**

This is a genuine compiled, ZIP-compressed **SWORD zLD dictionary** created from our corrected historical English ISBE TEI, not a copy of the unchanged original CrossWire binary. It uses a unique SWORD module ID `BRISBE1915` so it can coexist with upstream `ISBE`.

## Scope and fidelity

- All **9,380 source articles** compiled under their original dictionary keys.
- A full native `mod2imp` readback compared **every** article, key, Unicode character and XML tree with the SWORD-importer TEI: no missing or extraneous keys, no malformed entries, **zero content or XML-structure mismatches**.
- **5,919 internal links** retargeted from source TEI IDs to native SWORD `self:key` references; original selectors retained in `corresp` for reversibility.
- **93,164 biblical cross-reference elements** expose SWORD `osisRef` alongside their unchanged original `cRef`.
- **80 section-level links** now reach the corresponding article but may lose deep-scroll precision, explicitly documented.
- Verified native module registration and HTML/HTMLHREF/plain rendering through Diatheke: representative HTMLHREF samples produced 63 markup anchors across AARON, ABIDE, GAINSAY and ZEBIDAH.
- The 1915 text was **not modernized**, nor was its entire printed edition critically reconstructed. Original Greek/Hebrew omissions and editorial limitations inherited from the source remain documented.

## Standard installation layout

The installable ZIP contains standard SWORD paths:

```text
mods.d/brisbe1915.conf
modules/lexdict/zld/brisbe1915/dict.dat
modules/lexdict/zld/brisbe1915/dict.idx
modules/lexdict/zld/brisbe1915/dict.zdx
modules/lexdict/zld/brisbe1915/dict.zdt
```

Do not install or redistribute this RC until the legal gates are satisfied. The separate original CrossWire `ISBE` module is not overwritten.

## Provenance

Historical corrected source: `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml`, SHA-256 `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.

Compiled import TEI SHA-256 `6d5262d69ca13724a9a9a3bcd8cd23e957aefddfeeb0be20a7ce59e2d97fa745`.

Producer repo: https://github.com/icfmp/Bible-Resources-ISBE . Producing native-build source commit: `47755bfc36d0e05dc33482e2109740e7b23e784e` ([PR #80](https://github.com/icfmp/Bible-Resources-ISBE/pull/80)). Independent native roundtrip: [Actions #45259095383](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45259095383).

## Publication blockers

This draft is only a reproducibility and quality-control artifact; **not permission to redistribute**. See [rights issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1), which specifically requires independent review of named original 1915 contributions in the target EU/France jurisdiction and of the CrossWire digitization layer. CrossWire itself labels its version 2.2 `Public Domain`, but the project has not completed its exact layered legal assessment.

Xiphos/BibleTime graphical article, language, internal-link navigation and 29 nested section rendering still need real independent reader verification. [Module issue #79](https://github.com/icfmp/Bible-Resources-ISBE/issues/79) remains open. The project owner has requested publication but these prerequisites are not falsely marked complete. No GitHub release may be promoted from draft to public while the rights gate is open.
