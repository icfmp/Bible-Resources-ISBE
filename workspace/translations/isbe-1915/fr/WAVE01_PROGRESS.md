# French ISBE 1915 — wave 01 / lot 1 progress

Tracking: [issue #109](https://github.com/icfmp/Bible-Resources-ISBE/issues/109).
Source: immutable corrected English TEI, SHA-256 `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.

## First incremental translation change — 24 November 2026

The new source-locked batch `batches/0002-early-a-entries.json` contains **16 complete first drafts**, all using original English `@n` and `xml:id` values:

- Canonical #0001 `A`; #0002 `AALAR`
- #0004 `AARON'S ROD`; #0005 `AARONITES`
- #0007 `AB (2)`; #0008 `ABACUC`
- #0010 `ABADIAS`; #0011 `ABAGARUS`; #0012 `ABAGTHA`
- #0016 `ABATE`
- #0018 `ABDA`; #0019 `ABDEEL`; #0020 `ABDI`
- #0021 `ABDIAS`; #0022 `ABDIEL`; #0024 `ABDON (2)`

The follow-up source-locked batch `batches/0003-complete-first-25.json` adds **8 complete first drafts** for previously missing canonical positions: #0006 `AB (1)`, #0009 `ABADDON`, #0013 `ABANAH`, #0014 `ABARIM`, #0015 `ABASE`, #0017 `ABBA`, #0023 `ABDON (1)` and #0025 `ABED-NEGO`.

**All canonical source positions #0001–#0025 now have full first drafts**, including #0003 `AARON` from the original pilot.

Each draft specifies every eligible source text/tail unit. The existing 50 pilots and the full `ABRAHAM` draft were not duplicated. `ABIDE` and `ARK OF BULRUSHES` were revised within their existing source-locked pilot patches.

Across the 1,000 entries of issue #109, **30 full first drafts** exist (the 6 pre-existing drafts plus these 24); **970 have no complete French draft**. Across the complete 9,380-entry encyclopedia there are **75 full first drafts**.

**These are source-locked translation drafts, not individually accepted editorial translations. No checkboxes were checked, no release produced.** A separate paragraph-by-paragraph bilingual collation and review decision is still required for each article.

## Translation and witness decisions

- In `ABIDE`, retain the *exact historical English quotations* that analyze `abide/abode`, explain the lexicographical abbreviation `a.`, and supply natural French glosses. Do not falsely present the English KJV/RV word study as a French Bible-version comparison.
- In `ARK OF BULRUSHES`, avoid the false implication that the palace women were necessarily members of the royal family; translate the historical narrative with the source's qualified language.
- The English `AARON` article contains `leaders of Da and Reuben`, while the existing French pilot draft says `des chefs de Dan et de Ruben`. The English witness may have a truncated proper name. **This needs printed-source verification before acceptance. No English master correction has been made.**
- The English `AARONITES` article has the punctuation `where it. denotes a family`. French draft removes the typographical obstruction for readability, but the historical source remains unchanged; verify the printed witness before any English-source repair.
- `AALAR` shows visible `ALLAR` but its original link provenance names `ISBE:ALTAR`. Retain its original target and `n` without silent remapping; investigate only if a canonical index/link audit establishes a defect.
- Preserve historical geographical identification in `ABDON (2)` and `ABANAH` as statements made in the early twentieth century, not as verified modern identifications.
- The English `ABDON (1)` source contains `Israelirish community`, a likely digital-text corruption; the French draft renders the apparent sense but **must not be editorially accepted without witness review**.
- The English `ABED-NEGO` source contains `it seems ore probable` and `Nebuehadnezzar`. The French draft renders the probable meaning without altering the English master; verify both spellings against the historical witness before editorial sign-off.
- All existing twelve flagged pilot-source anomalies remain unresolved; none was silently corrected.

## Technical validation and next editorial gate

CI batch and reading-proof workflows include both new patch files and require 75 complete reconstructed drafts, zero partial drafts, zero editorial sign-offs and publication disabled. Regression tests verify that the new articles remain in the frozen worklist, are deduplicated, and rebuild without changes to canonical identifiers, structural nodes, Scripture destinations or original Greek/Hebrew.

After passing CI, collate each complete French article against its *entire* English original, document an independent editorial decision, then mark the corresponding item in #109. Work in bounded batches with traceable PRs. Leave #109 open and do not publish a French module until the separate whole-corpus publication gate is met.

## Further bounded French first drafts — 24 November 2026

The independent source-locked draft file `batches/0004-short-a-entries.json` adds **nine complete first drafts**: source positions **#0027 `ABEL (2)`, #0029 `ABEL-CHERAMIM`, #0030 `ABEL-MAIM`, #0032 `ABEL-MIZRAIM`, #0034 `ABEZ`, #0035 `ABGAR; ABGARUS; ABAGARUS`, #0036 `ABHOR`, #0037 `ABI (1)`, and #0040 `ABIA; ABIAH`**. They reuse the original IDs, SWORD keys, source text-unit offsets, and Scripture reference targets. Historical English lexicography remains explicit in `ABHOR`; the `ABGAR` tradition is carefully identified as legend rather than established historical fact.

**Current coverage:** 39/1,000 first drafts in issue #109, with 961 entries still to draft; 84/9,380 first drafts across the encyclopedia. These nine are complete *first drafts* but have **no independent editorial acceptance**. Keep all issue checkboxes unchecked. No publication was initiated. Official CI and independent bilingual collation must precede sign-off.

## Eight additional short articles — 24 November 2026

The source-locked batch `batches/0005-short-ab-entries.json` adds eight full French first drafts, at canonical positions **#0039 `ABI-ALBON`, #0041 `ABIASAPH`, #0043 `ABIB`, #0044 `ABIDA`, #0045 `ABIDAH`, #0046 `ABIDAN`, #0048 `ABIEL`, and #0050 `ABIEZRITE`**. The extraction uses the corrected English master, reconstructs all eligible text/tail units, and preserves the English SWORD keys, TEI IDs, source-language spans, and original Scripture targets.

**Coverage after this batch: 47/1,000 complete first drafts in lot 1; 953 still without full drafts. Across the whole ISBE: 92/9,380 first drafts. Editorial sign-offs: 0.** This is first-pass translation, not release readiness.

- The English `ABIDA` article terminates unexpectedly at `Abidah in the King James Version in Gen.` Its incomplete citation is preserved as source evidence; French supplies no invented book/chapter/verse locator. Check the historical print witness before editorial acceptance.
- `ABIB` distinguishes the historical KJV name from the calendar discussion; its displayed cross-reference `CALENDAR` is translated to `CALENDRIER` without changing the destination.
- `ABIASAPH` retains the author's qualified chronological and genealogical assessments rather than rewriting them as established fact.
- Existing English source and all other drafts remain unchanged.

Both translation workflows now discover every `batches/*.json` source-locked file automatically. Tests check exact source fingerprint, duplicate keys, reference parity, completeness, article preview, and nonpublication. No checkbox in #109 is approved on the basis of these tests alone.

## Twenty-five short notices across A/AB — 24 November 2026

Source-locked first drafts in `batches/0006-more-short-ab-entries.json` cover canonical positions **#0054, #0057, #0059, #0063, #0065–#0066, #0069–#0079, #0082, #0091–#0092, #0095–#0096, #0099, #0102–#0103**. They include redirects/aliases and full lexical, biographical and geographical short articles. Exact source article IDs, `@n` keys and every original Scripture link remain unchanged.

**New checkpoint: 72/1,000 complete first drafts in issue #109, 928 pending; 117/9,380 complete first drafts corpus-wide. 0 editorially accepted.** All remain nonpublishable drafts.

Editorial matters for later bilingual validation:

- `ABILITY` and `ABLE` preserve the source's historical King James Version / Revised Version distinctions, retaining explanatory English phrases where French translation alone would obscure the lexical comparison.
- `ABLE` has the awkward English phrase `absence of in external obstacles`; the first French draft renders the readily apparent sense but no English source text is silently changed. Check historical print evidence before sign-off.
- `ABISSEI` / `ABISUE` contain traditional apocryphal book labels, some as unlinked original prose; they are retained as historical references rather than given unsupported new TEI targets.
- `ABRONAH` follows the historical author's geographical identification without presenting it as a newly verified modern location.

Re-run complete translation, reading-copy, source-identity and official TEI validation for this patch before merge. Do not check issue boxes or publish solely from these technical gates.

## Twenty-eight AC / short A notices — 24 November 2026

Source-locked batch `batches/0007-short-ac-entries.json` contains 28 complete full-article *first drafts* from canonical source positions **#0106–#0162**, with gaps for longer entries that have not been translated yet. It reuses the exact corrected historical English TEI and all canonical article IDs, SWORD keys, original Scripture references and cross-link targets.

**Wave 01 lot 1 checkpoint: 100/1,000 first drafts, 900 without drafts. Full corpus: 145/9,380 first drafts. Accepted editorial sign-offs: 0.** No issue checkboxes or French releases are authorized by these draft-only tests.

Source and editorial flags:

- Historical English `ACHAZ` concludes `The name of a King of Israel.`, which appears questionable for the biblical king Ahaz. The French first draft preserves that historical source assertion as `roi d'Israël`; independently collate with the printed witness and biblical history before editorial acceptance. Do not silently rewrite the historical master.
- `ACCARON` retains the original historical identification of Ekron and the uncertain dating/context of King Alexander; no modernized historical assertions have been added.
- `ACCOZ`, `ACITHO; ACITHOH`, `ACUD`, and other apocryphal articles preserve historical English version labels and legacy unlinked references. Any later link improvement must be separately source-audited and reversible.
- French visible titles (e.g. `ABYSSINIE`, `ACTES DE PILATE`) do not alter original `@n` or link identities.

The dynamically discovered batch must pass full reconstruction, text-unit source fingerprint tests, official TEI profile validation, and full reading previews in CI before merge. Independent bilingual editorial approval remains a separate later gate.

## Five full substantive articles in the first 50 source positions — 24 November 2026

Two additional source-locked batches, `batches/0008-abel-full.json` and `batches/0009-abel-places-and-abiezer.json`, add **five complete first-pass French articles**: `ABEL (1)` (#0026), `ABEL-BETH-MAACAH` (#0028), `ABEL-MEHOLAH` (#0031), `ABEL-SHITTIM` (#0033), and `ABIEZER` (#0049). `ABEL (1)` includes all five original substantive sections, with its original biblical references, scholarly qualifications, citations and M. O. Evans attribution retained.

**Current lot 1 coverage: 105/1,000 complete first drafts, 895 undrafted; whole corpus 150/9,380 complete first drafts. Editorial acceptance: 0.** No publication.

Source-witness and fidelity notes:

- `ABEL-BETH-MAACAH` contains the historical English phrase `Ijon and Da`, apparently a damaged place name. The French draft deliberately retains `Da`, while another part of the same article has `Dan`. The primary printed witness must be checked before editing or accepting this article.
- `ABEL (1)` retains the original 1915 author's alternative historical interpretations, qualified speculative claims, Septuagint discussion and biblical/theological distinctions. It is **not** a newly composed modern doctrinal article.
- Historical geographic identifications in `ABEL-MEHOLAH` and `ABEL-SHITTIM` are translated as the author's assessments, without asserting they have been reverified today.
- All original canonical `@n` / `xml:id`, original-language spans, bibliographic names, Scripture `cRef` and internal targets remain unchanged in the English TEI.

These are complete source-locked first drafts, *not independent bilingual editorial approvals*. Source and reading-copy CI must pass; checkboxes stay unchecked and French publication remains prohibited.

## Six complete historical article drafts — 24 November 2026

Three source-locked patch files add **six** previously undrafted entries within lot 1:
`ABI (2)` (#0038), `ABIJAM` (#0056), `ABILENE` (#0058),
`ABIMAEL` (#0060), `ABINADAB` (#0062), and `ABISHAG` (#0067).
Their full English source text units were exported directly from the pinned
historical TEI using the existing `scripts.export_translation_source`
tool; all original `@n` keys, IDs, Scripture locators, link destinations,
source-language elements, and bibliography remain source-owned.

**Updated coverage after full draft reconstruction is verified: 111/1,000
complete first drafts in lot 1; 889 without French drafts. Whole corpus:
156/9,380 draft entries. 0 independent bilingual editorial sign-offs.**

This tranche includes substantial full paragraphs, not article excerpts:
- `ABI (2)`: the complete historical discussion of Hebrew name components,
  scholarly disputes, and qualified theological deductions.
- `ABIJAM`: original textual-critical alternatives and the author's
  historically conditioned interpretation remain explicit.
- `ABILENE`: historical geographical and dynastic statements remain attributed
  to the original 1915 work, not silently modernized.
- `ABIMAEL`: Arabic naming conjectures and the original bibliography retained.
- `ABINADAB`: all four persons/referents, text variants, and uncertainty
  concerning the location of the ark preserved.
- `ABISHAG`: original author's historical explanation of David's care and
  Adonijah's request translated without imposing a modern interpretation.

**Status remains complete *unreviewed* first drafts, not editorial acceptance.**
The full source-locked reconstruction and reading-copy CI must pass before
merging. No task in #109 is checked, and no SWORD release is authorized.

## First exactly 100-entry translation cohort — 24 November 2026

**Cohort 001** is a bounded group of exactly **100 original canonical entries**,
individually frozen in `cohorts/COHORT_001_100_SHORT_NOTICES.json`
with their existing English source position, unmodified SWORD key, canonical
`xml:id`, exact source article fingerprint and patch file.

**Selection is intentionally transparent:** these are the 100 shortest
previously undrafted entries in lot 1, **all short cross-reference notices**,
rather than 100 full-length scholarly essays. Their source prose spans 14–45
eligible text characters per notice (3,099 characters across the cohort).
The editorial workflow still translates each complete *source article*,
including its headword and every original cross-reference; no excerpt is
counted as an article. This selection makes the raw article-count progress
move faster than the proportion of the encyclopedia's total prose translated.

Five source-locked patches contain **20 complete notice drafts apiece**:
`0013-wave01-redirects-batch-01.json` through
`0017-wave01-redirects-batch-05.json`. They reuse the original 100 entries;
not a single canonical identity or link is added, removed or reindexed.
Historical English pronunciation guides and proper names may be retained with
a source-unit reason. French display heads and cross-reference labels are
localized without changing original reference targets, including historically
specific terminology (e.g., `FARTHING`).

**Lot-1 draft coverage after validating these files: 211/1,000, with 789
undrafted. Across the entire source: 256/9,380 first drafts.**
**Editorially accepted: 0/1,000.** This is a draft-only milestone: no issue
checkbox is checked, and no translated SWORD release is authorized.

Every cohort item is structurally checked against the immutable original TEI,
and the added generic cohort regression test verifies the 100 original IDs,
source positions, fingerprint parity, exact patch files, uniqueness, and
nonpublication state. The full reconstructed French excerpt and readable
editorial proofs are independently exercised by the existing translation CI.
Bilingual article-level editorial collation and acceptance are still pending.
