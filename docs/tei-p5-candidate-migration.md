# ISBE TEI P5 candidate migration — version 1

**State: fidelity candidate, NOT certified TEI P5.** Official RELAX NG
and Schematron checks required by issue #3 have not yet been performed.
Do not replace the faithful cleaned master.

## Provenance and reproducibility

- Immutable original digital witness: sources/crosswire/isbe-2.2/ISBE.zip.
- Unchanged faithful reconstruction: cleaned/en/ISBE.xml.
- Source lock: workspace/changes/tei-p5-candidate-v1.json, with original
  SHA-256 and exact expected node/reference counts.
- Separate candidate: workspace/candidates/en/ISBE.xml, generated in CI.
- Reversible method: remove the candidate and regenerate from the unchanged
  master; no inverse conversion is needed to recover the source.

Execute from the repository root:

    python3 scripts/normalize_tei_p5.py \
      --input cleaned/en/ISBE.xml \
      --index cleaned/en/article-index.json \
      --manifest workspace/changes/tei-p5-candidate-v1.json \
      --output workspace/candidates/en/ISBE.xml \
      --report workspace/candidates/en/tei-p5-candidate-report.json

## Approved changes

1. Add document xml:lang=en and teiHeader/encodingDesc/refsDecl with source
   reference provenance (NOT an invented external Bible URI or resolver), and
   add revisionDesc. Preserve original fileDesc.
2. Transfer every original scripture ref/@osisRef **exactly** to @cRef and
   assign type=scripture; no changes to source reference strings or wording.
3. Type original internal fragment links article when targeting an article
   entry, section when targeting an existing non-entry anchor. Preserve target,
   original @n, original XML ID and displayed words.
4. Mark the synthetic source-key head as type=index, after exact key check.
5. Wrap already-attested bibliography headings and subsequent article content
   in structural TEI div type=bibliography, preserving every original node,
   text, tail, identifier and order. No invented lists or bibliography items.
   The new wrapper has no id; the existing bibliography head retains its id.

## Validation limits and next step

The migration refuses changes to the input SHA, source inventory, IDs,
article-text checksums, original fileDesc, original node text/tail/attributes,
original node order, internal targets, or paragraph nesting outside the
approved bibliography wrapper rule.

Checks run on serialized candidate bytes and compare each article to the
master and its source index. The generated report says
official_tei_schema_validation = NOT_PERFORMED until a separate official,
version- and SHA-256-locked TEI P5 4.12.0 RELAX NG and Schematron gate passes.

No print-source validation, SWORD readback, rights clearance or publication
is implied. Review the migration and its complete corpus report before
changing the canonical master.
