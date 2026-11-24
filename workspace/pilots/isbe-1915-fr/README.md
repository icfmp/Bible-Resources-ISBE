# French ISBE 1915 — source-locked translation pilot (not for publication)

This working pilot comes **directly** from the corrected 1915 historical English TEI P5 edition, not from the original CrossWire reconstruction or a hypothetical modern-English edition.

## Identity rule

- Same **9,380 original canonical article IDs and SWORD source keys** throughout the eventual complete French edition.
- The **50** pilot articles listed in `roster.json` reproduce those original pairs in their exact source order. They are an evaluation *subset*, **not** a new index.
- Any French titles, links' visible labels or later localized search aliases must resolve to the existing canonical entry ID and original key.
- Preserve source `xml:id` values for internal nodes and canonical targets, `cRef` Bible destinations, original Greek/Hebrew scripts, section divisions, bibliographic data and provenance.

## Current scope

`roster.json` records the 50 exact source IDs selected deterministically from the SHA-256-locked historical English master. The subset includes attested difficult examples such as Greek and Hebrew, nested sections, source-authorized dictionary hyperlinks, Bible references, ordinary prose, short cross-reference articles and longer thematic articles. A selection does **not** imply any translation is complete.

`draft-patches.json` begins with **fifty actual source-based French drafts**, with exact original text nodes, original article hashes and source node ordinals. They have **not been independently proofread**. Historical English phonetic transcriptions are temporarily retained with explicit reasons; this is an editorial question for review, not a settled localization decision.

The generator never touches the English source. It emits a **temporary multilingual (EN+FR) working excerpt**, not a complete French edition. All 50 selected source articles now have complete sets of draft translation/preserve actions. **No human editorial review has been certified**, and the multilingual 50-article excerpt is not a complete 9,380-article French edition. No release, catalogue entry or module publication is authorized.

## Reproduction

From the repository root:

```sh
python3 -m scripts.select_translation_pilot \
  --source sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml \
  --output /tmp/isbe-fr-pilot-selection.json

python3 -m scripts.apply_translation_pilot \
  --source sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml \
  --roster workspace/pilots/isbe-1915-fr/roster.json \
  --patches workspace/pilots/isbe-1915-fr/draft-patches.json \
  --output /tmp/isbe-fr-partial-draft.xml \
  --report /tmp/isbe-fr-partial-draft-report.json

python3 -m unittest tests.test_translation_pilot_selection tests.test_translation_pilot_apply -v
```

The complete French TEI is **not yet created** at `sources/cleaned/encyclopedias/fr/isbe-1915/ISBE.xml`. The full-corpus identity validator `scripts/validate_translation_identity.py` remains the separate gate once **all 9,380** entries exist in genuine French. Editorial collation, official TEI validation, complete native SWORD readback, multi-reader smoke and maintainer publication authorization remain outstanding.

See [tracking issue #103](https://github.com/icfmp/Bible-Resources-ISBE/issues/103). BRSI maps external encyclopedia concepts to the original canonical ISBE article IDs **once**, not per translation.
