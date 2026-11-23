# Sixteen further individually reversible 1915 image-attested printed readings

This step extends—not replaces—the **separate, noncanonical** 1915 editorial
ISBE witness after the [previous eight source-image print corrections
(PR #69)](https://github.com/icfmp/Bible-Resources-ISBE/pull/69).
It leaves the CrossWire ZIP/IMP, the 9,380-entry canonical TEI, the 31 separately
restored source-empty entries, Scripture-navigation repairs, and all earlier
editorial outputs untouched.

## Source-confirmed printed-vs-digital differences

| Article | Corrected fragments | Exact scope |
| --- | ---: | --- |
| ABIDE | **8** | Seven false expansions of printed `a.` with original square brackets **or parentheses as actually printed**, plus one printed Greek `μονή` and transliteration restored |
| BUSINESS | 1 | Original **Greek plus transliteration** `ἐν τοῖς τοῦ πατρός μου, en tois tou patros mou`, not the malformed digital Latin-only expression |
| GAINSAY | 4 | Four exact printable Apocrypha citation spans containing unprinted electronic `/APC` markers |
| MEADOW | 1 | Historical quotation with **square brackets** `[AV “paper reeds”]` |
| REPAIR | 1 | Original AV abbreviation and restored quotation parentheses around Joel 3:16 |
| YEA | 1 | Printed closing parenthesis `)` instead of digital unbalanced `]` |
| **Total** | **16** | **Six articles** |

This **supersedes the incorrect earlier MEADOW image-reading inference**:
on the magnified original volume III PDF page 657 the printed passage uses
square brackets, **not parentheses**, around the abbreviation AV and quoted
*paper reeds*. The original v1/v2 research records remain in Git history to
show the correction of the research itself.

In GAINSAY, **do not conflate** an accurately read `Ad Est 13 9` with
digitized `Additions to Esther 9:13`. The displayed reading and its
`Bible:Esth.9.13` target remain untouched pending a separately documented
versification decision. Likewise, no systematic deletion of other `/APC`
occurrences is authorized: these **four exact printed citations** only. A magnified original ABIDE image also corrects our earlier spot-check description: `There he a.` is followed by **(dwelt)** in parentheses, not `[dwelt]`.

## Exact provenance and reversal

The [versioned decisions](../workspace/reviews/1915-additional-exact-print-deltas-v1.json)
pin each original printed page and JPEG SHA-256, the exact prior paragraph
text SHA-256, the stable article/paragraph/ref XML IDs, the `text` or `tail`
slot, the old phrase and its image-attested replacement.

`scripts/apply_1915_additional_prose_deltas.py` verifies the source canonical
SHA-256, the previous **eight-correction** editorial output SHA-256,
the 24-entry image research ledger, each original paragraph and XML text
slot, and literal uniqueness before performing a single substitution.
It reverses **all ten** in memory and proves byte-equivalent
serialized article restoration before reapplying the final new layer.
The resulting file retains the exact same 9,380 article IDs/order and all
unaffected serialized article contents, and passes the project strict TEI
profile.

The existing reproducible full editorial GitHub Actions workflow builds this
new, explicitly nonpublishable TEI and validates it against the pinned
official TEI P5 RELAX NG and Schematron schemas. Negative tests reject changed
printed image hashes, fake text, nonexistent XML slots, duplicate operations,
release approvals, bulk substitutions, and silently re-targeted references.

## What this does not certify

These sixteen small original-print restorations do **not** certify the entire
text, punctuation, original languages, notes, signatures, reference locations
or editorial choices of all 24 English-reviewed articles. The source-print
glyph-by-glyph verification remains separately open under [issue #9](https://github.com/icfmp/Bible-Resources-ISBE/issues/9);
copyright and redistribution remain blocked by [issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1).
