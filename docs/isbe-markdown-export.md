# Reusable ISBE 1915 Markdown translation workspace

## Why this export exists

The corrected historical English TEI remains the **single authoritative source**
for all 9,380 articles. Translators should not have to navigate a 37 MB XML file
to read individual articles. This exporter provides one readable English Markdown
file per canonical entry, and independently keeps the exact TEI content and
attributes in a machine-readable, lossless source map.

The source is pinned to SHA-256:
`5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.

## What is retained

The deterministic archive contains:

- `en/articles/<original-xml-id>.md` — 9,380 English Markdown reading copies.
- `en/maps/<original-xml-id>.json` — 9,380 complete ordered TEI element
  inventories, including every original element tag, attribute, text and tail,
  with node ordinal and parent. These maps can reconstruct the source element
  with an identical, namespace-independent semantic fingerprint.
- `en/INDEX.md` — all 9,380 canonical source keys in original index order.
- `fr/unreviewed/<original-xml-id>.md` — all available complete French first
  drafts, derived without retranslation from the existing source-locked patches.
- `fr/INDEX.md`, `MANIFEST.json`, and `README.md` — status, original
  source hash, article source fingerprints, Markdown and map SHA-256 checksums
  and provenance.

**The French content is a draft review copy, not an approved translation.**
The archive never approves an article, checks issue #109, creates a translated
TEI master or authorizes publication.

An article's filename is its existing `xml:id`, never a translated title.
The archive does not create a new French canonical index; original `@n`
SWORD keys and internal references stay stable across all future languages.

## Reproduce locally

From the repository root:

```bash
patches=(--patches workspace/pilots/isbe-1915-fr/draft-patches.json)
for path in workspace/translations/isbe-1915/fr/batches/*.json; do
  patches+=(--patches "$path")
done

python3 -m unittest tests.test_export_tei_markdown_corpus -v

python3 -m scripts.export_tei_markdown_corpus \
  --source sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml \
  --output /tmp/ISBE-1915-markdown-workspace.zip \
  --report /tmp/ISBE-1915-markdown-REPORT.json \
  "${patches[@]}"
```

The archive is deterministic for unchanged TEI, translation patches and
exporter version. The manifest includes SHA-256 for each exported English
Markdown file and its exact source map. `REPORT.json` includes the complete
ZIP SHA-256.

## Durable storage and CI

The `Build and retain reusable ISBE Markdown corpus` workflow checks the
English TEI hash, article count, every article's lossless source-map roundtrip,
existing French patch reconstruction and archive integrity.

On pull requests, it generates a **90-day CI artifact** for inspection.
After the workflow succeeds on `main`, it retains both the archive and the
checksum report in the dedicated branch
[`generated/isbe-1915-markdown`](https://github.com/icfmp/Bible-Resources-ISBE/tree/generated/isbe-1915-markdown/workspace/exports/isbe-1915)
under `workspace/exports/isbe-1915/`. This archive branch is the stable
storage location, distinct from the corrected source and normal development
history. If the retention job fails, do not claim that durable storage succeeded;
inspect GitHub Actions and correct the permissions or workflow.

## Critical editorial rule

Markdown is for **human reading and translation work**, not lossless document
structure. The paired JSON contains the complete source TEI structure and is
not modified by translators. A future translator can read the English Markdown,
compose a natural translation, then generate existing source-locked text-unit
patches against original TEI ordinals using the existing
`scripts/export_translation_source.py` / `scripts/apply_translation_batches.py`
contracts. Those tools continue to preserve Scripture `cRef`, internal
`ref/@target`, notes, original Greek/Hebrew, stable IDs and source provenance.

**Never** re-import Markdown by heuristic paragraph matching or claim that
a Markdown export alone is a validated TEI translation. Review and later SWORD
publication remain separate gates.

## Next five Markdown templates — readable directly on GitHub

After an approved technical merge to `main`, the same export job also prepares
the **five shortest still-undrafted source articles** in frozen wave 01,
keeping the original source-index order. They appear alongside the ZIP in
[`generated/isbe-1915-markdown/workspace/exports/isbe-1915/next-five/`](https://github.com/icfmp/Bible-Resources-ISBE/tree/generated/isbe-1915-markdown/workspace/exports/isbe-1915/next-five).

Each Markdown file is named by its canonical `xml:id`, contains all original
paragraphs and immutable in-line TEI anchors, and is **only an untranslated
English template**. The adjacent `MANIFEST.json` records canonical key,
original ID, source SHA, paragraph count and SHA-256 of the template.

To translate, copy an individual Markdown file (not the original English
source) to your working branch, translate its prose paragraph by paragraph,
and run `scripts.markdown_translation_bridge compile` against the pinned
archive. The converter generates the exact source-locked TEI JSON patch.
**Never translate, rewrite or delete a protected anchor or paragraph marker.**
The `next-five` files are periodically regenerated from pending entries;
translated drafts, if any, belong in source-locked batches rather than this
generated temporary queue. Preserve the original TEI and use the established
independent review/publication gates.
