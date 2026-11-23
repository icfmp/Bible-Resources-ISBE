# 1915 ISBE: all 24 low-fourgram entries reviewed for English prose

## Completed bounded research pass

The original five-volume, SHA-256-pinned **1915** edition was examined directly
against the full digitized English visible prose for all **24/24** low-fourgram
candidates. The cumulative v2 ledger is
[`workspace/reviews/1915-article-wide-prose-review-v2.json`](../workspace/reviews/1915-article-wide-prose-review-v2.json).
The original v1 ledger, with its twelve previously completed readings and
historical page digests, remains unchanged and is linked by exact Git blob hash.

| Stage | Cases | What it actually establishes |
| --- | ---: | --- |
| Original 1915 page availability | 24/24 | All source pages needed for these articles, including ZABUD continuation |
| Complete English-prose original-image read-through | **24/24** | One AI-assisted English reading from article start to article end |
| Complete character-by-character historical original-language, punctuation, reference/structure collation | **0/24** | **None certified** |
| Historical redistribution permission | **No** | Blocked by issue #1 |

The twelve new whole-English-prose readings beyond v1 are **BUSINESS,
GAINSAY, HERB, JERUBBESHETH, JEUSH, LINE, MEADOW, PRESENCE, RECOVER,
REPAIR, WATERCOURSE, ZEBIDAH**. Earlier twelve were ABIDE, BALTASAR,
BELLY, CARPENTER, CONFUSION, IMAGINATION, OZIAS, STOREHOUSES, SUMMER,
VERY, YEA and ZABUD.

## Notable source/print problems

- **Original-language script:** In each of these 24 candidates the printed
  witness contains Hebrew, Greek or Arabic graphies while the original
  digitized canonical article's visible text contains none. The surviving
  Latin transliterations are not complete substitutes for the original
  scholarly material. This is a systematic *candidate-set* gap, not a
  statistical claim that every article in the entire 9,380-entry ISBE corpus
  lacks original-script text.
- **GAINSAY:** Four literal `/APC` digital navigation prefixes appear where
  the printed source has Apocrypha citations with no such machine marker.
  The printed `Ad Est 13 9` is not the same *displayed reference* as the
  digital `Additions to Esther 9:13` (which additionally has
  `cRef="Bible:Esth.9.13"`). Do not silently reinterpret the underlying
  apocryphal versification without researching this exact edition.
- **BUSINESS:** The original has the Greek `ἐν τοῖς τοῦ πατρός μου`
  **and** a Latin transliteration; digital `en, tois, tou patros mou`
  drops the Greek and introduces extraneous commas.
- **MEADOW — correction of our own v1 spot-check:** the original printed
  phrase reads `“the meadows [AV “paper reeds”] by the Nile”`.
  The earlier limited-image transcription in the immutable v1 observation
  described parentheses and a closing quotation after *meadows*.
  **This was an error in the research transcription**, established by a
  higher-magnification inspection of the original volume III PDF p657 image.
  Use the superseding v2 reading for any future editorial decision;
  the earlier version is retained as a traceable superseded observation.
- **REPAIR:** the original printed opening parenthesis/quotation around the
  AV quotation is missing in the source; exact historical punctuation must
  be restored in a separate reversible delta if and only if source-image
  attested.
- **YEA:** previous v1 found a digital unmatched `]` in a citation where
  the printed closing mark is `)`.

## Safeguards

`scripts/validate_1915_article_wide_review_v2.py` checks the complete
canonical 9,380-entry source identity, pins the unmodified v1 JSON via its
actual Git blob hash, preserves all 24 source IDs, full digital article hashes,
original historical PDF page/JPEG provenance, and checks all digital excerpts
for unique literal occurrence. It refuses any invented blanket
original-script fidelity, editorial change or release approval.

The digital source ZIP/IMP and canonical TEI remain immutable. The eight
previously attested prose corrections from
[PR #69](https://github.com/icfmp/Bible-Resources-ISBE/pull/69)
remain in their **separate editorial stage**, not silently pushed back into
the CrossWire original.

## Remaining independent, exact print collation

The entire Greek/Hebrew/Arabic graphy, accent/diacritic inventory, punctuation,
scripture display and navigation, article divisions, original contributor
signatures, and scholarly typography still need word-by-word comparison before
calling any of the 24 historically print-faithful. All changes belong in
source-image-bound, individually reversible deltas and require a separate
independent reading. The entire 9,380-entry print-content audit (#9), original
historical rights (#1), and publication remain **open**.
