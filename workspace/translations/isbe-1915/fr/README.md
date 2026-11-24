# ISBE 1915 — full French translation, ongoing

## Editorial standard approved on 24 November 2026

The project owner approved a **complete, readable, natural French translation
of each historical ISBE article**, in the manner of the entire translated
**ABRAHAM** sample shown in the conversation.

This is a translation of the **corrected historical 1915 English ISBE**:
- Faithfully translate **the complete original article**: introduction,
  arguments, subheadings, references, bibliography, historical scholarly
  opinions and author attribution.
- Write clear, idiomatic, flowing French. Avoid the literal, fragmented style
  that obscured the first pilot; preserve the original intellectual substance,
  even where its early-20th-century assumptions are dated or controversial.
- **Never** quietly modernize historical claims, invent a passage absent from
  the English witness, or introduce translator judgments into the source prose.
  Log uncertain or corrupt textual evidence separately.
- Preserve the source article structure and the exact **9,380 original English
  canonical IDs and SWORD keys**, internal link targets, citations and
  original-script text. Localize visible titles only.
- Approval of this **style and workflow** does **not** mean that 9,380 entries
  or even the first 50 machine-assisted pilot drafts have been individually
  proofread and approved for public release.

## Reusing the existing fifty articles

The **50 full source-matched but unreviewed pilot drafts** remain at
`workspace/pilots/isbe-1915-fr/draft-patches.json`. They are not rewritten or
imported a second time. The new batch tool can combine them with additional
articles into one excerpt using the same canonical index.

## First new source-locked entry

`batches/0001-abraham.json` begins the full-corpus translation with **ABRAHAM**,
canonical source `isbe-34a2976d25bc7d0f3d37`. Its section coverage is
**I. Name through III. Career**, including source-owned references.
It is explicitly **partial and unreviewed**, not yet a complete translation
of the article and **not a published resource**. Work must continue with
sections IV–VII before full-article editorial review.

Source SHA-256 (immutable):
`5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.

## Reproducible extraction and validation

All commands run from the repository root.

```sh
python3 -m scripts.export_translation_source \
  --source sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml \
  --key ABRAHAM --start 0 --limit 100 \
  --output /tmp/isbe-abraham-source-0.json

python3 -m scripts.apply_translation_batches \
  --source sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml \
  --patches workspace/pilots/isbe-1915-fr/draft-patches.json \
  --patches workspace/translations/isbe-1915/fr/batches/0001-abraham.json \
  --output /tmp/isbe-fr-working-excerpt.xml \
  --report /tmp/isbe-fr-working-excerpt-report.json

python3 -m unittest tests.test_translation_batches -v
```

The output is marked `xml:lang=mul` because it is a multilingual, unfinished
editorial excerpt. Every generated report explicitly forbids publication.
The full-corpus parity validator `scripts/validate_translation_identity.py`
is the separate mandatory gate once **all 9,380 articles** are fully translated.
No French SWORD release, catalog publication, independent canonical index or
relabeling of the English SWORD module is authorized at this stage.

## Progress accounting

- Corrected original English entries: **9,380**.
- Existing first-pass source-locked draft entries: **50** (still unreviewed).
- First new article begun: **ABRAHAM**, sections I–III; remainder pending.
- New full French encyclopedia: **not completed / not published**.
- Next: finish ABRAHAM sections IV–VII, run source-locked completeness tests,
  create readable article previews from original TEI paragraphs, and begin
  editorial proofreading of the 50 initial entries before scaling in batches.

Tracking: [ISBE #103](https://github.com/icfmp/Bible-Resources-ISBE/issues/103).
