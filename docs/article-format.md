# Canonical TEI interchange format

The **target encoding standard** is [ISBE TEI P5 structure profile](tei-structure-profile.md). This document describes the present reconstructed data and its stable IDs. The current XML is a working reconstruction, not an officially schema-validated TEI P5 publication.

The editorial master is **TEI XML**, one document per language edition. `cleaned/en/ISBE.xml` contains the complete digital-source transcription. Subsequent editions use the same article identifiers and (where structure is unchanged) the same text-unit identifiers.

The document contains:

- `<TEI>`, `<teiHeader>`, `<text>`, `<body>`.
- One `<div type="entry" xml:id="isbe-…" n="ORIGINAL SWORD KEY">` per dictionary entry.
- One `<head xml:id="…">` for its heading.
- Source text units (`p`, `list`, `item`, etc.) and inline TEI elements (`ref`, `hi`, etc.) retained as found in the CrossWire source; each indexed content element receives an `xml:id`.
- Cross-article targets are rewritten to `#isbe-…` when the original key exists, and the original `ISBE:KEY` is retained in `n`. References that cannot be linked with sufficient evidence are emitted as non-clickable `<seg type="unlinked-source-reference" n="ISBE:…">` rather than as broken `<ref>` hyperlinks. The original visible text, `xml:id` and original target remain intact for auditing and possible future repair. Biblical `osisRef` values remain untouched **for fidelity in the working legacy reconstruction**. The target profile requires a separate, tested transfer to TEI `cRef` with a declared canonical-reference scheme before claiming P5 conformance.

## Stable IDs

Article IDs are `isbe-` plus the first 20 hexadecimal digits of SHA-256 over the **exact original SWORD key**. This avoids dependence on alphabetical ordering or translations. Content-element IDs incorporate the article ID and ordinal at initial ingestion. These IDs are fixed in the cleaned reference. Future modern-English editorial splits or merges require an explicit mapping rather than renumbering existing IDs.

`article-index.json` lists each article's order, source key, ID, text length and SHA-256 of its extracted text. The JSON is **an index and audit artifact only**, not a competing editorial source.

## Content integrity

The extractor compares the complete Unicode text of each source entry with its reconstructed TEI, then parses the serialized output and checks each article's text SHA-256. No editorial substitutions or source corrections are permitted at this stage.

The XML preserves inline TEI and source Bible references where present. It does not attempt to reproduce original printed layouts.

The unresolved links and name variants in the reconstruction report require separate editorial review; do not automatically equate similar entries without evidence.

## Internal cross-reference reconstruction

Original CrossWire `ISBE:...` targets are retained in the `n` attribute when resolved and replaced with a validated `#xml-id` destination. The resolver supports exact keys, uniquely attested punctuation and alternate-title components, local headings, numbered subentry paragraphs, and limited biblical-reference disambiguation of numbered homonyms. It does **not** invent entries or select among unresolved homonyms.

The reviewable `workspace/reviews/accepted-title-aliases.json` contains both justified global headword equivalences (`mappings`) and individual source-reference decisions (`occurrence_mappings`) with stable reference IDs, source/destination keys and reasons. The latter distinguish homonyms where a global alias would be wrong. All decisions fail validation if their source or destination has changed.

For rare references to a verified article with a numbered subdivision that cannot be reliably located, `occurrence_mappings` may specify `destination_precision: article_fallback`. The navigation then opens only the whole article, **not** an invented subsection. The original numbered source target and the limited precision remain traceable, and reconstruction reports `imprecise_article_fallback_count`. This fallback must be an explicitly justified editorial decision, never the default for an unmatched target. The source SWORD ZIP and IMP export are immutable.

The full regeneration verifies the Unicode article-text hash against the export, checks all `xml:id` values for uniqueness, checks every resolved fragment target, and confirms that all original encyclopedia references are accounted for as a valid resolved link, an inert source-reference segment, or a reclassified bibliographic heading. CrossWire sometimes encoded a final `LITERATURE.` heading as a reference to a nonexistent article: in demonstrable cases, it is reconstructed as a TEI bibliography heading, with identical visible text, stable source identifier and original `ISBE:...` value in `n`. A corresponding table-of-contents reference may then target the actual section. A remaining unresolved source reference is **not** a clickable link: its text and original destination remain visible in the XML and are recorded in `workspace/reports/tei-reconstruction.json` as `unlinked_source_references`. The report separately counts `active_broken_isbe_links` (required to be zero), and the contextual review files still list the unlinked occurrences. The original CrossWire ZIP and intermediate IMP export remain unchanged.

