# French ISBE translation conventions — provisional editorial decisions

This is a **working draft**, not a human-approved glossary. It records actual choices and review questions from the complete set of fifty source-locked French article drafts. Future batches must use consistent, source-faithful terminology without altering the original English edition.

## Non-negotiable technical contract

- `div[@type=entry]/@n` and every established `xml:id` are unchanged in French; localized names are **display text or search aliases**, never a second BRSI identity.
- Preserve `ref/@target`, `ref/@n` provenance, `ref/@cRef` canonical Bible destinations, and section/note/paragraph boundaries exactly.
- Greek/Hebrew script spans remain byte-for-byte at the text-unit level, even if embedded in untagged historical prose.
- Do not replace historic 1915 claims with modern interpretations or silently harmonize biblical/transliteration variants.

## Working French conventions

| English source text/type | French draft approach | Review note |
| --- | --- | --- |
| `See` and dictionary cross-reference labels | `Voir` and a French visible article name | Keep the source `ref/@target` and original `@n` unchanged |
| `Ark`, `Ark of Bulrushes` | `Arche`, `Arche de joncs` | Display only: canonical keys remain `ARK`, `ARK OF BULRUSHES` |
| `Methuselah`, `Zerubbabel`, `Kiriathaim` | `Mathusalem`, `Zorobabel`, `Kiriathaïm` | Review proper-name spelling against a consistent French Bible convention |
| `Revised Version`, `King James Version`, `AV` | Preserve the specific **historical** edition reference, usually in English | Never replace with a later French translation; consider an editorial abbreviation list |
| `Good Luck` in FORTUNE | `Chance` | Avoid projecting a later doctrinal sense into the 1915 article |
| `Release` | `Libération` in the displayed title; debt sense is `remise` | Polysemy requires later search aliases, not a second index entry |
| Greek, Hebrew, ancient name transliterations | Keep original source-script glyphs and scholarly transliterations | Exact display/readability and linguistic correctness require later human review |
| Historical English pronunciations (e.g. `fer'-i-bot`) | Preserve temporarily, with a per-unit reason | **Open editorial question:** explain, localize, or omit only by approved source-transparent policy |
| Scriptural references | Preserve `cRef` and original inline displayed citation initially | Any future display-label localization must be reversible and reference-neutral |

## Review priorities from the short drafts

1. Check every French theological/proper-name choice against the exact English article, not from prior Bible translation memory.
2. Review abbreviations `AV`, `RV`, `EB` and historic romanization; avoid ambiguous French expansions.
3. Preserve scholarly uncertainty (e.g. the *Methuselah* conjecture, uncertain *Dinhabah* location, tentative *Saph* lineage); do not replace it with a different assertion.
4. Review Greek/Hebrew codepoints and punctuation visually, even after automated invariance tests pass.
5. Create and test language-localized **search aliases** separately only after the common canonical index is stable. They cannot become BRSI keys.

Editorial source anomalies requiring separate printed-source review: HOLY OF HOLIES contains the damaged phrase `great @@clothed`; DEUTERO-CANONICAL, BOOKS contains `Teaching of the Apes`, `Shepher`, `He`, and a broken Jerome/Augustine clause; other source formatting/typographic anomalies appear in the pilot. Drafts mark uncertainties without silently changing historical English source text. Do not treat translator annotations as an authorized correction of the original.

All fifty draft entries are still **unreviewed**. No editorial acceptance or publication is implied.
