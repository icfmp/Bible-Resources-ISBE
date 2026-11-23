# Original 1915 ISBE: eight bounded prose corrections in a separate TEI

## Scope and provenance

This stage follows the already generated noncanonical 1915 edition with 31
restored source-empty articles, six print deltas, twelve Scripture-navigation
repairs, one printed Scripture continuation correction, and one display-only
TAANACH navigation repair. **No preceding layer or CrossWire source is edited.**

The independent original-page observations were recorded in
[`1915-low-overlap-prose-image-spotchecks-v2.json`](../workspace/reviews/1915-low-overlap-prose-image-spotchecks-v2.json)
after inspecting SHA-locked images from the
[1915 source-image research run](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45139297142).
Each operation is tied to the exact original PDF digest, rendered page JPEG
digest, original article and paragraph XML IDs, unique digital text span,
and **exact attested printed replacement**, in
[`1915-approved-low-overlap-prose-deltas-v1.json`](../workspace/reviews/1915-approved-low-overlap-prose-deltas-v1.json).

| Original article | Original printed vol. / PDF page | Difference addressed |
| --- | --- | --- |
| BELLY | I / 468 | Digital broken `espec ially` → printed `esp.`. |
| CONFUSION | II / 42 | Digital malformed `akatashatasia` → printed `akatastasia` (and original printed `Gr` abbreviation). |
| HERB | II / 732 | Restore printed opening quotation before `a garden of herbs`. |
| JERUBBESHETH | III / 231 | Grammatical `reluctant` → printed `reluctance`. |
| JEUSH | III / 313 | Remove spurious comma after `that`. |
| LINE | III / 536 | Restore parenthesis before `phthoggos`. |
| VERY | V / 244 | Digital `As ab adverb` → printed `As advb.`. |
| WATERCOURSE | V / 270 | Digital `Yahweh` → printed `Jehovah` within the individually attested quotation. |

The corresponding exact before/after phrases, not the shortened examples above,
are required by the machine-readable ledger. **These eight fragment repairs
do not certify the complete content of any article.** They are AI-assisted,
visually attested editorial decisions, not independent scholarly peer review.

## Deliberately deferred

Seven further snippet-level differences across **ABIDE** (three),
**MEADOW**, **REPAIR**, **GAINSAY**, and **BUSINESS** remain recorded but not
automatically modified. They involve ambiguous historical shorthand,
quotation-boundary interpretation, digitization locators, or missing original
Greek; some may need markup-aware operations or broader editorial policy.
Do not perform global `/APC` deletion, indiscriminate divine-name rewriting
or wholesale Greek transliteration. All 24 low-raw-overlap candidates remain
open for whole-article image collation and continuation-page review.

## Reproducible application

`scripts/apply_1915_low_overlap_prose_deltas.py` creates a **new distinct
TEI file** from the exact hash-validated preceding editorial candidate,
and refuses to overwrite the canonical source or prior witness.
It rejects missing/duplicate original snippets, changes crossing TEI markup
boundaries, mismatched witness PDF/image checksums, substituted article or
paragraph IDs, and unapproved/missing evidence. Every operation is reversible:
the script verifies that restoring the original slot restores the article
serialization byte for byte, and that all unrelated articles and all original
XML IDs are preserved. A full serialized TEI structure check follows.

`.github/workflows/validate-1915-textual-reference-deltas.yml` rebuilds
all earlier tiers, runs positive and adversarial tests, applies these eight
changes to the newly produced noncanonical copy, then validates it against
the pinned official TEI P5 RELAX NG and Schematron schemas. Artifacts are
**research only and not for publication**.

This is not release approval. The historical copyright/redistribution review
remains open in [issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1),
and the complete critical content collation in
[issue #9](https://github.com/icfmp/Bible-Resources-ISBE/issues/9).
