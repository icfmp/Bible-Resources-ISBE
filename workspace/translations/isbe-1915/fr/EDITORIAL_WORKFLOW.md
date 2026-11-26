# French ISBE 1915 — complete-article editorial workflow

## Goal and permanent source

Translate the **entire historical 1915 ISBE into clear and idiomatic French**,
using the complete seven-section **ABRAHAM** translation as the approved
presentation and prose standard. **Faithful historical translation, not an
adaptation or a re-authored modern encyclopedia.**

The only translation master is the **corrected English TEI P5** at
`sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml` (SHA-256:
`5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`).
The 9,380 article `xml:id` values, original `@n` SWORD keys, exact
sequence, TEI children, citations, Scripture `cRef` and internal reference
targets are canonical **across languages**. No new BRSI per-language identity.

## Repeat the MHCC per-article cycle

1. **Read source**: extract the entire canonical article; examine all source
   TEI nodes, headings, inline Hebrew/Greek, names, references, bibliography
   and flagged corruption evidence.
2. **Translate**: produce the full French article, with natural paragraphs,
   accurate meaning, established French biblical names, and faithful historical
   nuance. Do not omit inconvenient or dated scholarship. Avoid a literal
   fragment-by-fragment reading style.
3. **Reconstruct**: maintain a source-locked patch specifying the original
   **exact text for each original TEI text/tail node**. Generate the complete
   TEI and human-readable Markdown from that patch. Preserve every canonical
   ID, key, script and reference destination. Only target text/display changes.
4. **Collate and review**: compare **the entire English and French article**
   paragraph by paragraph; inspect theology, logic, translation fidelity,
   original names, references, section boundaries, source anomalies and
   typography. An independent editorial review is a **separate gate**.
   A source-damaged passage remains flagged and cannot silently be guessed.
5. **Verify and commit**: run source-fingerprint, full-node coverage, TEI
   parity, content and regression tests, then commit the article and its
   available review evidence directly on the active translation branch.
   Keep a reversible explanation for each correction. **Do not open a PR for
   individual articles, cohorts, 1,000-entry waves, or the 14-entry completion.**
   Open one translation PR only after **all 9,380 French articles have their
   complete first translations**, subject to subsequent full-corpus review
   and publication gates. The draft and editorial acceptance states remain
   distinct.
6. **Check the GitHub issue checkbox only now**: one original source key
   corresponds to one checked item **only after actual reviewed acceptance**.
   Draft translation, automated proof, CI success and article acceptance are
   distinct states. Record the article's commit and gate evidence, so work
   resumes after interruption without trusting a checkbox alone.
7. **Publication is a different decision**: the full French TEI needs 9,380
   entries, final source parity, official schema, native SWORD roundtrip, real
   reader navigation, editorial sign-off and explicit release permission.
   A batch issue being closed does not authorize publication.

## What the initial 50 drafts mean

The initial 50 heterogeneous French entries were drafted at the source-unit
level before the full-article editorial standard was approved. They are already
**complete drafts** — not 50 half-articles. They remain immutable baseline
inputs until their translations are explicitly revised in a versioned patch.

The audit generator reconstructs **all 50 + ABRAHAM** as complete readable
Markdown proofs and produces a machine-readable status/report. This
**harmonizes the presentation and review mechanism** without claiming that
all 50 are already editorially polished.

The source anomaly ledger
`workspace/pilots/isbe-1915-fr/SOURCE_REVIEW_FLAGS.json`
has **12 unverified digital-text anomalies affecting 6 articles**.
The English source is unchanged; no invented repairs.

For articles about a historical English Bible word or KJV/RV wording, retain
the meaningful English historical wording (with an understandable French
explanation where necessary). Do not falsely replace the source's quotations
with a modern French Bible translation. French localized title/alias is a
display and search concern, never a canonical source key change.

## Issue batches

Wave 1 has four **source-index contiguous lists** (not selected by text length):

| Ticket lot | Exact canonical source positions | Count |
| --- | ---: | ---: |
| 01 | 1–1,000 | 1,000 |
| 02 | 1,001–2,000 | 1,000 |
| 03 | 2,001–3,000 | 1,000 |
| 04 | 3,001–4,000 | 1,000 |

Immutable machine rosters:
`workspace/translations/isbe-1915/fr/worklists/wave-01/`.
Each individual checklist starts **unchecked** (including any articles with
unreviewed first drafts). `scripts/validate_translation_worklists.py`
matches every source `@n` and `xml:id` against the corrected English
master and rejects any skip, duplicate, reordering or changed key.

The remaining source positions **4,001–9,380** are **not included** in
wave 1. They can be assigned later in nonoverlapping waves of 1,000 plus a
final group of 380. Do not claim that four issues cover the encyclopedia.

## Current recorded status (not a release)

- Original English source: **9,380** entries; unchanged.
- Pilot first drafts: **50**.
- New full first draft: **ABRAHAM**.
- Total first-pass full drafts: **51**; editorially approved: **0**.
- Remaining to draft: **9,329**.
- Source anomalies still flagged: **12**, original witness review outstanding.
- French complete TEI/SWORD: **not built or published**.

GitHub tracking: [#103](https://github.com/icfmp/Bible-Resources-ISBE/issues/103).
