# Editorial triage: missing articles and non-content apparatus

Status: **research evidence, no authorized textual change** (2026-11-22).

## Authority and separation of layers

- The immutable CrossWire SWORD 2.2 ZIP and IMP export are digital *witnesses*, not the editorial authority for a critical edition.
- The 1915 five-volume **James Orr / Howard-Severance** printed encyclopedia is the historical comparison target. Do not substitute the later Bromiley revised edition.
- The source-faithful canonical TEI P5 baseline (SHA-256 `a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25`) is preserved unchanged until reviewed, source-backed deltas can be validated.
- Material created only for electronic distribution (CrossWire notes, licensing banners, OCR or transcription credits, maintenance notices, navigation instructions, source-key-generated display headings) must not be mistaken for original article prose. Keep provenance in repository metadata and manifests rather than duplicating it in the reading text.
- Historical author attributions, quotations, bibliography, critical observations, and original editorial notes that explain the work or text **are substantive** and remain unless a specific historic-source review shows otherwise. The rule is **relevance and origin**, not whether the word “note” is present.
- Record removals as explicit, reversible, source-SHA-bound deltas, including affected stable unit IDs, exact original content, evidence and rationale. Do not introduce bulk regex deletions or silently relax source-parity tests.

## Proven empty-source entries: 31 missing content records

See issues #7 and #12, PRs #8 and #11, and [full source-locked context audit](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45069263570).

All 31 cases are **entire article records with an empty sole paragraph**, not isolated whitespace inside complete articles. All paragraph IDs end in `-n000003`. The preceding node is the synthetic entry heading; there is no next paragraph. Removing the empty `p` alone would make the markup cosmetically cleaner but would conceal the missing-content problem.

### Independently attested original content

| Key | Print witness evidence | Digital source status | Editorial disposition |
| --- | --- | --- | --- |
| ABISSEI | 1915 vol. I, printed *ABISSEI* article after *ABISHUR*, before *ABISSUE*; the scan text includes an identification as an ancestor of Ezra and biblical cross-references | Empty in CrossWire-derived canonical TEI | **Text recovery required**; exact type, accents, punctuation and page image must be checked before transcription |
| AMNON | 1915 vol. I, printed *AMNON* article following *AMMONITESS*, before *AMOK*; the scan text includes two numbered definitions | Empty in CrossWire-derived canonical TEI | **Text recovery required**; printed spelling, Hebrew, punctuation and section boundaries need page-image proof |

**Source identification:** James Orr, ed., *The International Standard Bible Encyclopaedia*, Chicago: Howard-Severance, 1915, vol. I (*A–Clemency*). Digitized scan hosted at https://commons.wikimedia.org/wiki/File:The_International_Standard_Bible_Encyclopedia_Volume_1.pdf . Searchable scan text: https://upload.wikimedia.org/wikipedia/commons/c/c7/The_International_Standard_Bible_Encyclopedia_Volume_1.pdf . Independent transcriptions: https://bible-history.com/isbe/a/abissei and https://www.internationalstandardbible.com/A/amnon.html .

**Limit:** textual presence was corroborated in the scan's searchable text. A page-image inspection was attempted but the PDF screenshot service rejected this ~50 MB file; **the printed pages and exact lineation were not visually certified**. This is therefore not permission to copy either online transcription into the master. Exact printed page and PDF image index remain open.

## Complete provisional classification of the 31 missing records

A batch comparison against the **1915 volume-I searchable witness** and independent ISBE text reproductions has now produced a source-linked classification for **all 31 entries** in `workspace/reviews/empty-article-recovery-ledger.json`:

- **21 likely substantive article records** (including ABISSEI and AMNON, independently attested in the 1915 scan text).
- **10 likely historical cross-reference records**, which can be restored as valid editorial navigation rather than invented encyclopedic prose. Evidenced examples include ASTARTE; ASTORETH → ASHTAROTH; COMING OF CHRIST → ADVENT / PAROUSIA; PROSTRATION → ATTITUDES; REGENERATION, BAPTISMAL → BAPTISMAL REGENERATION; and PAUL, VOYAGE AND SHIPWRECK OF → PAUL, THE APOSTLE / PHOENIX.

These are **provisional genre hypotheses**, not corrections already committed to canonical TEI. Online reproductions may themselves descend from earlier digital versions and do not establish text-accurate correspondence with the printed 1915 volumes. All 31 records have exact source keys and preserved stable IDs; each classification links its supporting witness and states uncertainty. Printed page-image checking, detailed punctuation/structure transcription, target verification, and rights clearance remain outstanding.

A GitHub Actions attempt to fetch the five Internet Archive OCR datasets failed with an external TLS error. The one-off network downloader and workflow were discarded rather than leaving a permanently failing research pipeline; the source-backed editorial classification itself is retained and tested.


## Non-content notice audit

The source-locked [full-corpus content scan](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45069147164), delivered by PR #10, matched 21 text units (24 occurrences), all with digital-process vocabulary such as `transcribed`, `transcriber`, or `scanned`. Many of these words describe the transmission of ancient manuscripts, a legitimate scholarly subject. **Zero automatically removable notes were established by this lexical scan.**

The canonical structure inventory currently has **no `note` elements** in its article markup; this does not prove that parenthetical/editorial prose or process notices are absent, only that there are no explicitly TEI-tagged notes. Further review should look for substantive prose islands, author signatures and suspicious introductions/end matter and should compare them with the historic printing, not rely solely on keyword matching.

### Next editorial gates

1. Identify the exact printed page and visually compare the 31 empty records against the 1915 scans. Start with the two attested missing entries, then proceed across volumes in batches.
2. Classify possible non-content notices as `historic-authored`, `historic-editorial-content`, `digitization-only`, `navigation-only`, or `uncertain`, with individual evidence.
3. For each approved addition/removal, record original/source and revised-text hashes and stable unit mapping. Reject changes to unaffected article text and IDs.
4. Validate the resulting separate editorial edition through pinned TEI P5 RELAX NG, Schematron and article-reference audit. Keep original digital witness intact.
5. Rights and translation publication remain blocked by #1 until separately cleared.

## Recovery checkpoint — second text batch (2026-11-22)

**Historical genre correction:** `JOSIBIAH` is not a prose article; its independent 1915-attributed transcription contains a pronunciation and `See JOSHIBIAH`. It is now the **eleventh** provisional original-redirect record. The prior first-pass classification was wrong and is corrected in the versioned source-gap ledger.

Six more CrossWire-empty entries have now been transcribed into the **noncanonical** review specimen: `BEERA`, `ITHLAH`, `MANASSITES`, `SAVIAS`, `SESIS`, and `HASRAH`. Each is restricted to the actual article passage from its own 1915-attributed reproduction; HTML menus, website terms, recommendations and copyright/bibliographic boilerplate are **excluded**. The exact secondary witness is recorded per entry in `workspace/reviews/print-prose-candidate-v1.json`.

Combined preview target: **11 provisional redirects plus 9 prose entries**, with 9,360 other article texts and all original identifiers preserved. This is an editorial research specimen, **not** the canonical text or an approved printed transcription. No invented expansion or silent editorial modernization is permissible. Final page-image collation and rights checks remain required.

## Guard against electronic-edition paratext at ingestion

The provisional print-text recovery builder now **rejects** distinctive website boilerplate before serializing recovered prose (e.g. `Copyright Statement`, `Bibliography Information`, `Popular Articles`, `Share Tweet Save`, `Bible Study Tools`, HTML `footer` or `nav` elements). It fails rather than silently sanitizing text. This prevents modern website additions from entering a historical encyclopedia article and documents exactly where the provenance boundary lies.

The check intentionally does **not** reject generic historical terms such as `editor`, `note`, or `copyright`: those can be substantive encyclopedia prose. This is a candidate-import QA gate, **not** proof that all content of the original CrossWire source has been reviewed for unrelated historical/editorial annotations. Every deletion from the original canonical witness still requires its own source-backed, reversible editorial delta.

## Redirect transcription fidelity: preserve visible text

The 11 previously missing digital redirect records have now been compared with their own individual 1915-attributed independent entry reproductions. The review manifest records each **complete short visible secondary-witness text** and the source URL, not just its inferred target. Five source entries include historical pronunciation preceding the redirect (ASTARTE; ASTORETH, DUALISM, PROSTRATION, STANDING, JOSIBIAH). Both review builders are required to reproduce the recorded short text **exactly** while linking to an actual existing article and retaining original paragraph IDs. Existing article-level link precision remains intentionally limited where the printed source mentions a specific subsection.

This is still a **secondary-transcription comparison**, not image-verified historical print approval. Site furniture is excluded and no original article is modified in the canonical CrossWire-derived witness.

## Final source-empty recovery batch (2026-11-22)

All **31 original CrossWire-empty article records** now have independently cited content in the **noncanonical review edition**: 11 original cross-reference entries (including historical pronunciations, cross-reference labels and subsection locators) and 20 historical prose entries. The last eleven additions are `CHORBE`, `DEHORT`, `FROWARDNESS`, `HEMDAN`, `MANKIND`, `SEPHARVITES`, `SHALLUN`, `SYCHEM`, `TEPHON`, `THOCANUS`, `THOMEI`.

Each added prose passage is recorded verbatim in `workspace/reviews/print-prose-candidate-v1.json` with its individual independent **1915-attributed** transcription URL, source-entry key and stable existing XML paragraph ID. The full original corpus remains a separate preserved baseline. In total, **9,349 unaffected article records** must maintain identical text, all **185,657** original XML IDs must remain present, and two genuinely added paragraph IDs in AMNON must remain distinct.

The cross-check exposed possible secondary transcription defects which are retained **as flagged evidence rather than silently corrected**: the additional `>` in the SEPHARVITES pronunciation, the abrupt final wording of FROWARDNESS, and the capitalization at the start of the second sentence of SYCHEM. All require verification against the real page images of the 1915 five-volume edition. Complete initial reconstruction **does not mean** source-image proofreading, historical editorial acceptance, redistribution rights, or publication. The canonical `cleaned/en/ISBE.xml` intentionally remains unchanged pending that separate gate.


## Original 1915 facsimile collation — five physical volumes

The five original **Howard-Severance 1915 printed-volume PDF facsimiles** have been downloaded independently in GitHub Actions. Their source URLs, SHA-256 hashes, exact page counts and bibliographic identity are pinned in `sources/print/1915-volume-witnesses.json`. Unlike online HTML transcriptions, these are primary print witnesses, but their embedded OCR layer still requires correction against the actual page image.

The source-locked batch locator in `scripts/research_1915_print_pages.py` distinguishes both physical OCR columns and filters out ordinary lower-case prose mentions and especially the **back-of-book alphabetic index of volume V**, which otherwise generates false source claims for earlier volumes.

The complete recorded outcome is in `workspace/reviews/1915-printed-headword-ocr-locations.json`, based on the successful five-volume research run at https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45076272496 :

- **25/31** missing CrossWire headwords now have a strong **original printed-volume OCR heading page candidate**, identified by a 1-based PDF image index, not yet visually verified.
- **6/31** remain unresolved by strict heading OCR: `ASTARTE; ASTORETH`, `CHORBE`, `JOSIBIAH`, `PATRIARCHS, TESTAMENTS OF THE TWELVE`, `REGENERATION, BAPTISMAL` and `THOCANUS`. None of these is silently declared absent from the original; OCR can misread a heading, split it across columns, or conflate a short redirect with a running head.
- **0/31** has yet been certified as an exact, visually collated 1915 print-page transcription. The 31 proposed repairs still remain only in the separate noncanonical review candidate.

Next editorial gate: review the **actual printed page images** for all 31, prioritizing the six unmatched headwords, the three known suspicious web-transcription anomalies (SEPHARVITES, FROWARDNESS, SYCHEM), and Hebrew/Greek accents. Record the original printed page number and image index, collate each source block, then stage explicitly approved and reversible source-SHA-bound changes. Do not mistake successful XML schema validation or a heading OCR match for textual verification or rights clearance.

## Original printed-page visual review — first nine entries

A real visual comparison against image renders of the **original 1915 printed pages** is now recorded in `workspace/reviews/1915-visual-page-collation-v1.json`, with separate original PDF and rendered JPEG SHA-256 proofs and **both** the printed folio and the 1-based PDF image index. The evidence was reviewed from https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45077481982.

Nine source-gap entries have been visually inspected:
- Volume I: `ASTARTE; ASTORETH` (printed p. 295; PDF p. 329), `CHORBE` (p. 614; PDF p. 654).
- Volume II: `FROWARDNESS` (p. 1147; PDF p. 499).
- Volume III: `JOSIBIAH` (p. 1753; PDF p. 393).
- Volume IV: `PATRIARCHS, TESTAMENTS OF THE TWELVE` (p. 2264; PDF p. 176), `REGENERATION, BAPTISMAL` (p. 2550; PDF p. 466), `SEPHARVITES` (p. 2723; PDF p. 642).
- Volume V: `SYCHEM` (p. 2877; PDF p. 67), `THOCANUS` (p. 2973; PDF p. 169).

**Material source-fidelity findings:** The 1915 `ASTARTE` headword includes the alternate form `ASTORETH` in the printed entry, absent from our earlier redirect body. `JOSIBIAH` has a different pronunciation from the derivative transcript. The `PATRIARCHS` cross-reference names `APOCALYPTIC LITERATURE, IV, 1` without the later insertion `sec.`. `REGENERATION, BAPTISMAL` is a real short printed redirect despite previous strict OCR failure. `CHORBE`, `THOCANUS` and `SYCHEM` need their original Greek/1915 terminology and abbreviations retained rather than expanded paraphrases. The source-website's spurious `>` after the second `SEPHARVITES` pronunciation is **not printed**. Conversely the unusual ending `in "is."` in `FROWARDNESS` **is printed**: it is genuine source text, not a truncated digitization error.

Only confidently source-backed portions have been changed in the **noncanonical, still unapproved** editorial preview. Each amended record retains its earlier reading, provenance and print-page evidence. These nine page observations are **not** claims that every mark, Hebrew/Greek character, paragraph or bibliography in the full articles has been exhaustively collated. Original 1915 typography and scientific transliteration require further precision review. The other **22 records** still await visual checking. The canonical TEI remains deliberately unchanged pending source-wide validation and editorial approval.

## Closure of all six strict-OCR misses by direct print-image inspection

All **six** previously unlocated entries have now been identified in their proper original 1915 printed volumes, not inferred from the back-of-book index:

| Historical source key | Original vol. | PDF page (1-based) | Printed folio |
| --- | ---: | ---: | ---: |
| ASTARTE; ASTORETH | I | 329 | 295 |
| CHORBE | I | 654 | 614 |
| JOSIBIAH | III | 393 | 1753 |
| PATRIARCHS, TESTAMENTS OF THE TWELVE | IV | 176 | 2264 |
| REGENERATION, BAPTISMAL | IV | 466 | 2550 |
| THOCANUS | V | 169 | 2973 |

The source-located evidence is now **31/31**: 25 strict primary-print OCR matches plus six additionally checked printed-page image matches. **Do not equate this to 31/31 complete article transcription validations**: only nine individual pages have been visually checked, and none of the entire source articles or Greek/Hebrew punctuation has yet received fully certified text-level collation.

This correction supersedes the earlier six-unresolved *OCR* checkpoint without rewriting the audit history. In the historical OCR ledger, the six original strict-OCR fields remain absent, with their separate confirmed page-image locations preserved. The original CrossWire and canonical TEI remain immutable.


## Second original 1915 printed-page image review — twelve entries

Another twelve original printed facsimile pages have been visually examined in the source-locked [GitHub Actions image run](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45078377694), with JPEG digests, full original-volume SHA-256 and printed folios recorded in `workspace/reviews/1915-visual-page-collation-v1.json`. The total is now **21 of the 31** source-gap entries with page-image observations; the other **10** remain unchecked, and **zero** complete scholarly transcriptions have been editorially certified or published.

The new historical print evidence covers: `ABISSEI`, `AMNON`, `BURNT OFFERING` (volume I); `COMING OF CHRIST`, `DEHORT`, `DUALISM` (II); `ITHLAH`, `MARKET, SHEEP` (III); `PAUL, VOYAGE AND SHIPWRECK OF`, `PROSTRATION` (IV); `STANDING`, `TEPHON` (V).

Material findings retained in the **separate unapproved candidate**:
- The original `BURNT OFFERING` cross-reference reads `SACRIFICE IN THE OT AND NT`, not merely `SACRIFICE`. The printed label is preserved in the preview, with the existing broad article link clearly marked as needing an exact historical destination check.
- `PAUL, VOYAGE AND SHIPWRECK OF` points visibly to `PAUL THE APOSTLE, V, 9` (not the derivative punctuation `PAUL, THE APOSTLE`); article-level navigation remains separate from display wording.
- `DUALISM`, `PROSTRATION` and `STANDING` had extra hyphens or altered pronunciation in the web transcriptions; the print readings replace them.
- `DEHORT`, `ITHLAH`, and `TEPHON` had substantial secondary-source drift including omitted Greek/Hebrew wording, expanded AV/RV and scriptural book abbreviations, and **`Jetblah` for the correctly printed `Jethlah`**. Their candidate entries were revised, without claiming all accent marks are settled.
- `ABISSEI` has been re-checked against original print. `AMNON` retains two separate numbered senses while Hebrew characters still need rigorous verification.
- `COMING OF CHRIST` and `MARKET, SHEEP` already had the correct proposed redirect meanings, confirmed by print images.

All changes preserve prior readings and source identifiers in manifests; the immutable 1915 facsimiles, the original CrossWire ZIP/IMP and `cleaned/en/ISBE.xml` are untouched. Technical TEI P5 validity is necessary but not sufficient to approve printed-text fidelity, language variants or redistribution rights.


## All 31 source headwords inspected on original printed pages

The final nine remaining primary printed-page scans were visually inspected from [the authenticated five-volume source run](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45079034324): `ANTIQUITY` (I, p. 160), `BEERA` (I, p. 424), `HASRAH` (II, p. 1342), `HEMDAN` (II, p. 1374), `MANASSITES` (III, p. 1980), `MANKIND` (III, p. 1982), `SAVIAS` (IV, p. 2700), `SESIS` (IV, p. 2743) and `SHALLUN` (IV, p. 2747). `THOMEI` appears on the **same original volume-V image as THOCANUS**, printed folio 2973, already inspected in [the first image run](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45077481982).

**Result: 31/31 original source-gap headwords viewed on genuine 1915 printed images; 30 distinct printed pages.** Their source PDF SHA, individual rendered image SHA, volume, PDF index, printed folio, original paragraph XML ID and individual observation are now in `workspace/reviews/1915-visual-page-collation-v1.json`.

The newest textual review exposed additional historical-script and abbreviation drift, especially in `BEERA`, `HEMDAN`, `MANASSITES`, `SAVIAS`, `SESIS` and `SHALLUN`. Seven short candidate prose passages were amended with recorded prior readings. **Not every proposed Hebrew/Greek vowel mark, accent, word or paragraph boundary has yet been exhaustively proofread**. Consequently `all_text_punctuation_and_foreign_script_certified=false`, `source_recovery_approved=false`, and publication remains prohibited. The 9,380-record canonical `cleaned/en/ISBE.xml` is unchanged and reconstructible from the preserved CrossWire source.

The remaining editorial task is not locating articles anymore: it is **full character-for-character collation and formal approval** of the source-rich draft, checking the exact cross-reference destinations/section anchors, and settling legal redistribution (#1) prior to adoption.
