# Source-to-translation workflow

## 1. Preserve the original
Keep `sources/crosswire/isbe-2.2/ISBE.zip` byte-for-byte, accompanied by its retrieval metadata and SHA-256 in `MANIFEST.json`. No re-downloading or rewriting as part of normal editorial work.

## 2. Rebuild the faithful reference
Use SWORD `mod2imp` to export `workspace/exports/isbe-2.2.imp` and retain that export. Run `scripts/rebuild_tei.py` to create `cleaned/en/ISBE.xml`, `cleaned/en/article-index.json`, and `workspace/reports/tei-reconstruction.json`. The program aborts on missing entries, duplicate IDs, malformed XML or text integrity failure. Cross-references that fail to resolve and original label differences are reported, not guessed.

## 3. Review the corpus
Audit unresolved references, headings, unusual article structures and representative content against the official source and, for textual issues, the historic printed edition. Keep factual/OCR/editorial questions distinct. The 2.2 module itself reports historic OCR and layout corrections, so it is not automatically a facsimile of 1915.

## Navigation-only corrections

Treat cross-reference navigation as a separate layer from source text. Run the canonical TEI rebuild action on changes to `scripts/rebuild_tei.py` or `workspace/reviews/accepted-title-aliases.json`. The action regenerates `workspace/reports/tei-reconstruction.json` and the remaining-link diagnostics under `workspace/reviews/`.

Resolve mechanical title variants and explicitly identifiable article/section destinations through generic rules. Where the original headings are insufficient, record a source-backed decision with a concise rationale in `accepted-title-aliases.json`. Use a global `mapping` only if its title equivalence holds in every context; for homonyms and exceptional references use `occurrence_mappings` with the stable source reference ID and original target. Never add guessed links merely to decrease the unresolved count. All original CrossWire encyclopedia reference destinations must remain recoverable in `n` on rewritten links.

Checks must confirm entry/character counts, per-article text hashes, unique XML IDs, valid rewritten targets, and that every original SWORD encyclopedia link occurrence is resolved, remains explicitly unresolved, or has been identified as a bibliographic heading with preserved provenance.

## 4. Modernize without overwriting
Copy the validated cleaned master to `modern/en/ISBE.xml`; preserve existing `xml:id` values. Modernize language in reviewable batches with recorded editorial rationale. Distinguish linguistic updates from corrections of historic assertions.

## 5. Translate
Create `translations/<lang>/ISBE.xml` from a recorded modern-English commit. Preserve stable entry/unit IDs, text structure and references. Record per-unit source revision and hash for translation currency. Flag machine translations as such until reviewed.

## 6. Update incrementally
Compare consecutive modern-English TEI revisions at indexed text-unit level, retain machine-readable diffs in `workspace/changes/`, and retranslate only changed or added units. Treat deleted or structurally split units as editorial cases; never silently retain stale translations.

## 7. Publish
Publishing requires verified rights for the exact digital artifacts and derivative editions, coverage/validation reports, editorial approval and a separately generated distribution format (SWORD, OSIS or another supported target).
