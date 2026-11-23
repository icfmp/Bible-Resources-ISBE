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

## Conservative title-disambiguation second pass (2026-11-23)

[PR #59](https://github.com/icfmp/Bible-Resources-ISBE/pull/59)
adds a second **read-only, still-uncertified** OCR alignment stage, without
relaxing the original unique uppercase monotonic heading anchors.

- Repeated printed headwords: may be used only when **exactly one**
  occurrence lies between two already accepted strong anchors, and the
  occurrence is an exact standalone title or has corroborating opening
  prose (at least three ordered distinctive Latin tokens).
- Lowercase/title-case OCR headword candidates: only exact title lines
  with that corroborating nearby source opening, again strictly bracketed
  by two independently strong anchor points. Weak headings never override
  a strong match or gain full-printed-text certification.
- Unresolvable boundaries remain explicitly uncounted. The source ZIP,
  canonical TEI and accepted editorial TEI layers are unchanged.

The [fully successful five-volume pilot, run 45134232593](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45134232593),
measured **5,857 comparable canonical source article counts**, compared
with 5,781 in [PR #58](https://github.com/icfmp/Bible-Resources-ISBE/pull/58):
**76 newly comparable articles**, and 3,523 still unresolved. Among the
comparable group, 3,981 counts were within 10%, 1,858 differed by more
than 10%, and 18 original source-empty entries contained nonempty
printed OCR spans.

All **18** of the latter matched the exact previously approved **31
original-source-empty restorations** in the versioned, separate 1915
editorial witness. This eliminates **new** unknown empty-article alerts
**within the subset successfully delimited by this scanner**; it does
not exclude other omissions among the 3,523 unresolved articles, nor
certify any printed wording or rights.

The aggregation now also ranks **substantive source articles** with
large absolute count differences separately from tiny digital redirects.
Huge raw ratios (e.g. 11 TEI words against thousands of OCR words) are
*reasons to verify the printed boundaries first*, not automatic
approval to restore allegedly omitted prose.

Remaining audit: improve alignment for other distinct historical
headword styles, review actual source page images for high-priority
long-form discrepancies, and compare the independently approved
editorial TEI against source OCR without replacing the immutable
source-faithful baseline.

## Content coherence: original TEI vs printed OCR four-token sequences

The follow-up audit retains exactly the same five pinned PDF scan sources,
conservative article-boundary rules, and **numeric article word counts**.
It additionally compares **ordered four-word sequences** in the Latin
tokens of the digital-source article and its purported printed OCR span.

- Source four-gram recall: the proportion of source TEI four-token runs
  also observed in the OCR article, including repeated runs only as often
  as they really occur. Low recall is a candidate for transposition, a
  wrong boundary, or a genuinely different article or source reading.
- OCR four-gram precision: the proportion of OCR four-token runs also
  occurring in the source. High source recall with low OCR precision can
  indicate additional printed prose, but also an OCR boundary that
  swallowed unrelated material.
- Both metrics are unavailable for empty or fewer-than-four-token
  spans. Greek/Hebrew script and punctuation still require direct
  printed-image collation. OCR hyphenation, column layout and textual
  conventions can greatly lower scores, including for perfectly
  faithful source text.

A **near-equal word count with low four-gram recall** is separately
flagged if the source has at least 100 Latin tokens and source recall
is below 0.25. Longer OCR spans with at least twice as many words
and at least 0.60 source four-gram recall form a distinct research
shortlist. Both thresholds prioritize human review; neither
justifies an editorial correction or a published text.

Only counts/scores, source keys, article identifiers and source-page
locations are persisted in Actions reports. Full OCR or article prose
is **not copied into audit artifacts**. The original CrossWire source
and separately edited 1915 witness remain unchanged.

### First five-volume lexical-coherence result (2026-11-23)

The SHA-locked [GitHub Actions run 45135114531](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45135114531)
passed all five volumes and 9,380-entry consolidation, with unchanged
conservative word-count coverage: 5,857 comparable article spans, 3,523
unresolved, 1,858 >10% count differences, and 18 source-empty entries
already included among the 31 separately approved restorations.

The four-token overlap adds two more **human-review queues**:

- **24** substantial source entries (at least 100 Latin words) have OCR
  word counts within 10% but less than 25% source four-gram recall.
  Examples in the research report include `MEADOW` (266 vs 242 words;
  recall 0.0989), `REPAIR` (128 vs 128; recall 0.1440), and `PRESENCE`
  (165 vs 155; recall 0.1543). A near-equal length plainly does not
  prove equal text.
- **9** substantive entries have at least double the number of OCR words
  but retain at least 60% of the TEI source four-grams. For example,
  `JOHN THE BAPTIST` has 3,004 TEI Latin tokens vs 15,427 in its
  **candidate** OCR span, source four-gram recall 0.7251 and OCR precision
  0.1411. This combination is consistent with the source prose
  appearing inside an overly long candidate span, but **does not establish
  whether the printed article is longer or the boundaries were wrong**.
  Inspect original page images before interpreting the difference.

These lexical checks are fully **read-only**. They do not change the
CrossWire input, TEI source/paragraph structure or previously approved
separate historical edition. The two queues overlap the count-based
queues and must not be added together as distinct confirmed errors.
They are candidates for reviewing original images and OCR layout, never
automatic approval for edits or publication.

## Reproducible review dossiers for the 24 + 9 candidate queues

The next audit builds a **bounded, automatic evidence dossier per flagged
article** from the same original PDF extraction; there is **no second
download or OCR pass**. This lets researchers prioritize printed image
inspection without publishing entire OCR transcriptions or silently
editing the canonical TEI.

The source-locked report contains one record for every qualifying
candidate: the exact source article key and stable XML ID; the candidate
category; PDF page numbers and the following known article title;
normalized word counts and separate SHA-256 fingerprints of the source
and OCR tokens; page-by-page OCR word-count distribution; and normalized
source recall for unigrams, bigrams, trigrams and four-grams.

For long OCR spans, a separate localization algorithm selects
four-word sequences that occur **exactly once in both witnesses** and
finds the shortest OCR interval containing 80% of these unique matches.
If there are fewer than twelve such correspondences, the localization
remains explicitly null rather than speculating about a target.
The report records the span offset and PDF page bounds of the
localization candidate, never quotes or reconstructs historical prose.

These diagnostics can help distinguish two kinds of *hypothesis*:

1. A long OCR span in which most source-specific phrases occupy a
   relatively compact region may have swallowed adjacent print material.
2. An article with similar source/OCR length but low four-gram recall
   can be checked at the one-, two- and three-word levels to assess
   whether OCR word order or an actual variant needs source-image review.

**Neither explanation is automatically accepted.** A reproduced OCR
position remains only a digital transcription-layer observation; it
does not prove that the printed page has a particular article boundary.
Every report explicitly sets page images reviewed = false, textual
correction authorized = false, and publication permitted = false.
Historical page-image verification and the independent rights review
remain open. The strictly immutable CrossWire ZIP/IMP and canonical TEI
remain unchanged.

The aggregator checks that every one of the selected cases has a
matching, nonduplicated evidence dossier, verifies original volume and
canonical source hashes, ensures exact article IDs, reconciles per-page
token totals with known OCR counts, rejects extra unapproved fields
that could leak OCR text, and refuses machine-claimed print
certification.

## Correcting a systemic error: physical printed entry order can differ from CrossWire index order

Direct image inspection of SHA-pinned facsimiles showed that *even two
individually located article headings are insufficient* to calculate an
article length by subtracting their OCR positions when their order
follows a digitally sorted source index, rather than the historical
print. In the 1915 printed volume, an independently titled entry can
appear **between** two adjacent CrossWire keys.

Three original printed-image examples (see the separate, reversible
headword-only observation ledger
`workspace/reviews/1915-ocr-print-heading-visual-inspection-v1.json`):

- **JOHN THE BAPTIST**, vol. III PDF page 346 (printed 1708):
  it concludes in PDF page 349 (printed 1711), immediately followed
  on that printed page by **JOHN, THE EPISTLES OF**. The *digital-key
  next article* JOHN, GOSPEL OF begins at PDF page 358 (printed 1720).
  The previous candidate span to p358 included multiple other entries,
  not a proven 12,423-word omission from CrossWire.
- **JOSEPH BARSABBAS**, vol. III PDF page 380 (printed 1740):
  its text finishes top of the right column and **JOSEPH, HUSBAND OF
  MARY** begins on that same page; a digital-key-order interval running
  to another Joseph title must not be trusted as a word count.
- **PHARAOH HOPHRA**, vol. IV PDF page 271–272 (printed 2359–2360):
  **PHARAOH-NECOH** begins on p272 before the printed
  **PHARAOH'S DAUGHTER**, contrary to digital index order.

Two further direct image checks of title boundaries were recorded for
**MEADOW** (vol. III p657, printed 2013) and **REPAIR** (vol. IV p474,
printed 2558). For these, the immediate printed titles do appear
distinct and the low four-gram recall cannot simply be attributed to a
visually evident intervening printed headword. **Neither article's
full wording has been visually certified.**

To prevent recurrence **generically** and without special-casing these
five keys, the OCR scanner now looks for uniquely recognizable, strongly
structured printed headings between every pair of proposed source-key
article boundaries. For a competing original printed heading, it
**withdraws** the originally calculated OCR count and lexical scores
and marks the source article as
`unresolved_intervening_print_heading`. It retains the original source
ID and numbers/pages of intervening printed titles for later image
inspection. Only machine-readable, uniquely attested OCR headings
under strict syntax constraints can trigger this protective quarantine;
the image-review ledger documents separately what was really seen.

### First corrected full five-volume pass

The [source-locked full original print OCR run 45140687212](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45140687212)
passed for 9,380 digital entries and all five original print witnesses.
It detected **89** potentially contaminated source-order article
intervals and withdrew their numerical results:

| Measure | Before print-order guard | After guard |
| --- | ---: | ---: |
| Canonical source articles | 9,380 | 9,380 |
| OCR-count-comparable source articles | 5,857 | **5,768** |
| Unresolved original print boundaries | 3,523 | **3,612** |
| Overlong OCR / source-fourgram-rich cases | 9 | **6** |
| Similar count / low fourgram recall cases | 24 | **24** |

**More conservative coverage is a deliberate quality improvement.**
The 89 cases are *OCR-based possible print-order conflicts*, not 89
historical manuscript defects or 89 image-certified conclusions. The
three examples above are separately visually checked for printed
heading/boundary differences only. The 31 restored historical entries
and 1915 CrossWire/canonical TEI original remain unmodified. Future
research should check further original-page images and never
automatically infer an omitted original article from source-index
word-count differences.

The validator
`scripts/validate_1915_ocr_print_heading_visual_inspection.py`
compares the limited heading observations against the canonical
9,380-key index, the historical volume PDF SHA-256 manifest, the
rendered image SHA-256 and source page/folio metadata, and explicitly
rejects textual-correction, print-content and publication claims.

## Print-alias typography and midpage alphabetic sections (2026-11-23)

A further direct review of original 1915 printed images found that several
remaining high-ratio OCR comparisons were **not evidence of source omissions**.

Historical printed titles often present both a capitalized headword and
its pronunciation on one line, or multiple capitalized synonyms
interspersed with separate pronunciations. CrossWire stores some of these
as **semicolon-separated source keys**. For example, the original print
has independent headings for `ANTICHRIST`, `COCKATRICE`,
`CHILD; CHILDREN`, `FAITHFUL; FAITHFULNESS`, and
`OBEDIENCE; OBEY`. The previous guard recognized some
multiword headings but missed these single-word and interrupted compound
headwords.

The generic recognizer now accepts strongly typographic, uppercase,
punctuation-delimited single-word headings and a semicolon-separated
source key **only if each separately named printed component is itself
uppercase and on the same OCR line**. Uncertain, multiple and ordinary
prose occurrences remain untrusted. A recognized title inside two
digitally neighboring article heads continues to **quarantine** the
candidate word count, rather than silently redrawing the article boundary.

### Independent two-column layout finding

On original volume V, PDF page 240 (printed folio 3044), the letter
**V** is printed as a centered, full-width alphabetic section heading
midway down the page. The top two columns still contain the end of
`UZZIEL`, whereas the lower two columns begin the new V entries.
Reading the entire left column followed by the entire right column
wrongly inserted upper-right UZZIEL prose into the `VAIN` entry.

The new **source-agnostic page-band reader** accepts an alphabetic
section break only when all of these original OCR geometry conditions
hold:

- A single uppercase Latin letter is centered on the page and
  significantly larger than its own page's typical text glyph.
- Both columns have a sufficiently wide vertical whitespace gap at
  the candidate section.
- A strong, uppercase, punctuation-delimited headword beginning with
  **the same letter** appears promptly in the lower left section.

The reader processes upper-left/upper-right and then
lower-left/lower-right. It **does not erase** an isolated letter that
fails these checks. It reports every selected source page and letter,
with `image_verified: false` until an original page image is actually
reviewed. Only the V case is separately image-attested in the visual
review ledger; the scans additionally nominate III p752 N and
IV p436 R for future visual checking. The first looser geometric attempt
detected dozens of unjustified section breaks and was **rejected**, not
merged.

### Full original-source-locked scan results

The successful [all-five-volume v7 run 45144455342](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45144455342)
preserved all 9,380 original TEI article keys and all original PDF
SHA-256 locks:

| Research-only metric | Previous v6 | Revised v7 |
| --- | ---: | ---: |
| Conservative OCR-count-comparable source articles | 5,768 | **5,743** |
| Unresolved candidates, **including** quarantined intervals | 3,612 | **3,637** |
| Candidates withheld for intervening printed titles | 89 | **117** |
| Similar length but low source four-gram overlap | 24 | **24** |
| OCR spans ≥2x source with ≥60% source four-gram recovery | 6 | **0** |
| Source articles ≥100 tokens with ≥50 absolute-token discrepancy | 78 | **64** |

The remaining six OCR-excess candidates were handled as follows:

- `ANTHROPOMORPHISM`, `CHIEF SEATS`, `COCK`, `FAITH`,
  `OBED-EDOM`: the independent printed heading of a different
  article occurs inside the proposed digital-neighbor OCR interval,
  so the misleading count is **withdrawn**.
- `VAIN`: after the full-width section band is read correctly,
  its OCR count becomes **105 Latin tokens vs 103 source TEI tokens**,
  close enough for a numerical candidate, though still **not a
  certified historical transcription**.

The source-image observations (previous five plus six newly reviewed
headings/letter sections) are recorded in
`workspace/reviews/1915-ocr-print-heading-visual-inspection-v2.json`.
This **retains all five v1 records unchanged**, captures 1915 original
PDF and rendered page JPEG SHA-256s and folios, and is validated by
the same canonical source-index checks. Eleven original printed
heading/layout observations are **not** eleven complete content
collations. The exact original CrossWire texts, cleaned canonical TEI
and separate previously approved editorial corrections have not been
changed or silently normalized. Legal redistribution is still blocked.

Next editorial work should prioritize the **24** similar-length,
low-four-gram cases with original page images and token-level
comparisons, distinguishing OCR transcription noise from genuine source
variations. The **117** OCR-quarantined intervals are not automatically
117 historical errors; most still require printed-image validation.
