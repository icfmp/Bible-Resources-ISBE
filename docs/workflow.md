# Source-to-translation workflow

## 1. Preserve the original
Keep `sources/original/encyclopedias/en/isbe-crosswire-2.2/ISBE.zip` byte-for-byte, accompanied by its retrieval metadata and SHA-256 in `MANIFEST.json`. No re-downloading or rewriting as part of normal editorial work.

## 2. Rebuild the faithful source witness as an intermediate

Keep the preserved IMP and original CrossWire ZIP unchanged. Run `scripts/rebuild_tei.py` only into `workspace/tmp/isbe-legacy/`, preserving the reconstructed source's exact byte-level SHA-256. Its `osisRef` attributes and old bibliography leads are **source-intermediate markup**, not the released TEI encoding. The original stable article index and reconstruction/links reports are regenerated from the same intermediate. No source text edits are allowed.

## 3. Validate and adopt the source-locked canonical TEI P5

The canonical working XML at `workspace/witnesses/crosswire-2.2/ISBE.xml` is the exact verified TEI P5 candidate derived from that source. `scripts/normalize_tei_p5.py` makes only documented mechanical changes, in a **separate candidate**, and compares every article's source text, paragraph/node text and tails, original attributes outside the declared exceptions, IDs, keys and links to the intermediate and source index.

Before replacing the master, `.github/workflows/rebuild-tei.yml` enforces the pinned candidate SHA-256, strict project profile, and both official TEI P5 4.12.0 RELAX NG and Schematron. The shared validator is `scripts/validate_official_tei_p5.py`, with two deliberately invalid controls. The canonical master is overwritten **only after all tests pass**, and the report and source digest are committed together with the master.

Source-lock and schema proofs: `workspace/changes/tei-p5-candidate-v1.json`, `docs/tei-p5-candidate-migration.md` and [issue #3](https://github.com/icfmp/Bible-Resources-ISBE/issues/3). The exact original remains recoverable from the source ZIP, IMP, and repository history. New editorial changes require a reviewed revision and fresh provenance; never loosen a checksum just to make CI green.

## 4. Review the corpus
Audit unresolved references, headings, unusual article structures and representative content against the official source and, for textual issues, the historic printed edition. Keep factual/OCR/editorial questions distinct. The 2.2 module itself reports historic OCR and layout corrections, so it is not automatically a facsimile of 1915.

## Navigation-only corrections

Treat cross-reference navigation as a separate layer from source text. Use the source-first, schema-gated canonical TEI rebuild action on changes to `scripts/rebuild_tei.py` or `workspace/reviews/accepted-title-aliases.json`. The action regenerates `workspace/reports/tei-reconstruction.json` and the remaining-link diagnostics under `workspace/reviews/`.

Resolve mechanical title variants and explicitly identifiable article/section destinations through generic rules. Where the original headings are insufficient, record a source-backed decision with a concise rationale in `accepted-title-aliases.json`. Use a global `mapping` only if its title equivalence holds in every context; for homonyms and exceptional references use `occurrence_mappings` with the stable source reference ID and original target. Never add guessed links merely to decrease the unresolved count. All original CrossWire encyclopedia reference destinations must remain recoverable in `n` on rewritten links.

Checks must confirm entry/character counts, per-article text hashes, unique XML IDs, valid rewritten targets, and that every original SWORD encyclopedia link occurrence is a valid destination, an explicitly unlinked source-reference segment, or a bibliographic heading with preserved provenance. The count of active `ISBE:` targets with no verified destination must be **zero**.

## 5. Preserve the corrected historical English master

The immutable CrossWire original remains at `sources/original/encyclopedias/en/isbe-crosswire-2.2/`; its unedited reconstruction remains at `workspace/witnesses/crosswire-2.2/ISBE.xml`. The **authoritative source for translations** is the corrected English historical edition `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml`, SHA-256 `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c` (9,380 articles). Verify that SHA before translating. Any later editorial change needs a pinned source revision and translation-impact report.

An optional **modern-English edition** may still be made in the future, but is **not a prerequisite or intermediary** for French or other translations. A modern paraphrase must never redefine canonical article identity.

## 6. Translate with one canonical index for every language

Create the French TEI P5 derivative directly from the corrected historical English master. Future languages follow the same identity contract. Keep language editions in distinct versioned, provenance-documented locations (e.g. `sources/cleaned/encyclopedias/fr/isbe-1915/ISBE.xml` once a real translation exists). Do not create empty translated masters or imply that raw machine output has passed editorial review.

**Mandatory cross-language invariants:**

- Keep all **9,380 ordered original** `(entry/@xml:id, entry/@n)` pairs unchanged. Never translate `@n` source keys or regenerate IDs.
- Preserve all established internal `xml:id` values (paragraphs, sections, notes, headings and references), one-to-one structure for the initial translated edition, `ref/@target` destinations, `ref/@cRef` Bible references, source provenance and source-language text.
- Translate **visible text**, titles and display labels, *not* their canonical IDs or links. A localized search alias may resolve French words to existing article IDs, never to a second semantic index.
- A French SWORD module uses its **own** module ID while preserving dictionary addressability of every unchanged source key. Never use translated titles as replacement canonical keys.
- Track source revision/hash and translation state per article. Pending articles must remain explicitly pending, not silently fabricated.
- Any structural split/merge needs an explicit reviewed editorial mapping; it is not silently accepted by the first-version strict parity check.

Run `scripts/validate_translation_identity.py` on a **complete translated TEI candidate**, pinned to the historical source, before schema validation, SWORD build or BRSI inclusion. This checks the complete body structure and source-owned attributes and rejects reordered/renamed/missing IDs and keys, altered links/Bible references, and changed original-language quotations.

Example, once a complete candidate exists:

```sh
python3 scripts/validate_translation_identity.py \
  --source sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml \
  --translation sources/cleaned/encyclopedias/fr/isbe-1915/ISBE.xml \
  --expected-source-sha256 5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c \
  --expected-count 9380 \
  --target-language fr \
  --report workspace/reports/isbe-1915-fr-translation-identity.json
```

**Passing identity parity is not approval of translation accuracy, official TEI schema validity, native SWORD behavior, derivative rights, or publication.** Those remain separate gates.

## 7. Update incrementally

Compare source revisions at canonical text-unit level with `scripts/translation_diff.py`. Keep source revisions/hashes in the translation ledger. Retranslate affected units and recheck the complete canonical index. Any deleted or structurally split unit requires an explicit editorial mapping; do not silently retain stale translated content.

## 8. Publish

Publishing requires full official TEI schema validity, source-index parity, reviewed translation fidelity, independent native SWORD readback, reader tests, exact rights and owner authorization. The French module receives a distinct SWORD ID and version; English stays immutable. BRSI links the unchanged canonical article IDs, independent of the displayed language.
