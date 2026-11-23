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
