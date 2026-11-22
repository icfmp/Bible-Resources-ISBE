# Bible Resources — ISBE

A reproducible, multilingual workspace for the **1915 International Standard Bible Encyclopedia** (ISBE).

This repository preserves the historical source, prepares a faithful structured reference, develops a separate modern-English edition, and derives translations from identified revisions of that modern-English edition.

> **Status:** workspace initialization. No CrossWire archive, cleaned corpus, modernized article or translation has yet been imported or verified. Directory placeholders are not data.

## Repository layout

```text
sources/
  crosswire/isbe-2.2/          # Immutable original distribution, manifest and checksum
cleaned/
  en/                         # Faithful structured extraction, no rewriting
modern/
  en/                         # Version-controlled, modern English editorial master
translations/
  fr/ de/ es/ it/             # Derived translations, same stable IDs
workspace/
  changes/                    # Reviewable changesets for incremental translation
  reports/                    # Ingestion, integrity, coverage and QA reports
  reviews/                    # Editorial decisions and unresolved questions
scripts/                      # Reusable ingestion, comparison and QA tools
tests/                        # Representative, automated tests
docs/                         # General process, formats and editorial rules only
```

## Canonical relationships

1. The **CrossWire SWORD distribution** is kept byte-for-byte, with upstream URL, exact module version, retrieval date, SHA-256, and licensing information. Never overwrite it; a new upstream version receives a new folder.
2. **Cleaned English** extracts and represents the source faithfully (headings, articles, paragraphs, references, cross-references, notes and markup when present). No silent corrections or paraphrases. Record all transformation decisions.
3. **Modern English** is a separate editorial work. Its revisions are kept in Git and its article/segment identifiers remain stable. Modernizing language is not the same as changing historical claims.
4. **Translations** reference an explicit modern-English revision. Updating the English master invalidates only impacted translated segments; unmodified segments are retained.
5. The **BSI links** will later reference stable ISBE article IDs, not translated headings. Article-to-entity mapping remains a distinct activity.

## Incremental translation

Store articles as JSON (one article per file) with stable `id` and stable `segments[].id`. The utility `scripts/translation_diff.py` compares two modern-English snapshots and emits changed, added, removed and unchanged segment IDs with source hashes. Generate and review these reports before commissioning updates; changed source segments require retranslation or review, never silent reuse.

```bash
python3 scripts/translation_diff.py --old modern/en --new path/to/updated-modern-en --output workspace/changes/modern-en-diff.json
python3 -m unittest discover -s tests -v
```

## Publishing rules

No public release until provenance and redistribution rights of the exact source and any derived editions are documented and the transformed content has been validated. Git is the history of changes, but stable source snapshots and machine-readable change reports are also retained. Do not create empty or fabricated ISBE articles merely to populate folders.

See [workflow](docs/workflow.md) and [article format](docs/article-format.md).
