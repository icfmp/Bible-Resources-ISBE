# Original 1915 ISBE: article-wide visual review queue

## Precise evidence boundary

The 24 substantial, similar-length, low four-gram-overlap candidates already
identified by the original five-volume OCR audit are now recorded in
[`1915-article-wide-prose-review-v1.json`](../workspace/reviews/1915-article-wide-prose-review-v1.json).
The register binds each original CrossWire article key and XML ID to the
canonical **9,380-entry**, SHA-256-pinned TEI, the historical volume PDF hash,
the exact PDF page, and the original-page JPEG digest from
[source-image research run 45139297142](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45139297142).

The scanned original pages were examined, not a newer ISBE revision.
The printed and digital witnesses must **not** be silently collapsed.

| Evidence category | Entries |
| --- | ---: |
| Source-locked low-overlap cases | 24 |
| Printed entry starts and ends on the **same available page** | 23 |
| Printed entry spans two *now examined* original PDF pages | 1: ZABUD, volume V PDF pages 328–329 |
| Entire English prose visually read against the digital entry in the current additional passes | **12** |
| Exact original-language glyph, diacritic, punctuation and complete article collation certified | **0** |

The twelve bounded article-wide **English-prose** passes are ABIDE,
BALTASAR, BELLY, CARPENTER, CONFUSION, IMAGINATION, OZIAS,
STOREHOUSES, SUMMER, VERY, YEA and ZABUD. The other twelve remain
prior **initial-page spot-checks**; seeing the end of an article on the
same page does **not** imply that every word was checked. The newly
recovered original ZABUD continuation is page 329, JPEG SHA-256
`cf6b05de09558a263f56f949f5ddcd9f334aa31a5c9cf7f6576b903699e8af7c`,
from [successful image research run 45204221240](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45204221240).

## Important emerging digital-fidelity risk

All 24 selected digitized articles have **zero Greek, Hebrew or Arabic script
characters** in their visible canonical text, while the inspected original
printed pages have such original-language script. Latin transliterations,
often accompanied by expanded AV/RV/OT/NT abbreviations, are not substitutes
for a faithful original-script transcription. In particular:

- CARPENTER: printed Hebrew and Greek original-language forms accompany
  the transliterated words in the headword, but the digital article retains
  only the Latin transliterations.
- CONFUSION: the already image-attested print *akatastasia* is corrupted
  to digital *akatashatasia* in addition to missing original-language script.
- ABIDE: printed abbreviation *a.* has multiple incorrectly expanded
  instances in the digital text.
- VERY: the printed *As advb. it is commonly* becomes the malformed
  digital *As ab adverb it is commonly*.
- ZABUD: the article starts at the foot of page 328 and finishes at the top
  of page 329, which has now been directly inspected; its Hebrew original
  spelling and punctuation remain **uncertified**.

For the other bounded findings, see
[`1915-low-overlap-prose-spotchecks.md`](1915-low-overlap-prose-spotchecks.md)
and the previously merged v1/v2 evidence ledgers. This register does not
reapprove any of their edits or turn them into complete collations.

## Validation

`scripts/validate_1915_article_wide_review.py` checks the whole canonical
source SHA-256, each source text SHA-256 and XML ID, article inventories,
five historical PDF hashes, print-page bounds and the exact uniqueness of
any digital quote used in the record. Negative tests reject fabricated
source quotes, duplicate or changed article identities, false completions,
source modifications, bogus page metadata and publication claims.
The historical page JPEG fingerprints are recorded from SHA-pinned
research artifacts (including the new ZABUD continuation); CI checks their format and historical PDF identity but
**cannot re-read the original JPEG or certify its printed wording**.

This is an English-prose research pass, **not** a completed critical
edition, a complete line-by-line multi-script collation or a release gate.
The canonical CrossWire ZIP/IMP/TEI, separate approved editorial witness
and actual publication rights remain unchanged. Follow-up full collations
must capture exact original Greek/Hebrew/Arabic, annotations, punctuation,
signatures and references with page-by-page proof, and perform a second
independent review. Publication remains blocked by rights issue #1.
