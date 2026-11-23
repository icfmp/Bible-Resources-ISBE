# 1915 low-fourgram candidates: original-image prose spot-checks

> **Superseding 2026-11-23 image correction (PR #71):** The MEADOW v1/v2
> spot-check below misdescribes the original printed punctuation. Magnified
> original volume III PDF page 657 reads **“the meadows [AV “paper reeds”] by the Nile”**:
> square brackets, not parentheses, and no quotation closure after *meadows*.
> The original spot-check ledgers are retained for provenance; use the
> [all-24 v2 original-image review](1915-all24-english-prose-review.md)
> before any textual correction.


## Evidential scope

The source-locked five-volume OCR triage identifies **24 articles** with at
least 100 source Latin tokens, near-equal candidate OCR/source word counts,
and fewer than 25% of the original source's four-token phrases recalled.
These are **research candidates, not 24 certified textual errors**.
The original full PDF OCR and historical page positions are tracked in
[`1915-ocr-word-count-audit.md`](1915-ocr-word-count-audit.md).

The first two batches of **thirteen actual original page-image inspections**
document **fifteen bounded individual phrase discrepancies**, using images
from the SHA-locked
[original-image research run 45139297142](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45139297142).
The review ledger is
[`1915-low-overlap-prose-image-spotchecks-v2.json`](../workspace/reviews/1915-low-overlap-prose-image-spotchecks-v2.json).

| Article | Original 1915 volume / PDF page / printed folio | Bounded observation |
| --- | --- | --- |
| ABIDE | I / 33 / 9 | Three abbreviated `a.` usages are rendered `abide` in digital, despite printed past-tense or noun *abode* contexts. |
| MEADOW | III / 657 / 2013 | Expansion of `AV` disrupts quotation nesting in the digital reading. |
| REPAIR | IV / 474 / 2558 | Printed opening parenthesis and quotation before the Joel 3:16 quotation are absent from the digital reading. |
| HERB | II / 732 / 1375 | Opening quotation before *a garden of herbs* is missing in the digital reading. |
| JERUBBESHETH | III / 231 / 1595 | Printed *reluctance* differs from digital *reluctant*. |
| GAINSAY | II / 505 / 1153 | A literal digital `/APC` locator is not printed before the 2 Esdras citation. |
| VERY | V / 244 / 3048 | Printed `As advb.` becomes digital `As ab adverb`, introducing an extraneous `ab`. |
| LINE | III / 536 / 1894 | Opening parenthesis before `phthoggos` is missing digitally. |
| BELLY | I / 468 / 432 | Printed abbreviation `esp.` is expanded into digitally split `espec ially`. |
| WATERCOURSE | V / 270 / 3074 | Original printed *Jehovah* is replaced with *Yahweh* in the digital witness. |
| CONFUSION | II / 42 / 700 | Original *akatastasia* differs from digital *akatashatasia*. |
| JEUSH | III / 313 / 1675 | CrossWire inserts an extraneous comma in *that, of an Arabian lion-god*. |
| BUSINESS | I / 569 / 533 | Original Greek wording accompanies its transliteration; the digital witness has Latin-only text with added commas. |

## What is proved—and what is not

- Every reported **digital exact substring** is unique within its unmodified
  canonical TEI article and is checked against the source-locked, complete
  9,380-entry inventory. Each article ID, volume, original PDF SHA-256,
  research-image SHA-256, scan page and printed folio is recorded separately.
- The 1915 visual quotations are **direct image readings** of small segments.
  CI verifies their provenance metadata and the existing digital side, but
  does not re-read or independently certify the historical JPEG's wording.
- **This is not a full word-for-word or character-level collation of any
  entire article.** Greek/Hebrew, signatures, scripture references, all
  punctuation, remaining text, and other printed pages require separate
  comparison. None of the 24 candidates is closed as fully collated.
- Some differences are unmistakable digitization/prose artifacts; some
  abbreviation choices still need an editorial decision on the exact
  wording to restore in a separate historical witness. No automatic
  normalization or canonical source edit is proposed.
- There is a potentially **systemic digital locator issue**: in the immutable
  canonical XML, the literal string `/APC ` appears 158 times, spread
  across 111 article keys (including the printed-image-attested GAINSAY
  example). This raw count is a triage lead, **not 158 authorized deletions**.
  Occurrences inside scripture-reference markup and running text must be
  assessed separately, and a reproducible dedicated audit is still needed.

## Next stage

All **24 candidate starting-page images** have now been examined for initial triage, but only **13** have bounded recorded print/digital fragment differences. The other starting pages cannot be considered fully collated merely because no glaring first-page discrepancy was singled out. Revisit all relevant continuation pages and all article prose. Then collate **all 24 complete article bodies**
against the original facsimiles, including non-Latin text and punctuation.
Maintain independent, reversible editorial delta records with source and
historical witnesses before any change to a separately maintained 1915
edition. The CrossWire ZIP/IMP, canonical TEI and approved historical
edition stay untouched. Redistribution remains blocked by rights review #1.

## Individually attested noncanonical text corrections

Eight of the fifteen reviewed printed/digital snippets have a separately approved,
exact-source, markup-preserving corrective operation. Their independent
noncanonical TEI stage, strict regression checks, and seven deliberately deferred
snippets are described in [the print-backed prose delta report](1915-image-attested-prose-deltas.md).
This is not full-article collation; the 24 historical image comparisons remain open.
