# Workflow

## Acquisition
Download the exact upstream CrossWire ISBE 2.2 distribution through an approved official source. Retain the original download unmodified under `sources/crosswire/isbe-2.2/`. Record retrieval date, URI, checksums, distribution contents and exact licensing text in a manifest. A version number alone is not proof of textual fidelity.

## Faithful extraction
Extract the complete article set to `cleaned/en/` as structured files. Preserve titles, spelling, headings, paragraph structure, verse references, internal links and relevant source annotations. Audit article counts, collisions, broken references, ordering and output-to-input traceability. Log any unavoidable normalization. Do not treat cleaned output as a rewritten edition.

## Editorial modernization
Copy the validated cleaned corpus into `modern/en/` as separate tracked articles, then modernize in reviewable batches. Preserve stable article IDs and segment IDs across wording changes. Splitting, merging or deleting segments needs explicit mapping and review. Flag historical / theological changes independently of purely linguistic modernization. Record editorial decisions in `workspace/reviews/`.

## Translation
Translate from a known commit/release of `modern/en/`, preserving IDs and structure. Each translated segment records its `source_hash` (SHA-256 of canonical modern-English source text) and ideally source revision. Retain human review status and terminology decisions. Do not present raw machine translations as editorially validated.

## Updates
Before changing `modern/en/`, retain an identifiable old snapshot via Git tag/commit or an export. Compare old and new snapshots using `scripts/translation_diff.py`, store JSON reports in `workspace/changes/`, and queue only changed or newly added segments for translation. Removed segments need explicit editorial review; unchanged segments are reused only when their hashes match. After translation, run validation for IDs, hashes, references, links and completeness.

## Release
Require approved licensing, source provenance, integrity report, coverage/quality checks and editorial release decision. Outputs for SWORD/OSIS or other publication formats are generated from tracked sources, not maintained as competing editorial masters.
