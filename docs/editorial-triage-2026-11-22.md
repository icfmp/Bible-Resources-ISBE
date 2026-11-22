# Editorial triage: missing articles and non-content apparatus

Status: **research evidence, no authorized textual change** (2026-11-22).

## Authority and separation of layers

- The immutable CrossWire SWORD 2.2 ZIP and IMP export are digital *witnesses*, not the editorial authority for a critical edition.
- The 1915 five-volume **James Orr / Howard-Severance** printed encyclopedia is the historical comparison target. Do not substitute the later Bromiley revised edition.
- The source-faithful canonical TEI P5 baseline (SHA-256 `a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25`) is preserved unchanged until reviewed, source-backed deltas can be validated.
- Material created only for electronic distribution (CrossWire notes, licensing banners, OCR or transcription credits, maintenance notices, navigation instructions, source-key-generated display headings) must not be mistaken for original article prose. Keep provenance in repository metadata and manifests rather than duplicating it in the reading text.
- Historical author attributions, quotations, bibliography, critical observations, and original editorial notes that explain the work or text **are substantive** and remain unless a specific historic-source review shows otherwise. The rule is **relevance and origin**, not whether the word “note” is present.
- Record removals as explicit, reversible, source-SHA-bound deltas, including affected stable unit IDs, exact original content, evidence and rationale. Do not introduce bulk regex deletions or silently relax source-parity tests.

## Proven empty-source entries: 31 missing content records

See issues #7 and #12, PRs #8 and #11, and [full source-locked context audit](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45069263570).

All 31 cases are **entire article records with an empty sole paragraph**, not isolated whitespace inside complete articles. All paragraph IDs end in `-n000003`. The preceding node is the synthetic entry heading; there is no next paragraph. Removing the empty `p` alone would make the markup cosmetically cleaner but would conceal the missing-content problem.

### Independently attested original content

| Key | Print witness evidence | Digital source status | Editorial disposition |
| --- | --- | --- | --- |
| ABISSEI | 1915 vol. I, printed *ABISSEI* article after *ABISHUR*, before *ABISSUE*; the scan text includes an identification as an ancestor of Ezra and biblical cross-references | Empty in CrossWire-derived canonical TEI | **Text recovery required**; exact type, accents, punctuation and page image must be checked before transcription |
| AMNON | 1915 vol. I, printed *AMNON* article following *AMMONITESS*, before *AMOK*; the scan text includes two numbered definitions | Empty in CrossWire-derived canonical TEI | **Text recovery required**; printed spelling, Hebrew, punctuation and section boundaries need page-image proof |

**Source identification:** James Orr, ed., *The International Standard Bible Encyclopaedia*, Chicago: Howard-Severance, 1915, vol. I (*A–Clemency*). Digitized scan hosted at https://commons.wikimedia.org/wiki/File:The_International_Standard_Bible_Encyclopedia_Volume_1.pdf . Searchable scan text: https://upload.wikimedia.org/wikipedia/commons/c/c7/The_International_Standard_Bible_Encyclopedia_Volume_1.pdf . Independent transcriptions: https://bible-history.com/isbe/a/abissei and https://www.internationalstandardbible.com/A/amnon.html .

**Limit:** textual presence was corroborated in the scan's searchable text. A page-image inspection was attempted but the PDF screenshot service rejected this ~50 MB file; **the printed pages and exact lineation were not visually certified**. This is therefore not permission to copy either online transcription into the master. Exact printed page and PDF image index remain open.

Remaining 29 entries must be checked individually. An entry may be a real article, a source-key-only alias, a combined entry elsewhere, or a missing section; these possibilities cannot be decided from CrossWire alone.

## Non-content notice audit

The source-locked [full-corpus content scan](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45069147164), delivered by PR #10, matched 21 text units (24 occurrences), all with digital-process vocabulary such as `transcribed`, `transcriber`, or `scanned`. Many of these words describe the transmission of ancient manuscripts, a legitimate scholarly subject. **Zero automatically removable notes were established by this lexical scan.**

The canonical structure inventory currently has **no `note` elements** in its article markup; this does not prove that parenthetical/editorial prose or process notices are absent, only that there are no explicitly TEI-tagged notes. Further review should look for substantive prose islands, author signatures and suspicious introductions/end matter and should compare them with the historic printing, not rely solely on keyword matching.

### Next editorial gates

1. Identify the exact printed page and visually compare the 31 empty records against the 1915 scans. Start with the two attested missing entries, then proceed across volumes in batches.
2. Classify possible non-content notices as `historic-authored`, `historic-editorial-content`, `digitization-only`, `navigation-only`, or `uncertain`, with individual evidence.
3. For each approved addition/removal, record original/source and revised-text hashes and stable unit mapping. Reject changes to unaffected article text and IDs.
4. Validate the resulting separate editorial edition through pinned TEI P5 RELAX NG, Schematron and article-reference audit. Keep original digital witness intact.
5. Rights and translation publication remain blocked by #1 until separately cleared.
