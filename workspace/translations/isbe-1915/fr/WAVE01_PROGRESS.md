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

## Second 100-item source-locked French draft cohort — 24 November 2026

**Cohort 002 adds exactly 100 previously undrafted, complete historical English
source entries**, from 100 distinct `@n` keys and stable `xml:id` values. The
canonical positions, original source article SHA-256 fingerprints and four
25-item patch files are frozen in
`cohorts/COHORT_002_100_SHORT_ARTICLES.json`. Only the original canonical
worklist defines ordering or lookup; the cohort is a bounded editorial task
record, not a new index.

Selection uses the **next 100 shortest still-undrafted source entries** in
positions #0001–#1000, with all originally present text/tail units translated
or justified as proper-name/pronunciation preservation. This cohort includes
substantive short *biographical and lexical notices* as well as reference
redirects (46–112 eligible source characters apiece, **7,740 total**). Each
translation includes the *entire* historical article as represented in the
source TEI, never a truncated passage.

Complete draft patch files:
- `0018-cohort-002-short-articles-01.json` (25 original entries)
- `0019-cohort-002-short-articles-02.json` (25)
- `0020-cohort-002-short-articles-03.json` (25)
- `0021-cohort-002-short-articles-04.json` (25)

**Lot 1: 311/1,000 complete source-locked first drafts, 689 still undrafted.
Across the full original source: 356/9,380 complete first drafts.**
**Editorial acceptance: 0/1,000; no issue checklist boxes checked; no
French SWORD release permitted.** The article count must not be treated as a
percentage of total prose already translated.

Historical cautions for a later independent bilingual review:
- `AHBAN` and `AHUMAI` retain question marks qualifying the proposed name
  etymologies.
- `ARCTURUS` preserves the historical source's specific constellation wording
  rather than replacing it with a newly verified astronomical assertion.
- `ASSHURIM` retains the original unusual `Jokshah` spelling; confirm
  against the printed English witness before any editorial correction.
- `AVERSE` translates the source's historically conditioned lexical gloss
  without silently rewriting its original discussion.
- The article references to English versions, apocrypha and antiquarian source
  terminology are display-localized as applicable, while the canonical TEI
  source, article IDs and original destinations remain immutable.

Source identity, every complete text unit, source-language spans, link and
Scripture-reference parity, reconstructed French reading proofs, manifest
uniqueness and the official TEI profile must pass in CI before merge.
Independent editorial sign-off remains explicitly out of scope.

## Third 100-article historical French first-draft cohort — 24 November 2026

**Cohort 003:** exactly **100** additional complete first-pass translations from the
original corrected English TEI, frozen in
`cohorts/COHORT_003_100_CONCISE_ARTICLES.json`, with the original canonical
positions, English `@n` keys, `xml:id` identifiers, stable per-article SHA-256
fingerprints, and one exact source-locked patch reference for each entry.

All 100 are the shortest **previously undrafted** English articles after the
first two independent cohorts. Every included original entry is translated
**in full**, retaining all source TEI cross-references, Scripture links,
Greek/Hebrew source spans and original editing boundaries. These articles
are increasingly varied concise historical, biographical and lexical
notices, including the original authors' alternate readings and source
qualifiers, not just redirects.

English eligible source prose this cohort: **14,864 characters**, with
individual entries 114–187 characters. This is an article count metric,
not the proportion of the original encyclopedia's total prose translated.

Four source-locked patch files, each with exactly 25 entries:
- `0022-cohort-003-short-articles-01.json`
- `0023-cohort-003-short-articles-02.json`
- `0024-cohort-003-short-articles-03.json`
- `0025-cohort-003-short-articles-04.json`

**Updated lot 1 first drafts: 411/1,000 (41.1%); remaining undrafted:
589. Whole source: 456/9,380 complete first drafts. Editorial sign-offs:
0/1,000, so task checkboxes must stay unchecked. Publication: forbidden.**

Notes for later independent bilingual editorial collation:
- `ADADRIMMON` retains the original source's historical connection with
  the death of Josiah rather than adding external modern identifications.
- `ADDUS`, `AKKOS`, and `ASTAD` preserve the distinction between
  English biblical manuscript editions and original person/place names.
- `AGIA` retains the surprising source reference to descendants of
  Abraham in 1 Esdras; the historical witness requires separate collation
  before acceptance, not silent correction.
- `ALLEG(E)` and `AT ONE` explain the English lexical expressions rather
  than pretending their French equivalents have the same etymological form.
- `ARIDAI`, `ARIDATHA`, `ALVAN`, and similar entries preserve the author's
  tentative etymologies and manuscript variants, not modernized certainties.
- Ancient author interpretations, even when questionable, remain historical
  claims, not silently rewritten encyclopedic updates.

Before merging, require full source-locked reconstruction, 456 article
reading proofs, cohort uniqueness and immutable identifier checks,
and complete official TEI validation. Independent bilingual approval is a
separate, still-uncompleted editorial gate.

## Fourth 100-entry historical French draft cohort — 24 November 2026

**Cohort 004 adds exactly 100 more complete source-locked first drafts**, all
from previously undrafted original `@n` entries among canonical positions
#0001–#1000. They are frozen, without creating a second index, in
`cohorts/COHORT_004_100_SHORT_HISTORICAL_ARTICLES.json`, with exact canonical
source positions, source keys, TEI `xml:id`, per-entry source fingerprints and
source-locked patch filenames.

- `0026-cohort-004-concise-articles-01.json` — 25 complete entries
- `0027-cohort-004-concise-articles-02.json` — 25 complete entries
- `0028-cohort-004-concise-articles-03.json` — 25 complete entries
- `0029-cohort-004-concise-articles-04.json` — 25 complete entries

These are the shortest 100 among the remaining 589 undrafted lot-1 entries,
but are significantly more involved than the previous cohorts: **25,037
eligible historical English source characters**, 188–323 per article, with
multiple persons, original edition distinctions, historical lexical notes,
and ancient geographic identifications. All source-owned reference
destinations, internal links and canonical positions remain unchanged.
Source-historical pronunciation and proper names may be retained explicitly.

**Wave 01: 511/1,000 full first drafts (51.1%); 489 undrafted.
Entire ISBE: 556/9,380 complete first drafts.
Independent bilingual editorial approvals: 0/1,000; 0 issue checkboxes
checked. No French SWORD publication authorized.**
This is article-count coverage, emphatically **not** 51.1% of the English
source's entire prose by volume.

Separate bilingual editorial collation flags from this cohort:

- `AGADE`: the historical author's date of approximately **3500 BC** for
  Sargon is retained as a historical claim, not asserted as current research.
- `AGGABA`: source wording calls the temple servants "descendants of
  Abraham" despite naming Hagabah/Hagaba. We have translated the *actual*
  English source and flagged it; no silent correction to a different person.
- `AHIEZER`: the English phrase "when a furtive before Saul" is anomalous
  in the supplied witness; the French interprets it as fleeing Saul. This
  exact passage requires verification against the historical printed witness
  in bilingual review.
- `ARAM`: unusual original English reference `Mt 13:4` remains owned by the
  canonical source; determine whether it is a historical source error only
  through separately documented source collation, not a translation edit.
- `ASHKENAZ`: source cites `1Ch 16`; unchanged on purpose, requires
  separate source-witness check.
- `ANATH`: original bibliographic page span `105-896` was preserved rather
  than silently replaced.
- `ANTIOCHIS`: translation explicitly preserves that Antiochus granted
  the cities to Antiochis; the recipient is not the king.
- `AWAY WITH`, `ALBEIT`, `ARIGHT` and other English lexical entries
  explain their original English wording, without falsely inventing French
  etymologies.
- Uncertain name etymologies and ancient location identifications retain
  the original qualifiers ("perhaps", "apparently", "probably").

Every cohort must pass full reconstruction and source fingerprint checks,
manifest uniqueness and original key parity, French editorial reading-copy
rendering for all **556** first drafts, and the official TEI checks before
merge. Bilingual editorial sign-off remains *a separate, uncompleted gate*.

## Fifth 100-entry French historical first-draft cohort — 24 November 2026

**Cohort 005 adds exactly 100 complete original English source entries**, in
four JSON batches of 25 source-locked French first drafts. Each entry is
traceable by the original canonical worklist position, English `@n`,
immutable TEI `xml:id`, per-article SHA-256 and patch path in
`cohorts/COHORT_005_100_HISTORICAL_ARTICLES.json`. The cohort is an
editorial selection record, **not a new French dictionary index**.

The selection was the next 100 shortest **previously undrafted** entries
among positions 1–1000, excluding the previous four cohorts and pilot.
Every historical original entry is translated **in its entirety**, not
as isolated extracts. Translation of this cohort covers **39,551 eligible
English source characters**, 324–488 per article: technical biblical
lexicography, ancient history, Scripture references and text-critical
variants, rather than merely short redirects.

Four patches, exactly 25 original entries each:
- `0030-cohort-005-historical-articles-01.json`
- `0031-cohort-005-historical-articles-02.json`
- `0032-cohort-005-historical-articles-03.json`
- `0033-cohort-005-historical-articles-04.json`

Independent pre-CI checking: exactly 100 distinct English article IDs;
**476 source text units** in identical original order, **402 translated
units and 74 justified preserved historical names, pronunciations and
labels**; zero long untranslated historical prose units; no source-unit
identity mismatch or omission.

**Wave 01: 611/1,000 complete source-locked first drafts (61.1%);
389 remain undrafted. Entire 9,380-entry source: 656 complete first
drafts. Independent bilingual editorial approvals remain 0/1,000 and
issue #109 checkboxes 0/1,000. No French release authorized.**
The 61.1% is an original-article **count**, not the proportion of all
English encyclopedia prose translated.

### Editorial witness alerts (collation required, not silently amended)

- `AGGAEUS`: the original English witness surprisingly says
  "Abraham prophesied" where the entry concerns Haggai. The French
  draft explicitly attributes that wording to the English source.
- `ADVERTISE`: source says "Balsam advises Balak" rather than the
  expected biblical name. Preserved as a source-reported spelling,
  clearly flagged in the French draft.
- `ANAB`: original says "twelve males" in a geographical distance
  statement; French renders the obvious *distance unit* interpretation
  while leaving the English text untouched. Confirm against print.
- `ANCIENT OF DAYS`: original author's interpretation of Daniel 7
  must be faithfully distinguished from subsequent theological
  agreement or disagreement; translated as an attributed historical
  interpretation, never a newly asserted doctrinal verdict.
- `ALMIGHTY` and `ADONAI`: original ancient-name etymologies are
  represented with their uncertainty; other source-theological claims
  (including the historic vowel explanation of the tetragrammaton)
  are preserved as descriptions of the author, not rewritten.
- `AMASHSAI`, `AG(E)E`, `ALIAH` and `ALIAN`: uncertain manuscript
  readings remain uncertain, and the canonical cross-reference
  destinations are never rewritten.
- `ASPHAR, THE POOL`: alternative ancient-site identifications
  retain the original conditional language.
- `ARROWSNAKE`: the debate over serpent versus bird is preserved,
  including the historical citation of Gesenius.

Before merging, require automatic source-lock reconstruction of
**all 656 complete drafts**, 5-cohort unique original ID checks,
all 656 French reading proofs and official original TEI RELAX NG /
Schematron tests. **None** of these automated checks constitutes
independent bilingual editorial sign-off, which remains pending.

## Sixth 100-entry French historical first-draft cohort — 24 November 2026

**Cohort 006:** exactly **100 new, complete** canonical historical English
source entries translated into French first-draft form, each with unchanged
English `@n`, original canonical worklist position, TEI `xml:id`,
source-article SHA-256 and one exact source-locked patch path in
`cohorts/COHORT_006_100_HISTORICAL_ARTICLES.json`. This manifest is not a
new index or a different French versification.

Four patches, each with **25 entire original entries**:
- `0034-cohort-006-historical-articles-01.json`
- `0035-cohort-006-historical-articles-02.json`
- `0036-cohort-006-historical-articles-03.json`
- `0037-cohort-006-historical-articles-04.json`

**Actual source text:** **64,555 eligible English characters**, from
491 to 857 English characters per article. Selection: 100 shortest
*previously undrafted* complete entries from the fixed first 1,000;
these are increasingly substantive short-to-medium lexical, theological,
historical, archaeological and biographical articles, not long essays.
Exactly **613 source text units** compared by original node index, part,
source text, source article and SHA-256, consisting of **482 translated
units and 131 explicitly justified unchanged names, bylines and historical
pronunciation/cross-reference labels**; no unexplained long English
prose or omitted original text units.

**Cumulative first drafts:** **711/1,000** original wave-01 articles
(71.1% *by article count*), leaving **289** not yet drafted in wave 01.
Whole ISBE original index: **756/9,380** complete first drafts.
**Independent bilingual editorial sign-offs: 0/1,000**, checklist boxes
in issue #109: **0/1,000**. The French SWORD module must not be
published. This article count is **not** 71.1% of all original prose.

### Outstanding witness and editorial questions

- **ATHARIM source contamination:** the corrected canonical English
  source includes an unrelated clause about Charles II of England
  between the Numbers 21:1 discussion and the HORMAH cross-reference.
  The clause is source-locked and translated as witnessed; it was **not
  silently removed**. Independently tracked in
  **[source integrity issue #125](https://github.com/icfmp/Bible-Resources-ISBE/issues/125)**.
  Source collation and original-witness proof must precede any change to
  the English master and any bilingual acceptance of this draft.
- **ARNI:** the original English text has an unexpected Matthew 13:4
  cross-reference in a genealogy comparison; the original Scripture
  identifier is unchanged pending historical source collation.
- **AGUR:** the original author's appraisal of Agur as "agnostic" is
  presented as *the author's interpretation*, not as a new endorsed
  theological conclusion.
- **APPHIA:** the historical account of her alleged martyrdom is
  represented with its traditional attribution, not independently
  established as fact.
- **ANTIOCHUS I, II, V and VII, ARATHES:** original historical dates,
  identifications and bibliographic sources remain source claims.
- **ARIEL:** author's competing etymologies and readings are preserved;
  all references and TEI targets stay canonical.
- **AYIN and ALEPH:** original pronunciation and numerical descriptions
  remain historical descriptions, without changing Hebrew source text.
- **ANISE; DILL:** distinguishes actual plant identity from the English
  Bible vocabulary reported by the original article.
- **ANCIENT doctrinal interpretive sources:** this is translation of a
  historical encyclopedia, not silent rewriting to match later
  doctrinal positions.

Before merging, require **756 fully reconstructed source-locked drafts**,
all six frozen 100-entry cohort fingerprint/ID checks, 756 complete
readable French proofs, the original TEI regression suite and independent
official RELAX NG plus Schematron validation. No technical CI check
can substitute for later bilingual editorial approval. The original
corrected English source SHA-256 remains
`5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.

## Seventh source-locked 100-entry French historical draft cohort — 24 November 2026

**Exactly 100 complete original historical ISBE articles are translated into
French as first drafts in this cohort**, in four patches with 25 full entries
each. Frozen canonical selection and exact patch mappings:
`cohorts/COHORT_007_100_HISTORICAL_ARTICLES.json`.

- `0038-cohort-007-historical-articles-01.json`: 25 full entries
- `0039-cohort-007-historical-articles-02.json`: 25 full entries
- `0040-cohort-007-historical-articles-03.json`: 25 full entries
- `0041-cohort-007-historical-articles-04.json`: 25 full entries

Selection: **the next 100 shortest previously undrafted** original articles
from the fixed positions 1–1000. Their **113,544 eligible English source
characters**, 858–1,498 per original article, represent a much more
substantial body of historical, biblical, exegetical and lexicographic
prose than the first six cohorts. This is still not a proportion of the
entire ISBE's English word count.

Pre-CI independent source-unit audit: exactly **100 distinct original
article IDs**, 1,050 original source text units in original order,
**891 explicitly translated**, **159 deliberately preserved and
justified original author names, historical pronunciations, canonical
headwords or reference display labels**, **zero** long, unexplained
preserved English prose units, **zero** original unit identity mismatch
or omission, and **zero** incomplete first-draft article. Every patch
remains labelled `unreviewed_drafts` and
`publication_permitted: false`.

**Cumulative wave-01 first drafts: 811/1,000 (81.1% by article count),
189 undrafted. Entire original 9,380-entry ISBE: 856 complete
first drafts. Independent bilingual editorial approvals: 0/1,000.
Issue #109 checked boxes: 0/1,000. No French SWORD publication.**
These metrics are *not* source-prose-volume coverage.

### Source-witness collation and editorial alerts

- **[Issue #127](https://github.com/icfmp/Bible-Resources-ISBE/issues/127):
  AENON and ATARGATIS have unmistakable cross-entry splices** in the
  existing corrected original English TEI, respectively from ADVOCATE
  and ASYLUM. The French draft preserves the supplied fragment with an
  explicit editorial bracket explaining the contamination; the
  untouched English master must be collated against a scanned source
  before any separate, reversible correction.
- **AFFIRM; AFFIRMATIVES:** source itself reads `1Ti 17`,
  `Isa 88:1` and `bye` in the example about affirmative and negative;
  these are documented source errors, *not* silently repaired biblical
  locators or text.
- **ALEXANDER BALAS:** an incoherent transition around
  `Demetrius was defeated by Alexander II took up the cause...`
  needs printed-witness comparison before historical reconstruction.
- **ALCIMUS:** the existing English narrative attributes to Simon
  Maccabaeus actions usually associated with Judas/Jonathan; its
  historical assertions are translated as *claims of the source*,
  with no silent editorial substitution.
- **ACACIA:** the original description of fine leaves and flowers is
  evidently truncated (`finely leaves ular flowers`); translated
  with an explicit flag rather than invented botanic terminology.
- **ANATHEMA, ABSOLUTION, ANGELS OF THE SEVEN CHURCHES, ASLEEP, AGREE,
  ALPHA AND OMEGA:** historically attributed doctrinal interpretations
  are faithfully translated, including significant differences among
  Christian interpreters, not silently rewritten to fit a new thesis.
- **ADAMANT, ARIOCH, AENON, APHARSATHCHITES, ASARAMEL:** original
  manuscript hypotheses and geographic identifications remain
  conditional, with original cross-reference targets unchanged.

Source master SHA-256 unchanged:
`5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.
Every original `@n`, TEI `xml:id`, reference target, historic
editorial byline and article fingerprint remains source-locked.

**Before any merge**, run source-locked reconstruction of all **856**
first drafts, all seven frozen 100-entry cohort mapping and uniqueness
checks, all 856 French readable article proofs, full canonical
9,380-entry TEI regression suite and official TEI RELAX NG and
Schematron validation. **Independent bilingual collation/acceptance**
remains a separate, uncompleted publication gate.

## Eighth source-locked substantive first-draft milestone: 50 articles — 24 November 2026

**This milestone contains 50 entirely translated historical ISBE articles**, not
the entire 100-entry extraction candidate. The much denser eighth selection
(100 shortest then-undrafted source entries: **268,351 source English
characters**, 1,544–4,491 eligible English chars per entry) was divided
into smaller independently mergable and testable units. Only the first
50 of those 100 candidates, in unchanged canonical source-index order,
are finished. The other 50 candidate articles are still **undrafted**.

The frozen 50-entry editorial cohort is at
`cohorts/COHORT_008_50_SUBSTANTIVE_ARTICLES.json`. Complete first-draft
patches, both intentionally non-publishable:

- `0042-cohort-008-substantive-articles-01.json`: 25 full entries, **59,326** original English eligible chars, 403 exact source text units
- `0043-cohort-008-substantive-articles-02.json`: 25 full entries, **71,962** original English eligible chars, 472 exact source text units

**Combined: 50 distinct canonical articles; 131,288 English source
characters; 875 source text units; 783 translated and 92 preserved
original canonical/proper-name/author byline units with a reason.**
Independent pre-CI audit confirms no omission, changed reference locator,
source fingerprint mismatch, extra Greek/Hebrew script, unexplained long
unchanged prose or incomplete article.

**Cumulative first-draft status after merge: 861/1,000 (86.1% by article
count) in wave 01, 139 still undrafted; 906/9,380 complete source-locked
French first drafts across the whole original ISBE.**
These article counts are *not* relative source-word coverage.
Editorially approved by independent bilingual review: **0**.
Issue #109 checked boxes: **0/1,000**.
French SWORD edition published: **no**.

Historical/source-critical caveats are documented in
[issue #129](https://github.com/icfmp/Bible-Resources-ISBE/issues/129):
broken English in `ACCEPT; ACCEPTABLE; ACCEPTATION`,
`ABYSS` linked New Testament passage, `ACHMETHA` transcription
failures, `AHIMAAZ` `Dared`, and `ANNA` `distraction`.
No source text, original references, original-language strings,
`@n` keys, canonical `xml:id`, or manuscript fingerprints are
silently rewritten. Period-specific racial/ethnographic views in
`AFRICA`, contested historical identifications in `AMRAPHEL`
and authorial doctrinal interpretations in `AGONY` and
`ANTEDILUVIANS` are translated with source attribution, not
endorsed or silently updated. Original English witness collation remains
pending; dependent French patches must be regenerated if an English
witness correction is later accepted.

The immutable English source master remains SHA-256
`5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.

**Technical merge gates:** reproduce 906 source-locked full first drafts
and readable previews, assert all eight frozen cohort manifests, run all
canonical TEI tests, and pass pinned official TEI RELAX NG and
Schematron validators. These automated tests do not establish
independent human editorial approval. The historical 1915 English
master and no part of the application are to be modified in this PR.

## Ninth substantive cohort — first five complete French first drafts (24 November 2026)

A bounded, source-locked first set of **five** previously undrafted complete historical articles has been drafted from the corrected English TEI: original canonical positions #0594 `APHEK`, #0638 `APPII FORUM`, #0639 `APPLE, OF THE EYE`, #0892 `ASSURANCE`, and #0907 `ASTYAGES`.

- First-draft patch: `batches/0044-cohort-009-substantive-articles-01.json`; frozen exact original IDs, keys, positions and article SHA-256 values: `cohorts/COHORT_009_5_SUBSTANTIVE_ARTICLES.json`.
- All **43 original eligible text/tail units** are represented: **8,148** original English source characters. Scripture `ref` text and targets are source-owned, untouched. Each historical-author byline is retained with an explicit preserve reason; original-source fingerprinting was cross-checked against an already accepted cohort fingerprint algorithm.
- Draft status only: **866/1,000** complete, source-locked first drafts in wave 01 (86.6% by original article count); **134** wave-01 originals still without complete French drafts; **911/9,380** first drafts in the full corpus.
- **0 independent bilingual editorial approvals; 0 checkboxes in #109; no French SWORD publication.** The counts are not English prose-volume coverage.
- Witness/editorial flags: `ASTYAGES` has an orphaned source `I, king` that remains visibly signaled in French as `« I », roi` pending print collation; `APPII FORUM` shows `Revised Verson` and an unmatched Scripture-reference closing parenthesis in the historical English. Translation fixes none of the English master, original SWORD keys or biblical link targets. Any later English source repair belongs in a separate reversible witness PR.

Technical and editorial gates: the full draft reconstruction and reference/ID parity CI, all TEI checks and independent per-article bilingual acceptance are required before editorial checkboxes or release. The patch deliberately changes no historical English master, original article identity, canonical index or app code.

## Tenth substantive cohort — five more complete French first drafts (24 November 2026)

Five additional **entire historical English ISBE entries** now have source-locked, unreviewed first French drafts, without changes to the canonical English source: #0694 `ARCHERY`, #0761 `ARRAY`, #0825 `ASHES`, #0846 `ASIARCH`, and #0969 `AVENGE; AVENGER`. The original index `@n` and `xml:id` identities, exact source article fingerprints, and unchanged reference targets are frozen in `cohorts/COHORT_010_5_SUBSTANTIVE_ARTICLES.json`.

- Patch: `batches/0045-cohort-010-substantive-articles-01.json`, representing **84 complete original eligible text/tail units** and **8,704 source English characters**; author credits, historically specific English Bible wording, original language terms and Scripture reference labels are retained or translated with context, never re-indexed.
- Once this change is merged and CI passes, the first 1,000 English articles have **871/1,000** complete unreviewed French drafts (87.1% by source-article count), **129 undrafted**, and the entire 9,380-entry encyclopedia has **916** complete unreviewed first drafts. This percentage is **not** English-prose-volume coverage.
- **0 independently bilingual-editorially accepted articles, 0 issue #109 checkboxes checked, no French SWORD release**. Validation of patch completeness/TEI and authorial meaning is not a publication approval.
- Source witness/editorial caveat: `ASIARCH` includes the original historical form `Commune Asioe`, retained verbatim with attribution rather than silently regularized. `ASHES` historically attributes generalizations about Oriental mourning practices to its early-20th-century author; this is a translation, not a modern endorsement. `ARRAY` and `AVENGE; AVENGER` retain the source's King James Version / Revised Version lexical comparisons and original reference targets.

All five need independent bilingual editorial collation and, where warranted, printed-source witness checking before article approval. The original 1915 corrected English TEI fingerprint is unchanged.

## Eleventh substantive cohort — five complete source-attested French first drafts (24 November 2026)

Five previously undrafted full original historical articles are added as explicitly **unreviewed** source-locked translations: #0751 `ARNON`, #0828 `ASHKELON`, #0843 `ASIA`, #0942 `ATTALIA`, and #0960 `AUTHOR`. The full original index, `@n` SWORD source keys, `xml:id`, references and original English master are unchanged. The exact original fingerprints and indices are frozen in `cohorts/COHORT_011_5_SUBSTANTIVE_ARTICLES.json`.

- `batches/0046-cohort-011-substantive-articles-01.json`: all **48 original eligible text/tail units** and **9,689 source English characters** accounted for in complete articles. Historical bibliography, original lexicography, article structure, scripture destinations and author credits retained.
- Expected after CI-passing merge: **876/1,000** complete unreviewed first drafts in wave 01, **124 original articles undrafted**, and **921/9,380** complete unreviewed first drafts across the ISBE source. These numbers are by source-article count, not original English prose volume.
- **0 independent bilingual editorial approvals, 0 boxes checked in #109 and no French SWORD release**; these are working drafts, not accepted French articles.
- `ATTALIA` print-witness concerns: historical English source says `Louis IV` for the 1148 expedition; this requires independent collation and is explicitly attributed as `Louis IV, selon le texte source` in French, rather than silently replaced. Original English sentence `The town possesses considerable which is of archaeological interest.` appears to omit a noun; the French draft flags the lacuna rather than silently editing the historical English. Its historical demographic/geographic descriptions are attributed to the early twentieth-century author.
- `AUTHOR` maintains the historical writer's theological argument that `archegos` in Hebrews 12:2 can mean `leader` rather than automatically asserting this as modern exegetical consensus. `ASHKELON` source assertions about Herod's birthplace and ancient city chronology remain attributed historical claims, not independently reverified.

A separate original print-witness review and independent full bilingual article collation are required before any of the five articles receives editorial approval. Original corrected English master SHA-256 remains `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.

## Twelfth substantive cohort — five source-locked complete French first drafts (24 November 2026)

Five previously undrafted **complete original 1915 ISBE entries** now have faithful French first-pass drafts, ordered by their unchanged original source positions: #0572 `ANTIOCHUS IV; ANTIOCHUS EPIPHANES`, #0610 `APOLLONIUS`, #0768 `ARSACES`, #0818 `ASHDOD` and #0880 `ASSESSOR`.

- Source-locked patch: `batches/0047-cohort-012-substantive-articles-01.json`. Frozen five-entry manifest: `cohorts/COHORT_012_5_SUBSTANTIVE_ARTICLES.json`.
- All **43 eligible original text/tail units** represented; **10,429 eligible source English characters**, translated in full or deliberately preserved with explicit proper-name/byline reasons. Scripture reference nodes, original-language spans, canonical `@n`, `xml:id`, cross-reference destinations and entire English TEI master remain unchanged.
- Expected upon CI-passing merge: **881/1,000** complete source-locked, **unreviewed** French drafts (88.1% by original article count), **119** still undrafted in issue #109; **926/9,380** complete first drafts across the whole ISBE source.
- **0 independent bilingual editorial approvals; 0 checkboxes in #109; no French SWORD publication.** These article counts do not measure total source prose volume.

Editorial witness flag: the source's `ANTIOCHUS IV; ANTIOCHUS EPIPHANES` says that Ptolemy VI died in 173 BC, which conflicts with the historical chronology normally given for Ptolemy VI. The French draft faithfully retains the source's wording, without presenting the historical claim as an independent verification or silently altering the English original. Authenticate the printed 1915 witness and distinguish transcription error from authorial historical error **before** accepting the article editorially. Historical opinions, biblical citations and bibliographic ascriptions in the other four entries remain attributed to the original historical ISBE authors.

Reconstruct all **926** source-locked unreviewed drafts, check article and manifest uniqueness/fingerprints against the exact English master, render full readable proofs, run TEI profile/official validators and require independent bilingual review before any approval. No application code or historical source is changed by this batch.


## Thirteenth substantive cohort — five complete French first drafts (25 November 2026)

APPEAL, ARABIC VERSIONS, ARISTOBULUS, ASHAMED and AX (AXE); AX-HEAD: 90 mutable units, 11,696 source characters. Batch 0048 and cohort 013 preserve canonical identity and source references. Expected after successful CI and merge: 886/1,000 first drafts, 114 remaining; 931/9,380 corpus-wide. No independent editorial approvals or publication. Source witness concerns: retain the stray CR in ARISTOBULUS and the spelling Sasdish in ARABIC VERSIONS pending printed-source collation; retain historical assertions as authored.
