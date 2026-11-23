# ISBE 1915 — corrected historical TEI source v0.1.0-rc.1

**UNPUBLISHED DRAFT — rights clearance pending. Not a public release, endorsed facsimile, modern-English edition or SWORD module.**

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

## Limitations and release gate

This text is **not** modern English. A 24-article source-fidelity audit established that many original Greek/Hebrew graphemes are not reproduced in the CrossWire-based digital witness. Neither exact original-print facsimile certification nor full-corpus independent editorial peer review is claimed.

**Do not publish this draft** until the [copyright / redistribution assessment (#1)](https://github.com/icfmp/Bible-Resources-ISBE/issues/1) is independently completed, including the source's original article/contributor rights (particularly for France/EU), the specific CrossWire digitization and any independently protected later editorial layer. CrossWire labels its ISBE 2.2 distribution `Public Domain`, which is meaningful primary evidence, but does not alone settle every jurisdiction and layer. Source retention in a public repository should itself be assessed under the same rights review.

No compiled SWORD binary, Bible app integration, modernized derivative, GitHub publication or catalog update is authorized by a **draft**.

## Validation evidence

- [Verified historic corrected source retention](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45228747068).
- [Two independent source rebuilds](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45229503769) and [45229484424](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45229484424).
- [Official TEI P5 source validation](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45229858513).
