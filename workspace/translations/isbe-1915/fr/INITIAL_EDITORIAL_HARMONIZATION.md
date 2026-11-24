# Initial editorial harmonization — 2026-11-24

The original corrected English ISBE source is **byte unchanged**.
This ledger documents deliberate, reversible changes to the existing **French
draft patches**, not approval of the complete translated articles.

## Translation changes (not source corrections)

| Source key | Source node(s) | French adjustment | Reason |
| --- | --- | --- | --- |
| `ARK` | linked visible label, node 3 | `ARCHE DE JONCS` → `CORBEILLE DE JONCS` | Distinguish Moses' floating basket from Noah's ark in natural French; original link destination and key unchanged |
| `ARK OF BULRUSHES` | heading node 1; prose node 5 tail, 6 tail, 8 text | Localize as `corbeille de joncs`, with correct `la` / `de la` articles | Harmonize the title, definition and references across the same article |
| `HOLY OF HOLIES` | node 9 tail, 10 text/tail | Render the split `MERCY-` + linked `SEAT` as **« propitiatoire »** | The original source splits an English lexical label at a TEI reference boundary; French should display a single coherent term without changing that reference or the English original |
| `LAUGHTER` | nodes 32 text, 33–35 tails | Keep historical KJV/RV English lexical comparisons, but explain `laugh`, `mock`, `laughing-stock`, `laugheth at the time to come` in French alongside them | English-version word studies must be intelligible to French readers without falsifying the original version distinctions |

The **12 suspected source-text anomalies** in
`workspace/pilots/isbe-1915-fr/SOURCE_REVIEW_FLAGS.json` remain
**unverified and unresolved**; none was silently repaired.
In particular the damaged `@@clothed` sequence remains *flagged* in the
working French text of `HOLY OF HOLIES`: it must be resolved against a
proper source witness before editorial sign-off.

## What is — and is not — validated

- 50/50 existing pilot source-locked draft articles remain complete.
- Generic reading-copy rendering is now extended to nested TEI divisions and
  lists as encountered in real historical articles.
- Each of the 50 is exported as a readable *complete draft* in CI (alongside
  ABRAHAM), with source identity and original reference invariants enforced.
- The technical worklist for source positions 1–4,000 is checked against
  the corrected historical English source.
- **None** of these facts implies that all fifty articles have received a
  full independent English–French editorial collation. No article checkbox
  is marked complete by this step.

## Next editorial work

Read each reconstructed bilingual article from beginning to end and check
meaning, fluency, theology, proper names, historical variant wordings,
bibliography and Scripture locators, before checking its single GitHub task.
Prioritize the six articles with exact source-witness anomaly flags, but do
not erase or replace the historical English witness.
