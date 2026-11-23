# Original 1915 ISBE GAINSAY: Additions to Esther 13:9, not Esther 9:13

The primary source **ISBE 1915, volume II printed folio 1153** (original PDF
page 505) reads **`Ad Est 13 9`**, after the earlier `Jth 12 14` citation,
and before the Greek verb antitassō.

Exact original volume II PDF SHA-256
`e8ad1d382b79ee40701983ffee89201193585a0e4542fb0c52b99cbff6ad2cb1`,
research source JPEG SHA-256
`88f820a4945cb7c8a5c8561ece0f1f015dc79b79a1724fcd4ca97f63556b3976`
([first original page image research run](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45139297142)).
The earlier source's digitized visible sequence is
`Additions to  Esther 9:13`; its original source scripture
`<ref>` has XML ID `isbe-b892edd68cfa282dd67e-n000006`
and `cRef="Bible:Esth.9.13"`.

This is a wrong biblical **target**, not a harmless formatting issue.
The [1611 KJV](https://www.kingjamesbibleonline.org/Additions-to-Esther-Chapter-13_Original-1611-KJV/)
and the [1895 RV](https://ebible.org/eng-rv/ESG13.htm)
both contain *gainsay* in **Additions to Esther 13:9**. The official
[CrossWire OSIS abbreviations](https://wiki.crosswire.org/OSIS_Book_Abbreviations)
use **`AddEsth`** for this *separate* Apocrypha book; CrossWire's
[versification note](https://crosswire.org/pipermail/sword-devel/2024-February/049959.html)
warns that some Bible editions place additions differently. **Do not invent
a mapping to canonical Hebrew Esther 9:13 or change the original verse number.**

## Single exact, separately generated correction

The edition stage **after** the approved sixteen print-word deltas changes
one sibling-pair of XML slots in the source-locked and reviewed paragraph:

- previous reference tail ends `...; Additions to  ` → `...; Ad `
- next reference visible text `Esther 9:13` → `Est 13 9`
- same stable reference's cRef `Bible:Esth.9.13` → `Bible:AddEsth.13.9`.

The original complete visible string therefore becomes **`Ad Est 13 9`**,
without a new article, a new verse, changing any other reference or
altering CrossWire's source text. A Bible reader that lacks the apocryphal
book `AddEsth` may be unable to navigate to the target, but **must not
silently jump to an unrelated Esther 9:13**; book availability is separate
from metadata correctness.

All edits are individually reversible and tied to one precise
[versioned ledger](../workspace/reviews/1915-gainsay-additions-esther-reference-v1.json)
with exact original PDF/JPEG, original stable XML IDs, source-target pairs,
and prior paragraph SHA-256. The target cannot be applied if the preceding
16-correction noncanonical editorial layer SHA-256 changes. The script
validates that the exact old paragraphs and adjacent ref slots exist, changes
no unrelated article or XML ID, checks reverse serialization, and
serializes a new nonpublishable TEI under `workspace/tmp/`.

The existing full editorial reconstruction workflow additionally checks both
official pinned TEI P5 RELAX NG and Schematron validators on the newly
generated separate edition, without changing the immutable canonical source.

**This is not a 24-article complete original-script collation, not an
independent human peer review, and not publication permission.**
Issue #9 remains open; rights #1 still blocks redistribution.
