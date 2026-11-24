# ISBE repository layout — single source of truth

The physical layout follows [Bible-Resources](https://github.com/icfmp/Bible-Resources): real `sources/original/`, real `sources/cleaned/` and independently verified `modules/` records.

| Kind | Authoritative file | Status |
| --- | --- | --- |
| Exact CrossWire 2.2 original | `sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip` | Immutable 9,987,447 bytes |
| Original digital-text TEI witness | `workspace/witnesses/crosswire-2.2/ISBE.xml` | Reconstructed, CrossWire-faithful; **not** cleaned |
| Original article index | `workspace/witnesses/crosswire-2.2/article-index.json` | Stable IDs and source checksum evidence |
| Original printed facsimile research metadata | `workspace/witnesses/print/1915-volume-witnesses.json` | PDFs are external, not committed |
| Corrected historic English master | `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml` | 9,380 entries, TEI P5 validated |
| Public corrected historical SWORD edition | `modules/isbe-1915/metadata.json` and the [0.1.0 release](https://github.com/icfmp/Bible-Resources-ISBE/releases/tag/isbe-1915-v0.1.0) | Compiled, full 9,380-entry native readback verified; reader limitations documented; published ZIP is authoritative (no duplicated `payload/`) |
| Optional future modern English | `sources/cleaned/encyclopedias/en/isbe-modern/` | Separate optional edition, not a translation prerequisite |
| Future translations | `sources/cleaned/encyclopedias/<language>/isbe-1915/` | Derive directly from the SHA-pinned corrected English historical master, **reusing all canonical IDs and source keys**; create only with real content |

Old root `cleaned/`, `modern/`, `translations/`, old `sources/crosswire/` and `sources/print/` paths are intentionally removed. No symlinks or temporary compatibility copies are left in the repository. Code and workflow references to these exact old paths have been migrated and are guarded by `tests/test_source_layout.py`.

The original ZIP, source-faithful TEI witness and corrected historical TEI preserve their original **byte-for-byte SHA-256 values**. The migration changes file locations and path metadata only, not original or editorial content, article order or stable identifiers.

Verification:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/persist_1915_cleaned_master.py --verify-only
python3 scripts/persist_1915_cleaned_master.py --assemble
```

The complete source rebuild requires pinned official TEI P5 validation dependencies including `jing`. CI enforces the exact original and corrected historical TEI bytes. The corrected English 0.1.0 SWORD edition is **publicly released** with independently verified native contents and documented GUI-reader limitations. The project owner accepted CrossWire's Public Domain declaration as the distribution basis; [issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1) is closed. The earlier source/candidate draft remains unpublished and historical only.

**Translation rule:** all future language versions share the original corrected English 9,380-entry ordered index, `entry/@xml:id`, `entry/@n`, intra-article source IDs and reference targets. See the [translation workflow](workflow.md), [fail-closed parity checker](../scripts/validate_translation_identity.py), and [tracking issue #103](https://github.com/icfmp/Bible-Resources-ISBE/issues/103). Localized display titles and search aliases are not new canonical indexes.
