# ISBE 1915 — corrected historical source and compiled SWORD candidate v0.1.0-rc.1

**UNPUBLISHED DRAFT — remaining editorial and GUI acceptance; CrossWire Public Domain distribution basis accepted by the owner.** This draft now contains the historical TEI source **and a genuine compiled SWORD dictionary candidate**. Neither is publicly released, approved for redistribution or certified as a facsimile of all 1915 print typography.

## What the candidate contains

- Full historical English *International Standard Bible Encyclopedia* (Orr/Howard-Severance, 1915), reconstructed as TEI P5 from CrossWire SWORD ISBE 2.2.
- **9,380 entries**, stable source-key-derived article IDs.
- **31 originally empty entries restored** (20 substantive texts and 11 redirects) from source-traceable 1915 print evidence.
- Source-backed editorial corrections of printed text and Biblical cross-references, including the Additions to Esther 13:9 target. Every change is documented and reversible.
- Official TEI P5 4.12.0 RELAX NG/Schematron and source parity checks passed. Byte-identical rebuild of the checked-in corrected master was verified in GitHub Actions.

## Provenance

Source repository: [icfmp/Bible-Resources-ISBE](https://github.com/icfmp/Bible-Resources-ISBE). The **exact** pinned source commit for this candidate is `0853bc904acc24de50fb49ab75a32a5b2bb3c339` ([PR #76](https://github.com/icfmp/Bible-Resources-ISBE/pull/76)).

- Immutable original CrossWire 2.2 ZIP SHA-256: `4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32`.
- Preserved source-faithful CrossWire TEI SHA-256: `a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25`.
- Corrected historical working TEI SHA-256: `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c` (37,062,851 bytes).

A deterministic source ZIP in this **draft** contains the corrected TEI `ISBE.xml`, its `CLEANUP_MANIFEST.json`, the original CrossWire `PROVENANCE.json` (metadata only, not the original ZIP), and this README. Asset checksums are attached separately.

## Native SWORD candidate included in the unpublished draft

A genuine `BRISBE1915` zLD module was compiled via upstream SWORD `tei2mod` from our **corrected** TEI, not copied from the old CrossWire binary. The **newest draft candidate** is `BRISBE1915-native-workid-draft.tar.gz`, SHA-256 `6b7edccc0f27fbcf71595597ddd8794a5db72acd3952fb03e1e4e569e7acf3a5`, 11,731,030 bytes, created by [run #45346863700](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45346863700) from explicit `BRISBE1915:<key>` SWORD links. The old `BRISBE1915-native-candidate-NOT-FOR-PUBLICATION.tar.gz` (SHA-256 `6993937ffcdba83348dc0f0cc510613a42f85d3e4c5423f19355a1cf65ee9c9b`) remains in the draft as superseded evidence. Additional draft assets include `BRISBE1915-NATIVE-SHA256SUMS.txt` and `sword-native-roundtrip.json`.

On native `mod2imp` readback: **9,380/9,380 keys**, zero missing, unexpected, malformed, Unicode text-different or XML-structure-different entries. SWORD link adaptation maps 5,919 internal references to their article keys, exposes 93,164 Bible references and documents 80 section targets that now resolve only to their containing articles. A later CLI `HTMLHREF` smoke on four articles renders links. Independent real GUI article clicks are partially validated: both readers' dictionary/Mag panes resolve `ARK OF BULRUSHES`, but Xiphos's separate Book View still shows an error. Scriptural navigation and final editorial presentation remain open. No further independent copyright audit is required by the owner. [Native build evidence](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45259095383); [permanent SWORD CI fix](https://github.com/icfmp/Bible-Resources-ISBE/pull/81).

The source-draft promotion process privately attached the binary, validated its exact SHA-256 and native parity JSON, checked `draft=true` before and after, and deleted the previous temporary Actions binary artifact after successful storage. [Private archival run #45262814840](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45262814840).

## Limitations and release gate

This text is **not** modern English. A 24-article source-fidelity audit established that many original Greek/Hebrew graphemes are not reproduced in the CrossWire-based digital witness. Neither exact original-print facsimile certification nor full-corpus independent editorial peer review is claimed.

**Do not publish this draft** until the [copyright / redistribution assessment (#1)](https://github.com/icfmp/Bible-Resources-ISBE/issues/1) is independently completed, including the source's original article/contributor rights (particularly for France/EU), the specific CrossWire digitization and any independently protected later editorial layer. CrossWire labels its ISBE 2.2 distribution `Public Domain`, which is meaningful primary evidence, but does not alone settle every jurisdiction and layer. Source retention in a public repository should itself be assessed under the same rights review.

The **compiled SWORD binary is retained in this private draft**, but no Bible app integration, modernized derivative, public GitHub release or catalog update is authorized by a draft.

## Validation evidence

- [Verified historic corrected source retention](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45228747068).
- [Two independent source rebuilds](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45229503769) and [45229484424](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45229484424).
- [Official TEI P5 source validation](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45229858513).

## Latest candidate correction and known GUI limitations (2026-11-24)

The retained corrected SWORD adapter uses the installed dictionary module's identity instead of the invalid `self` work name, providing a rendered HTMLHREF URL `sword://BRISBE1915/ARK+OF+BULRUSHES`. Exact native importer TEI SHA-256: `bdac245cad329fdff8039d0374815ff7086b8a5f8055118f1250461b9d5f17ec`. This changed the compiled-copy links **only**, not any original article wording, title, source ID or corrected historical TEI master. The complete 9,380-entry binary was rebuilt, native-readback-verified and SHA-pinned. The earlier draft binary is superseded, not deleted.

The [Xiphos/BibleTime GUI click run](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45344977265) confirms correct destination content in the dictionary/Mag panes of both clients, but **not** in Xiphos's separate Book View. BibleTime's requested Exodus 6:20 Scripture tab also had a separate main-body mismatch (Genesis 1), while its reference/magnifier view recognized the requested passage. Both limitations remain disclosed and unresolved. Publishing will require the owner's approval of the final candidate and its declared limitations; the archive's presence in a draft does not imply release approval.
