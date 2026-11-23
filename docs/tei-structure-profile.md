# ISBE TEI P5 structure profile

**Scope:** the faithful `workspace/witnesses/crosswire-2.2/` master of the International Standard Bible Encyclopedia and structurally aligned modern-English and translated derivatives. **Status:** adopted as the ISBE *canonical working profile*; the mechanically normalized master has passed pinned official TEI P5 4.12.0 RELAX NG and Schematron and source-fidelity checks. This does not certify historic print-edition accuracy, rights or publication readiness. This is an edition-specific application of the public TEI standard, **not a new XML dialect**, and it does not activate the deferred BRNP proposal in [Bible Resources #451](https://github.com/icfmp/Bible-Resources/issues/451).

This profile follows the source-first principles of [Bible Resources normalization policy](https://github.com/icfmp/Bible-Resources/blob/main/docs/policies/NORMALIZATION_POLICY.md), [OSIS semantic fidelity](https://github.com/icfmp/Bible-Resources/blob/main/docs/policies/OSIS_SEMANTIC_FIDELITY.md) and [editorial rules](https://github.com/icfmp/Bible-Resources/blob/main/docs/policies/EDITORIAL_RULES.md), specialized for an **encyclopedia**, not for biblical verses. See official [TEI P5 dictionary structure](https://tei-c.org/release/doc/tei-p5-doc/en/html/DI.html) and [TEI `ref`](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-ref.html).

## 1. Source and editorial authority

1. The exact CrossWire ISBE 2.2 ZIP and its `mod2imp` export are **immutable digital witnesses**. The Orr encyclopedia and its identified printed edition are the historical editorial reference; CrossWire digitization is not automatically the printed original.
2. `workspace/witnesses/crosswire-2.2/ISBE.xml` is a *faithful, separately versioned reconstruction*, not a facsimile or an English modernization. Preserve all visible characters, word order, source paragraph boundaries, meaningful emphasis, labels, original references and entry order unless an individually evidenced, reversible change is approved.
3. Distinguish **source-attested structure**, **mechanical encoding normalizations**, and **new editorial interpretation**. If the difference cannot be justified, retain the source structure and report it. Never derive a heading, list, quote, historical assertion or Scripture target from typography, punctuation, capitalization or a model's guess alone.
4. The original source key and original navigation targets remain recoverable. A current reader's rendering defect is not permission to change authorial content.

## 2. Required TEI document skeleton

The master is UTF-8 XML using only `http://www.tei-c.org/ns/1.0` for TEI elements and `xml:*` for XML language/IDs. It has exactly one `TEI / teiHeader / text / body` hierarchy. The TEI header must describe the exact work/edition, source module/version, editorial responsibility, provenance, rights status, language, revision and reference schemes. Do not put an unsupported claim of publication approval into the header.

An encyclopedia **article** is a text division, not a Bible verse and not necessarily a formal lexical `<entry>`. This profile retains the existing `<div type="entry">` convention for long prose articles. A fully TEI-structured dictionary `<entry>` would be a different profile and must not be mixed into this edition without review.

```xml
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:lang="en">
  <teiHeader>
    <fileDesc>
      <titleStmt><title>International Standard Bible Encyclopedia</title></titleStmt>
      <publicationStmt><p>Editorial working edition; not released.</p></publicationStmt>
      <sourceDesc><p>CrossWire ISBE 2.2 digital witness; historical work edited by James Orr.</p></sourceDesc>
    </fileDesc>
    <!-- Exact edition, rights, revision and reference-declaration details
         must be source-pinned before claiming header completeness. -->
  </teiHeader>
  <text>
    <body>
      <div type="entry" xml:id="isbe-STABLE-ID" n="ORIGINAL SWORD KEY">
        <head type="index" xml:id="isbe-STABLE-ID-head">ORIGINAL SWORD KEY</head>
        <p xml:id="isbe-STABLE-ID-n000002">Source-attested prose.</p>
      </div>
    </body>
  </text>
</TEI>
```

The source-key-derived first `head` is explicitly an **index label generated from the SWORD key**, not a claim that the printed edition contained the same authored heading at that point. Do not duplicate a real heading or translate the key stored in `div/@n`.

## 3. Allowed structural meanings

| Meaning | TEI P5 target | Rule |
| --- | --- | --- |
| One encyclopedia record | `div[@type="entry"]` | Exactly one per original source key, stable order and ID |
| Synthetic article label | leading `head[@type="index"]` | From that entry's original SWORD key, distinguish from authorial headings |
| Authored subdivision | `div[@type="section"] / head / p` | Only when section boundaries and scope are attested; preserve paragraphs and text |
| Original prose paragraph | `p` | Retain exact boundaries unless an approved source-backed change exists |
| Genuine authored heading | `head` | Do not infer it from `hi`, all caps or a navigation item alone |
| Bibliography | `div[@type="bibliography"]`, `head`, `bibl`/`listBibl` as supported | Separate bibliographic matter only when structure is identifiable; never fabricate citations |
| True list | `list` with `item` | Use only if the source supports list semantics and item boundaries |
| Block / inline quotation | `quote` / `q` | Preserve actual quotation boundaries and attribution; do not infer from mere quote marks |
| Poetic lines / stanzas | `lg` / `l` | Use only on independently attested lineation |
| Table | `table` / `row` / `cell` | Only actual tabular relationships, preserving row/column meaning |
| Original note | `note` with stable ID and attachment | Preserve content, authorial note position, caller and scope; no generated notes |
| Line break | `lb` | Keep attested meaningful breaks, not as a replacement for paragraph markup |
| Authored emphasis | `hi[@rend]` | Preserve bold/italic/underline distinctions; do not convert emphasis to a heading mechanically |
| Original-language phrase | `foreign[@xml:lang]` | Only with reliably identified language; do not invent linguistic classification |

**Unknown elements or attributes:** inventory, consult the official TEI specification and halt normalization until a documented mapping and positive/negative tests exist. A valid TEI element need not be permissible in this particular context.

## 4. References are typed by what they point to

- **Article/section link:** `<ref type="article" target="#isbe-…">…</ref>` (or `type="section"` for an internal subsection). All fragment targets must exist. Keep the original CrossWire destination in `@n="ISBE:…"` even when repaired; retain the visible label unchanged. No speculative mapping.
- **Biblical passage:** `<ref type="scripture" cRef="Bible:Gen.1.1">Ge 1:1</ref>`. Transfer the **entire, exact** CrossWire `osisRef` value to TEI `@cRef`, not a paraphrased or renumbered reference. Declare/document the `Bible:` canonical-reference scheme in `teiHeader/encodingDesc/refsDecl` before converting. Do **not** give one TEI `ref` both `@target` and `@cRef`; TEI explicitly forbids that combination. No fabricated external URL or inference of a complete reference from a source abbreviation.
- **Unresolvable original link:** `<seg type="unlinked-source-reference" n="ISBE:ORIGINAL">original visible words</seg>`. This is **not clickable**, but its original key, inline position, content and `xml:id` are retained and the discrepancy is reported.
- **Bibliography label incorrectly linked by the digital witness:** represent the label with appropriate heading/markup and its source `n`, not an invented destination. Keep the original textual content; record this separately from a repaired cross-reference.
- **External URL or other citations:** only real source-attested URIs with justified TEI `ref` semantics; no invented websites or navigation targets.

The faithful **source intermediate** contains 93,162 CrossWire `osisRef` attributes. The canonical TEI P5 master transfers every exact value to `cRef` with a verified, source-hash-bound, reversible `osisRef` → `cRef` map. The original CrossWire witness and reconstructed legacy intermediate remain preserved separately. No Scripture target is expanded or rewritten.

## 5. Identifiers, ordering and translations

- Every source article keeps its existing `xml:id="isbe-…"`, computed from the exact original key, and `@n` contains that key unmodified. Retain existing IDs for *all* pre-existing content elements and cross-reference targets.
- Original node IDs are positional identifiers **at initial extraction**; never regenerate existing IDs merely because a modernized article adds, deletes, splits or reorders nodes. Allocate genuinely new IDs with collision checks and record explicit old/new unit mappings for reviewed splits and merges.
- The English modernized edition and translations preserve article IDs and, where units correspond, the original structural IDs. New text may change, but not the established source identity or reference semantics.
- `xml:lang` declares the edition's language, with nested overrides only where source-attested. Right-to-left original-language material must retain its direction and script behavior.
- Don't encode an article's multiple headwords as multiple invented dictionary records. Explicit original alternatives stay in the original indexed key; a search index can map these to the same article ID.

## 6. Acceptance and audit gates

**Two different gates are mandatory and must not be confused.**

**A. Source-fidelity and project-profile gate:** identical article/key coverage and order; per-article character, whitespace and punctuation integrity for a faithful cleanup; enumerated paragraph/head/list/quote/note/line-break boundaries; structure and attribute inventories; stable IDs; complete reference accounting; justified reversible changes; approved exceptional mappings; no dangling active internal links. Any altered element/attribute must appear in a source-pinned change ledger. Source text checksums alone are not sufficient.

**B. Official format gate:** the serialized candidate must validate against an explicitly **version- and SHA-256-pinned official TEI P5 schema** (RELAX NG and associated Schematron checks), plus the ISBE-specific restrictions above. Do not claim P5 validity from XML well-formedness or our custom audit. Check the selected schema against known positive/negative examples and record validation tool/version and report. Until that gate exists and passes, the master is a *working TEI reconstruction*, **not a certified P5 edition**.

Separate, later proof gates cover historic print-source review, CrossWire-derived SWORD round-trip, reader rendering, legal rights and publication authorization. They cannot be inferred from a successful XML validation.

## 7. Validated canonical corpus and outstanding editorial work

The original reconstructed source contained 9,380 article divisions, 66,450 source paragraphs, 93,162 legacy scripture attributes, 5,906 active internal links, 144 intentionally inert references and 31 empty source-derived paragraphs. The source inventory is preserved in git history and locked by SHA-256.

The canonical TEI P5 4.12.0 working master is rebuilt by a source-first pipeline, which retains the complete text and original 185,657 `xml:id` values, transfers all Scripture references to `@cRef`, types index headings and references, and creates 29 source-justified bibliography sections (27 authored heads plus 2 bibliography-lead paragraphs). The two TEI-invalid `p/@type` attributes were moved to the containing bibliography divisions without removing or rewriting their paragraphs.

Full-serialization article parity and the official, byte-pinned TEI P5 4.12.0 RELAX NG and ISO Schematron both passed, including negative controls. Source SHA-256: `98b07b64019601a8ad1eb13feff5b336c870fd80adfecd670bd9b7e3be7b8575`; canonical candidate SHA-256: `a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25`. See `docs/tei-p5-candidate-migration.md` for the exact schema digests, validation commands and evidence.

**Editorial work still required:** independently assess the 31 source-derived empty paragraphs and potential lists, quotations, notes and poetry against a reliably identified historical print witness. Never derive these semantic structures solely from formatting or TEI schema acceptance. Historical edition verification, legal rights and redistributability, reader compatibility, and modern-English translation remain distinct from successful P5 normalization.
