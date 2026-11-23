# ISBE source store — immutable originals and maintained cleaned masters

Following the same **category / language / resource** convention as [Bible-Resources](https://github.com/icfmp/Bible-Resources/tree/main/sources):

- `original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip` — byte-identical CrossWire SWORD 2.2 source with `PROVENANCE.json`. The existing historical archive `sources/crosswire/isbe-2.2/ISBE.zip` is also retained for existing source-locked rebuilds.
- `cleaned/encyclopedias/en/isbe-1915/ISBE.xml` — complete **historical working editorial TEI P5**, restored from original printed evidence and all separately source-locked corrections, with `CLEANUP_MANIFEST.json` and a detailed editorial index. This is **not modern English**.
- `../cleaned/en/ISBE.xml` — the unchanged source-faithful TEI witness of CrossWire, **not** the historically corrected master. It must remain unchanged because the whole original extraction and every correction build explicitly refer to its SHA.

The stored cleaned master is generated, not hand-edited, by `python3 scripts/persist_1915_cleaned_master.py --assemble`. `--verify-only` checks both original and cleaned exact SHA-256 locks. The build fails if an original, expected corrected edition, editorial proof, or pinned official TEI P5 validation differs.

**Rights are under independent review (issue #1)**. Saving a working editorial source in Git is not release approval, a claim that the full 1915 print has been critically collated, or permission to publish a new SWORD module, translation, or other distribution.
