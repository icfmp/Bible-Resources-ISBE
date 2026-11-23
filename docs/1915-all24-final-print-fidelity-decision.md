# Final 24-case original-print exact-fidelity decision — 1915 ISBE

This document **closes the yes/no fidelity assessment** of the 24
similar-length, low-fourgram original-1915 ISBE candidates. It does
**not** claim that every Greek/Hebrew letter, accent, note, biblical
reference and punctuation character has been transcribed from the print.

## Decisive outcome

| Criterion | Result |
| --- | ---: |
| Source article identities SHA-locked | 24/24 |
| Original 1915 printed pages available (including ZABUD continuation) | 24/24 |
| Original-printed English prose read through | 24/24 |
| Complete digital article compared against its original PDF text-layer physical print interval | **24/24** |
| Unambiguously faithful, exact original 1915 printed articles | **0/24** |
| Exact print fidelity **rejected** due to missing original-script glyphs | **24/24** |
| Complete letter-by-letter original-print transcription and punctuation/references certification | **0/24** |
| Automatically approved additional corrections | **0** |

**All 24 articles fail the exact original-print reproduction criterion.**
The original 1915 printed page contains original-language Hebrew/Greek/other
non-Latin letters while the canonical digital visible text for **each of these
24 entries** has zero characters from the original-script categories.
A definitive **failure** only requires one genuine source difference;
there is no need to invent a word-for-word restoration to reach this decision.

This is not evidence that the digitized resource lacks every text passage.
It is evidence that **literal printed-edition fidelity is not established
and in fact is disproved** for this candidate set.

## Complete original PDF text-layer alignment

The original **five 1915 PDF scans** were SHA-256 verified before
`pdftotext -layout` extracted the page text layer for every requested article.
The results are from
[original-page run 45220031270](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45220031270),
and are reproduced by the new GitHub Actions research workflow and source checks.

The [comparison ledger](../workspace/reviews/1915-all24-print-layer-whole-article-comparison-v1.json)
records for every article its exact immutable digital text SHA-256 and XML ID,
original printed PDF volume/page, source-page JPEG SHA-256, the page/column
physical extraction spans and original text-layer region SHA-256, distinct
Latin-token counts, raw fourgram recall and whether the source content covers
the available OCR print span.

**All 24 original digital articles have a complete corresponding
printed region in the machine text layer.** The printed-text-layer to digital
word-count ratios range from **0.8896 to 1.0964** after resolving column
transitions. This is numerical evidence against a wholesale multi-paragraph
omission in this selected group. It is **not** proof of textual identity:
historical abbreviations, modern digital substitutions, machine OCR noise,
punctuation changes and missing original-script glyphs remain.

Two previous apparent incomplete printed comparisons, **JERUBBESHETH** and
**RECOVER**, were caused by omitted top-of-second-column intervals. The exact
physical boundaries were corrected: print-vs-source ratios moved to **0.9932**
and **0.9598**, respectively. Neither finding justified any textual edit.

## What is complete vs not complete

The **fidelity verdict** for these 24 candidates is finished and unambiguous:
**24 rejected as exact printed editions; zero approved**. The
[individual source/photo SHA-bound failure decisions](../workspace/reviews/1915-all24-print-fidelity-disposition-v1.json)
are checked by `scripts/validate_1915_print_fidelity_disposition.py` with
negative tests that prohibit inventing full historical certifications or
automatically editing the canonical source.

The **separate task of reconstructing every missing historic glyph** has
NOT been finished. It requires comparison at actual page-image resolution,
transcription and independent checking of all Greek/Hebrew words, historical
punctuation, source footnotes, verse numbering, marginal apparatus and other
original typography. The PDF text layer is not an authoritative primary
transcription for this purpose. A rejected edition and a fully reconstructed
edition are two different milestones.

Already source-backed textual edits were applied only to separately
generated noncanonical editions via [PR #72](https://github.com/icfmp/Bible-Resources-ISBE/pull/72),
and the specific printed Additions to Esther 13:9 reference via
[PR #74](https://github.com/icfmp/Bible-Resources-ISBE/pull/74).
Neither makes the complete historical text print-identical.

The CrossWire ZIP and IMP, canonical cleaned TEI, and previous editorial
layers remain unchanged. **Redistribution is blocked** pending rights
[issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1).
The wider source/content audit of all **9,380** ISBE entries
[issue #9](https://github.com/icfmp/Bible-Resources-ISBE/issues/9)
remains open. No historical or scholarly approval is fabricated.
