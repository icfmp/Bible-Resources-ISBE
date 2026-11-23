# Scripture-reference display consistency audit

This read-only, source-SHA-locked scanner assesses **only** digital consistency between
explicit single-verse visible labels and their encoded `cRef` chapter/verse.
It scans the full canonical TEI, but intentionally does not infer book aliases,
reconstruct missing references, compare 1915 printed pages, or alter the source.

Run:

```sh
python3 scripts/audit_scripture_ref_display.py workspace/witnesses/crosswire-2.2/ISBE.xml \
  --report workspace/tmp/scripture-ref-display-audit.json
```

Every mismatch is a **candidate**, not an authorized correction. Complex ranges,
implicit chapter/verse labels, unparseable or missing `cRef` values are excluded
from the narrow comparison and must not be counted as validated. The report
records assessment and exclusion totals, original identifiers and both readings.
The workflow retains the complete report as a CI artifact; no correction or
publication can follow without checking the 1915 print witness, recording
individual provenance and a versioned editorial delta.

This check complements, but does not replace, full-volume print collation under
#9. Source rights and distribution remain blocked under #1.
