# ISBE — translate by full Markdown paragraphs

The permanent English Markdown archive is reusable across languages, but the
corrected historical English TEI remains the source of truth. The bridge uses
the archive's checksummed per-article source maps to reconstruct exact TEI
text/tail patches, without heuristic matching or changing canonical IDs.

## One article

Download `ISBE-1915-markdown-workspace.zip` from the permanent
[`generated/isbe-1915-markdown` branch](https://github.com/icfmp/Bible-Resources-ISBE/tree/generated/isbe-1915-markdown/workspace/exports/isbe-1915).

From the repository root:

```sh
python3 -m scripts.markdown_translation_bridge template \
  --archive /tmp/ISBE-1915-markdown-workspace.zip \
  --key ANDREW --output /tmp/ANDREW-fr.md

# Translate the ENTIRE article naturally, paragraph by paragraph.
# Keep all source-owned block comments and inline ISBE anchors unchanged.

python3 -m scripts.markdown_translation_bridge compile \
  --archive /tmp/ISBE-1915-markdown-workspace.zip \
  --input /tmp/ANDREW-fr.md \
  --output /tmp/andrew-fr-batch.json \
  --report /tmp/andrew-fr-audit.json
```

The template is a **draft**, not an automatic translation. Edit the text
between original markers, never the markers themselves.

A paragraph may contain a protected Scripture or Greek/Hebrew token such as
`⟦ISBE:KEEP:3:Jn 1:1⟧`. These anchors are source-owned and must not be
deleted, rewritten, or reordered. `OPEN` and `CLOSE` markers retain inline
TEI elements, while their inner visible prose remains translatable. `FIX`
marks original punctuation-only content that the existing patch contract does
not permit translating. Every `ISBE-BLOCK` and `ISBE-END` marker is mandatory.

An intentionally unchanged English text unit needs a `preserve` reason in the
metadata JSON comment (e.g. `"preserve":{"67:text":"Original author name"}`).
Otherwise compilation fails rather than silently count untranslated English
as a complete French draft.

## Mandatory checks

The compiler checks the pinned English TEI revision, per-article SHA,
Markdown and source-map hashes; exact block count and order; every mutable
TEI text/tail unit; all Scripture/original-script anchors and immutable
attributes; and an in-memory reconstructed TEI structural comparison.
It emits the existing nonpublishable French source-locked patch schema.
The full `apply_translation_batches` CI, independent bilingual editorial
review, official TEI schema, and any later SWORD publication remain separate
gates. No GitHub checkbox is marked by this tool.

**It does not translate automatically, judge translation quality, publish a
module, or modify the historical English source.**

For future languages, reuse the original English archive and article IDs.
This first bridge targets French because the existing patch application
workflow currently validates `language: fr`.
