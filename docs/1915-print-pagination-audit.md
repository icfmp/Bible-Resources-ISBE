# Historical print folio continuity: five-volume source check

Source-image comparison of the thirteen Scripture metadata candidates
revealed a potential **facsimile pagination discontinuity** around the
TAANACH printed passage in volume V: PDF page 78 shows printed folio
2886, and PDF page 79 shows folio 2889. The source witness may lack
leaves 2887–2888; this is a research observation, not a verified claim
that the original physical 1915 book lacked its pages.

The source-SHA-locked audit
`scripts/audit_1915_scan_pagination.py` checks the printed running
folio numbers recognized in the top OCR layer of **every PDF page of all
five volumes** and reports suspicious gaps **only** where two adjacent
PDF pages both yield unambiguous printed folio numbers. There is no
attempt to fill an absent page or reconstruct an author's words.

Page header OCR is imperfect. **Every candidate gap must be checked
against the original page images**; no missing-page claim is certified
by this audit alone. The workflow preserves machine-readable reports
as CI review artifacts, with the original PDF hashes in
`sources/print/1915-volume-witnesses.json`. Keep recovered historical
source images and a new page witness distinct from the source-locked
canonical CrossWire TEI. Rights and publishing remain blocked (#1);
full article-to-print comparison remains open (#9).

## First five-volume result (2026-11-23)

The completed initial CI matrix [run 45123423853](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45123423853)
reported **eight adjacent printed-folio jump candidates** (volumes I: 1,
II: 4, III: 0, IV: 1, V: 2). The versioned report
`workspace/reports/1915-scan-folio-continuity-v1.json`
records the exact neighboring PDF pages and their apparent printed numbers.

One discrepancy can be corroborated by visually examining **the
two actual adjacent PDF images**: volume V PDF page 78 shows printed
folio **2886**, and PDF page 79 shows folio **2889**. The identified
*scan* does not contain images of intervening printed folios **2887–2888**.
Its source JPEG digests and evidence run identifiers are retained.
This is a **digitization-source gap**, not proof that those folios were
absent from the 1915 printed book. An independently obtained scan of
those leaves is necessary for source-certified TAANACH collation.

The seven other OCR candidates are **not yet visually certified**,
especially jumps of ten folios, which may simply reflect OCR confusion
between printed numerals. They must not be advertised as seven confirmed
missing-page events. This scan is not an exhaustive inventory of every
physical leaf: any page whose OCR header could not be interpreted was
deliberately excluded.

## OCR neighborhood cross-check: volume V, folios 2949–2960

A read-only examination of the OCR layer of the same SHA-locked volume V
shows running headers in the sequence **2949, 2960, 2951, 2952**; after
2959, **2960 appears again**. This strongly indicates that the first
apparent 2960 is actually folio **2950 misread by OCR**, rather than
ten missing leaves. It is **not image-certified** because a direct
page-image screenshot could not be obtained in that examination.
The unchanged gap candidate has gained an explicit OCR-neighborhood
annotation in the versioned report; no source text or article content
has changed.

The generic pagination auditor now adds follow-up OCR page-header
context for *every* candidate, including whether the suspicious number
recurs at its expected position. It **never suppresses** a candidate
or upgrades its evidence to visually confirmed solely on OCR. Verify
remaining candidates with the original page images before declaring
a missing page, and keep the distinct genuine volume-V scan gap
at folios **2887–2888** unresolved pending a second physical witness.
