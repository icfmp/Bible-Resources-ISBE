# Original 1915 ISBE OCR / TEI article word-count triage

## Purpose and baseline

The first all-volume comparison is a **count-based anomaly detector**, not
a critical edition, character-level collation or publication permission.
It compares all 9,380 source article identities and counts the portion
whose boundaries can be conservatively determined in the original printed
PDF OCR layer. Source input is the unchanged SHA-pinned canonical
`cleaned/en/ISBE.xml`; the independently corrected, noncanonical editorial
witness is **not** silently substituted for that baseline.

The five source PDFs and digests are fixed in
`sources/print/1915-volume-witnesses.json`; volume V is known to lack
printed folios 2887–2888 in this particular digitization. Those pages
cannot receive print certification based on the present scans.

## One extraction, two-column aware, per volume

`scripts/audit_1915_article_ocr_word_counts.py`:

1. Confirms PDF and canonical TEI SHA-256 digests before comparing.
2. Runs `pdftotext -bbox-layout` **once** for that full volume, using the
   existing embedded OCR layer, not Tesseract or another image OCR pass.
3. Reconstructs printed reading order column-wise using the bounding-box
   coordinates, while excluding typical running headers/page furniture.
4. Locates source headword candidates only if an original uppercase heading
   matches a unique normalized TEI key. Multiple candidates, duplicate
   normalized keys and alphabetical order inversions remain unresolved.
5. Assigns an OCR article count **only between two consecutive TEI entries**
   whose original heading candidates have both been aligned. An article
   whose next boundary is ambiguous or missing is not assigned a count.
   This strict gate avoids making a large chapter look artificially complete
   by absorbing an adjacent article.
6. Subtracts the printed headword from the counted segment, and excludes
   the synthetic `head type="index"` from the canonical TEI count.

The word-count definition on **both** sides is deliberately conservative:
NFKD normalization followed by ASCII Latin/digit tokenization
(`[a-z0-9]+`). This excludes non-Latin Greek and Hebrew, punctuation and
typographic fidelity; it can split apostrophes differently from a human
word count. There are also inevitable OCR errors and difficult book
structures (e.g. tables, illustrations, inline subheadings and unusual
column arrangements).

## Statuses are not proof of fidelity

Each article has its **TEI word count** and one of these research-only
statuses:

- `unresolved_print_boundaries`: no reliable per-article OCR number;
  **never** fill it in with a plausible guess.
- `ocr_count_near_source_candidate`: comparable OCR count within 10% of
  source TEI; candidate for lower-priority review, **not verified text**.
- `ocr_count_diff_over_10pct_candidate`: candidate for higher-priority
  image comparison; the difference may be OCR/layout noise, not a bad TEI.
- `source_empty_print_ocr_nonempty`: candidate source omission; compare
  with separately restored 31-entry witness before concluding anything.
- `both_zero_candidate`: both counts zero, but neither witness certified.

Every row explicitly states `visually_verified=false` and
`full_print_text_certified=false`. No output from these scripts ever
authorizes text deletion, repair, publication or full original-print
certification. A true correction requires a separate exact-image
collation, page-image SHA, editorial ledger and source-locked reversible
transformation in the **separate edition**.

## Running and collecting evidence

The `.github/workflows/audit-1915-article-ocr-word-counts.yml`
workflow runs preflight unit tests, then five jobs in parallel.
Each volume PDF is downloaded once and compared in one extraction
pass; only count/evidence reports are uploaded, not the entire copyrighted
or potentially restricted original OCR text.

Local equivalent, for an already obtained source PDF:

```bash
python3 -m scripts.audit_1915_article_ocr_word_counts \
  --volume 1 --pdf /path/to/original-1915-vol-1.pdf \
  --report workspace/tmp/1915-ocr-wordcounts/volume-1.json
```

The matrix merge verifies that all five original print witness digests,
all 9,380 TEI keys and identifiers, individual status invariants, and
noncertification flags agree, then produces
`1915-ocr-word-counts-overview.json` with per-volume coverage and
50 highest relative count-difference candidates.

**Important limitation:** the pilot is expected to leave many articles
unresolved because source keys and historic printed headings can differ
or the OCR does not preserve a usable headword. Coverage must be
measured first. Improving matching confidence is separate follow-up
work; do not relax evidence gates merely to inflate a dashboard metric.

## Interpretation

The first evaluation is: *how many article boundaries are trustworthy,
and how often do their coarse Latin word counts differ sharply?*
This can rank later visual collation work dramatically faster than a
manual, serial reading of all 9,380 articles. It cannot demonstrate
that prose, punctuation, references, Greek/Hebrew, scholarly decisions
or article divisions match the original 1915 print.

## Initial five-volume research result (2026-11-23)

The **full** [Actions run 45132413080](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45132413080) passed for all five original print witnesses, with unit tests and the exact 9,380-source-entry consolidation gate. Results below refer to the **source-faithful canonical TEI** (not yet the separate, 31-restoration-and-further-corrections editorial candidate).

| 1915 volume | Source TEI entries | OCR counts assigned | Extract existing OCR text (s) |
| --- | ---: | ---: | ---: |
| I | 2,145 | 1,394 | 3.67 |
| II | 2,129 | 1,287 | 3.22 |
| III | 1,908 | 1,146 | 4.32 |
| IV | 2,009 | 1,234 | 4.33 |
| V | 1,189 | 720 | 2.47 |
| **Total** | **9,380** | **5,781** | **18.01 (sum; jobs parallel)** |

The extraction seconds measure **only Poppler's extraction pass after downloading each verified PDF**, not download, XML parsing or total CI runtime. The five-volume workflow ran in parallel. It does not imply a two-second *review* of individual articles.

Among 5,781 entries with two OCR heading boundaries resolved in source order:

- **3,926** have normalized Latin token counts within ±10% of source TEI.
- **1,837** differ by more than 10%; this is a **review queue**, not an error count.
- **18** are empty in the immutable digital-source TEI but nonempty in these OCR spans. These must be reconciled against the already separately recovered 31 historical entries before treating as new defects.
- **3,599** source entries remain `unresolved_print_boundaries`; no OCR word counts were invented for them.

Some of the highest-ratio candidates involve a very short digital redirect and a long apparent print span (e.g. `PROPERTY`, `COUTHA`, `WINDOWS OF HEAVEN`). These require **image/heading-boundary review first**; an extreme numerical difference is not yet evidence of a several-thousand-word digital omission. This is deliberately a first-stage *coherence check*, not exhaustive character-level collation.

The per-volume row reports and the combined top-50 discrepancy overview are uploaded as **research-only** Actions artifacts; the historical OCR text itself is not included in the artifacts. Follow-up should improve heading alignment with grounded neighboring text/visual checks and compare the separate approved editorial witness, preserving the source-locked canonical baseline for reproducibility.
