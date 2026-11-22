# Canonical TEI interchange format

The editorial master is **TEI XML**, one document per language edition. `cleaned/en/ISBE.xml` contains the complete digital-source transcription. Subsequent editions use the same article identifiers and (where structure is unchanged) the same text-unit identifiers.

The document contains:

- `<TEI>`, `<teiHeader>`, `<text>`, `<body>`.
- One `<div type="entry" xml:id="isbe-…" n="ORIGINAL SWORD KEY">` per dictionary entry.
- One `<head xml:id="…">` for its heading.
- Source text units (`p`, `list`, `item`, etc.) and inline TEI elements (`ref`, `hi`, etc.) retained as found in the CrossWire source; each indexed content element receives an `xml:id`.
- Cross-article targets are rewritten to `#isbe-…` when the original key exists, and the original `ISBE:KEY` is retained in `n`. References not resolvable to a source key remain unchanged and are reported. Biblical `osisRef` values remain untouched.

## Stable IDs

Article IDs are `isbe-` plus the first 20 hexadecimal digits of SHA-256 over the **exact original SWORD key**. This avoids dependence on alphabetical ordering or translations. Content-element IDs incorporate the article ID and ordinal at initial ingestion. These IDs are fixed in the cleaned reference. Future modern-English editorial splits or merges require an explicit mapping rather than renumbering existing IDs.

`article-index.json` lists each article's order, source key, ID, text length and SHA-256 of its extracted text. The JSON is **an index and audit artifact only**, not a competing editorial source.

## Content integrity

The extractor compares the complete Unicode text of each source entry with its reconstructed TEI, then parses the serialized output and checks each article's text SHA-256. No editorial substitutions or source corrections are permitted at this stage.

The XML preserves inline TEI and source Bible references where present. It does not attempt to reproduce original printed layouts.

The unresolved links and name variants in the reconstruction report require separate editorial review; do not automatically equate similar entries without evidence.

## Internal cross-reference reconstruction

Original CrossWire `ISBE:...` targets are retained in the `n` attribute when resolved and replaced with a validated `#xml-id` destination. The resolver supports exact keys, uniquely attested punctuation and alternate-title components, local headings, numbered subentry paragraphs, and limited biblical-reference disambiguation of numbered homonyms. It does **not** invent entries or select among unresolved homonyms.

The small, reviewable `workspace/reviews/accepted-title-aliases.json` is the source of manually approved heading equivalences. Each mapping records a reason and is applied generically by the reconstruction tool. The source SWORD ZIP and IMP export are immutable.

The full regeneration verifies the Unicode article-text hash against the export, checks all `xml:id` values for uniqueness, checks every resolved fragment target, and confirms the number of internal source links is unchanged. Unresolved `ISBE:` targets remain visible as such; they are not silently discarded.

