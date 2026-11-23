# Corrected and maintained source masters

Real reviewed editorial masters belong under `<category>/<language>/<resource-id>/`, matching Bible-Resources.

The corrected historical English ISBE is [`encyclopedias/en/isbe-1915/ISBE.xml`](encyclopedias/en/isbe-1915/ISBE.xml), with an adjacent `CLEANUP_MANIFEST.json` and [editorial record](encyclopedias/en/isbe-1915/editorial/README.md). It contains all **9,380 entries** plus the source-attested 1915 repairs, without changing the original upstream SWORD source.

Original CrossWire bytes live separately in `sources/original/`. The reconstructed digital-faithful TEI is an **intermediate witness** under `workspace/witnesses/crosswire-2.2/`, and is never confused with this corrected edition.

Future modern English or translations must be new independently versioned source masters (e.g. `encyclopedias/en/isbe-modern/ISBE.xml`), created only when they exist; no empty placeholder folders. Rebuild/verification: `python3 scripts/persist_1915_cleaned_master.py --assemble` and `--verify-only`. Redistribution remains blocked by rights issue #1.
