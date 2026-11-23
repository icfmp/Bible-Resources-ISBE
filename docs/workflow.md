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

## 5. Modernize without overwriting
The immutable CrossWire original now also lives under `sources/original/encyclopedias/en/isbe-crosswire-2.2/`. The source-faithful TEI remains locked under `workspace/witnesses/crosswire-2.2/ISBE.xml` for reproducibility and parity of the original. Rebuild our historical edited master into `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml` using `python3 scripts/persist_1915_cleaned_master.py --assemble` and independently verify its exact output digest before any modernization.

**Modernization begins from `sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml`, not from the uncorrected `workspace/witnesses/crosswire-2.2/ISBE.xml`.** Copy this verified *historical working master* to `sources/cleaned/encyclopedias/en/isbe-modern/ISBE.xml`; preserve existing `xml:id` values. Modernize language in reviewable batches with recorded editorial rationale. Distinguish linguistic updates from corrections of historic assertions.

## 6. Translate
Create `sources/cleaned/encyclopedias/<lang>/isbe-modern/ISBE.xml` from a recorded modern-English commit. Preserve stable entry/unit IDs, text structure and references. Record per-unit source revision and hash for translation currency. Flag machine translations as such until reviewed.

## 7. Update incrementally
Compare consecutive modern-English TEI revisions at indexed text-unit level, retain machine-readable diffs in `workspace/changes/`, and retranslate only changed or added units. Treat deleted or structurally split units as editorial cases; never silently retain stale translations.

## 8. Publish
Publishing requires verified rights for the exact digital artifacts and derivative editions, coverage/validation reports, editorial approval and a separately generated distribution format (SWORD, OSIS or another supported target).
