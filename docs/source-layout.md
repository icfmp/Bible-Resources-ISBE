# ISBE repository layout — single source of truth

The physical layout follows [Bible-Resources](https://github.com/icfmp/Bible-Resources): real `sources/original/`, real `sources/cleaned/` and independently verified `modules/` records.

| Kind | Authoritative file | Status |
| --- | --- | --- |
| Exact CrossWire 2.2 original | `sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip` | Immutable 9,987,447 bytes |
| Original digital-text TEI witness | `workspace/witnesses/crosswire-2.2/ISBE.xml` | Reconstructed, CrossWire-faithful; **not** cleaned |
| Original article index | `workspace/witnesses/crosswire-2.2/article-index.json` | Stable IDs and source checksum evidence |
| Original printed facsimile research metadata | `workspace/witnesses/print/1915-volume-witnesses.json` | PDFs are external, not committed |
| Corrected historic English master | `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml` | 9,380 entries, TEI P5 validated |
| Planned compiled SWORD module | `modules/isbe-1915/metadata.json` | **Not built**; no `payload/`, no native reader validation or publication approval |
| Future modern English | `sources/cleaned/encyclopedias/en/isbe-modern/` | To be created **only when an actual source exists** |
| Future translations | `sources/cleaned/encyclopedias/<language>/isbe-modern/` | To be created **only when actual sources exist** |

Old root `cleaned/`, `modern/`, `translations/`, old `sources/crosswire/` and `sources/print/` paths are intentionally removed. No symlinks or temporary compatibility copies are left in the repository. Code and workflow references to these exact old paths have been migrated and are guarded by `tests/test_source_layout.py`.

The original ZIP, source-faithful TEI witness and corrected historical TEI preserve their original **byte-for-byte SHA-256 values**. The migration changes file locations and path metadata only, not original or editorial content, article order or stable identifiers.

Verification:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/persist_1915_cleaned_master.py --verify-only
python3 scripts/persist_1915_cleaned_master.py --assemble
```

The complete source rebuild requires pinned official TEI P5 validation dependencies including `jing`. CI enforces the exact original and edited bytes. All source and correction rights remain pending under [issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1); the only GitHub source release is an unpublished draft. No corrected SWORD module should be represented as compiled or released until native readback, reader acceptance and rights review succeed.
