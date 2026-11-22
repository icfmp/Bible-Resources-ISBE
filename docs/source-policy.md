# Provenance and fidelity

The historical 1915 work, the CrossWire ISBE **SWORD module 2.2**, our faithful rebuilt **TEI master**, and future modernizations/translations are distinct artifacts.

## Archived original

`sources/crosswire/isbe-2.2/ISBE.zip` was obtained from the CrossWire distribution and retained without modification. Its exact URL, timestamp, size and SHA-256 are recorded in `MANIFEST.json`. The ZIP contains one module configuration and four compressed dictionary files. The module configuration states `SourceType=TEI`, `ModDrv=zLD`, `Encoding=UTF-8`, `Version=2.2`, `DistributionLicense=Public Domain`. The module's documented 2.2 history includes an OCR correction and layout improvements.

## Derived artifacts

`workspace/exports/isbe-2.2.imp` preserves the content exported by SWORD. The extractor reconstructs `cleaned/en/ISBE.xml` with stable identifiers, preserving article text and all source-contained scripture references. This **does not independently verify** the digital text against printed 1915 volumes; no such claim should be made.

Only source-backed editorial corrections may alter historical content, and each correction must be documented and reversible. Modern English and translations are separate derivative editions. Before publishing, review licensing and legal rights for both the digital original and derivatives in intended jurisdictions.
