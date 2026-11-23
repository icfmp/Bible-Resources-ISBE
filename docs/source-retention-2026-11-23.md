# ISBE original and corrected editorial source retention — 2026-11-23

This is a reproducible source-retention record, **not** a module publication,
critical facsimile approval, or copyright determination.

## Stored source bytes

| Role | Repo path | Size | SHA-256 |
| --- | --- | ---: | --- |
| Unedited CrossWire ISBE 2.2 SWORD ZIP | `sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip` | 9,987,447 bytes | `4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32` |
| **Historically corrected, non-modernized** English ISBE TEI | `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml` | 37,062,851 bytes | `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c` |
| Byte-locked source-faithful intermediate (unchanged from before retention) | `cleaned/en/ISBE.xml` | 37,056,724 bytes | `a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25` |

The new original ZIP has the **same Git blob SHA**
(`c72a179b275e21387fb26bfe6851174aa69f1d60`) as the original saved
earlier at `sources/crosswire/isbe-2.2/ISBE.zip`: Git stores identical bytes
as one content-addressed blob. The source-faithful intermediate continues to
serve as an immutable source witness; only the distinct **source-cleaned
historical edition** contains the verified restorative changes.

The maintained `scripts/persist_1915_cleaned_master.py --assemble`
rebuilds eight successive source-evidence-locked editorial stages,
independently validates the complete final TEI P5 XML against pinned official
RELAX NG + ISO Schematron, refuses changed output bytes, then copies the two
whole files. The `--verify-only` mode checks both stored files and manifests.

Build/commit proof: [GitHub Actions run
45228747068](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45228747068)
**success**. The earlier independently validated source material and exact
final target came from [run
45217614531](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45217614531).

**Modernization:** future `modern/en/` derives from the historical working
cleaned edition, not the uncorrected digital source witness, and must preserve
article identifiers. It is **not started** here.

**Limits:** original-print literal fidelity rejected in 24 historically
inspected candidates; all Greek/Hebrew and typography are not reconstructed.
CrossWire and the print remain separate primary witnesses. Neither the source
retention nor schema validation resolves source-derived field rights. Issue
[#1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1) remains open, and
release, SWORD publishing and translations are **not authorized**.
