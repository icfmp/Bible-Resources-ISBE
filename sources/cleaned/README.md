# Maintained historical cleaned masters

Real, complete, verified sources under `<category>/<language>/<resource>/` only, following Bible-Resources.

The **English ISBE historical editorial master** is:
`encyclopedias/en/isbe-1915/ISBE.xml`.

It starts from the immutable 9,380-entry CrossWire source-faithful TEI; restores the 31 documented printed articles/redirects and applies all the exact, reviewed 1915 prose, structure and verse-target corrections in their original order. The adjacent `CLEANUP_MANIFEST.json` records original/canonical/output SHA-256, source paths, original evidence and validation status. `editorial/README.md` records the correction chain and outstanding editorial uncertainties.

Rebuild reproducibly: `python3 scripts/persist_1915_cleaned_master.py --assemble`.
Check stored bytes: `python3 scripts/persist_1915_cleaned_master.py --verify-only`.

This is the base for future `modern/en/` modernization; **never modernize or silently change the historical master in place**. Note that `cleaned/en/ISBE.xml` at the repository root remains a locked **CrossWire-faithful technical witness** for original parity tests, not the historically corrected master.

Rights and publication remain unapproved: a clean XML file is not a release or a license clearance.
