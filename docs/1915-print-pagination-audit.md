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
`workspace/witnesses/print/1915-volume-witnesses.json`. Keep recovered historical
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

At the first review, seven additional OCR candidates remained unverified.
They have since been **visually resolved as OCR errors** (see below).
The original automated scan was not an exhaustive inventory of every
physical leaf: pages whose OCR header could not be interpreted were
deliberately excluded.

## OCR neighborhood cross-check: volume V, folios 2949–2960

A read-only examination of the OCR layer of the same SHA-locked volume V
shows running headers in the sequence **2949, 2960, 2951, 2952**; after
2959, **2960 appears again**. This strongly indicates that the first
apparent 2960 is actually folio **2950 misread by OCR**, rather than
ten missing leaves. This inference was **OCR-only at that stage**. The following independent
page-image examination has since confirmed that folio 2950 is present.
The earlier OCR-neighborhood annotation remains preserved in the ledger
as evidence of the discovery sequence.

The generic pagination auditor now adds follow-up OCR page-header
context for *every* candidate, including whether the suspicious number
recurs at its expected position. It **never suppresses** a candidate
or upgrades its evidence to visually confirmed solely on OCR. Keep the distinct genuine volume-V scan gap at folios **2887–2888**
unresolved pending a second physical witness.

## Second pass: all seven remaining pairs visually examined (2026-11-23)

The [SHA-locked two-page image research, run 45125508778](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45125508778)
has now verified all seven remaining OCR jump candidates **directly
against the original facsimile images**. These are AI-assisted visual
readings, not independent human scholarly peer review. The original
digital OCR readings are retained in the report; the source images
establish that the folio numbers below actually appear on those pages.

| Volume | PDF image pages | OCR jump originally reported | Printed numbers seen on page images | Finding |
| --- | --- | --- | --- | --- |
| I | 408–409 | 374→376 | **374→375** | OCR misread |
| II | 408–409 | 1058→1069 | **1058→1059** | OCR misread |
| II | 528–529 | 1174→1176 | **1174→1175** | OCR misread |
| II | 688–689 | 1331→1333 | **1331→1332** | OCR misread |
| II | 706–707 | 1349→1360 | **1349→1350** | OCR misread |
| IV | 53–54 | 2149→2160 | **2149→2150** | OCR misread |
| V | 143–144 | 2949→2960 | **2949→2950** | OCR misread |

The versioned report
`workspace/reports/1915-scan-folio-continuity-v1.json`
records the source PDF SHA-256, two independently generated page JPEG
SHA-256 digests, exact PDF page positions, source-image job ID and
visible folios for each case. Its findings remain explicitly scoped to
the **eight initial adjacent-header jump candidates**: seven confirmed
OCR false positives, one confirmed missing-page interval **in this
specific scanned copy** (volume V, 2887–2888). Other omissions cannot
be ruled out by this OCR-driven candidate search.

**Editorial consequences:** no changes to the CrossWire original,
source-locked canonical TEI, or historical article content; the TAANACH
case remains uncorrected until a separately sourced facsimile of its
missing folios is actually compared. Neither this scan audit nor the
existing corrected navigation TEI is publishable without the separate
rights investigation (#1). Wider 9,380-article print collation stays
open (#9).
