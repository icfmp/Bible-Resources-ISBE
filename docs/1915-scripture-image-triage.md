# Image-based research on thirteen Scripture navigation inconsistencies

The 2026-11-23 read-only audit (#49) identified **13 digital reference
inconsistencies in 12 articles**. Research (#50 and #51) downloaded the
identified original Howard-Severance 1915 scans for **all five volumes** and
verified original PDF SHA-256 digests. Original rendered-page images were
examined for the affected passages, not merely OCR output.

The versioned evidence ledger
`workspace/reviews/1915-scripture-reference-image-triage-v1.json`
stores each exact immutable TEI reference and parent paragraph identifier,
original visible reference, original digital `cRef`, the print volume, PDF
page, page-image SHA-256, GitHub Actions job, and the reading observed on the
printed image. The results are **AI-assisted**, not human peer-reviewed.

- **12 reference occurrences** have an identified image-based reading
  indicating an incorrect digital target. They span Zephaniah incorrectly
  linked as Zechariah, Judges incorrectly linked as Revelation, and Job
  incorrectly linked as Jonah.
- **1 occurrence (TAANACH)** has no adequately verified page in the
  identified volume-V facsimile. Do not infer a correction merely because
  MEGIDDO cites the same passage.
- **ESCHATOLOGY OF THE OLD TESTAMENT:** the printed reference appears as
  Zeph 3:13,20, while the digital continuation ends in 10; this possible
  **textual** discrepancy requires an independent exact text-slot review,
  beyond correcting the first digital `cRef`.
- **ROBBER; ROBBERY:** markup splits the displayed book abbreviation across
  the paragraph and the reference node (`J` + `Ob 5:5`); do not replace
  the visible label without checking this segmentation.
- **JUDGES, BOOK OF** and **MEGIDDO; MEGIDDON** encode continuation text
  in a single reference node, so an apparent mismatch cannot be safely
  corrected by simplistic global regex operations.

The ledger is a research record, **not an approval to edit canonical or
editorial text**. Before a corrected separate editorial TEI is produced, the
generic exact-source transformation must preserve the whole printed reading,
parent structure, all existing IDs, source provenance and unrelated articles.
The original ZIP/IMP and canonical source-locked TEI stay unchanged.
Issue #9 remains open for full print collation and editorial cleanup; #1
blocks publication and redistribution until rights are independently cleared.

Source-image review workflows were temporary; their reproducible evidence
remains in the GitHub Actions history. Repeat full PDF rendering only on
manual dispatch to avoid unnecessary network and CI churn.
