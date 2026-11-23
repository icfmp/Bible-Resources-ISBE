# Original 1915 eschatology continuation: source-backed visible and target repair

This is a **separate, nonpublishable editorial candidate** built after the
previously approved 31 restored entries, six historical print corrections,
and twelve Scripture **navigation-only** repairs. It does not alter any
CrossWire ZIP or IMP, the source-locked canonical
`workspace/witnesses/crosswire-2.2/ISBE.xml`, or those preceding generated editions.

## Precise original-print discrepancy

Article: **ESCHATOLOGY OF THE OLD TESTAMENT**, original digital article ID
`isbe-597435f14b3ed29a6a72`, source paragraph ID ending `n000230`.

The SHA-256-pinned original **1915 volume II** printed folio **977**
(PDF page **325**) visibly cites **Zeph 3 13.20** among the remnant
proof texts. Source PDF SHA-256:
`e8ad1d382b79ee40701983ffee89201193585a0e4542fb0c52b99cbff6ad2cb1`.
Rendered JPEG SHA-256:
`03cda84a940065be6b77b62e9d2c88b5e8ce93bcb7ecc28b9fc78a8567434150`.
[Exact original page-image evidence](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45121869473),
job `137517240676`. Examination was AI-assisted, not independent human
editorial peer review.

The earlier, separate metadata-only correction already fixed the
first digital ref `Ze 3:13` from `Bible:Zech.4.3` to
`Bible:Zeph.3.13`, retaining its visible text.

Independent inspection of the actual **generated previous editorial
witness** (PR #52, [CI run 45122965787](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45122965787))
then revealed the next **separate** child reference, not plain prose:

- First child: XML ID ending `n000236`, text `Ze 3:13`,
  `cRef="Bible:Zeph.3.13"`, tail `,`.
- Immediately following child: XML ID ending `n000237`, text
  `10`, `cRef="Bible:Zech.3.10"`.

Thus the existing displayed sequence `Ze 3:13,10` is inconsistent
with both the **1915 printed reference** and the encoded navigation.
The new, individually approved operation restores **`20`** and the
associated target **`Bible:Zeph.3.20`** in the second reference only.
It deliberately retains the already-digitized separation and comma:
this is an explicit digital-reference formatting decision and **not**
a claim that the printed typography uses those exact punctuation
characters.

## Source lock and reproducible checks

The exact decision, source paragraph text SHA-256, first and second
reference IDs, their old text and metadata, original printed-page digest,
rendered JPEG digest, image run/job IDs, and rationale live in
`workspace/reviews/1915-approved-reference-text-deltas-v1.json`.

The generic `scripts/apply_1915_reference_text_deltas.py` rejects
unexpected source identity, wrong predecessor or separator, a mutated
original paragraph digest, duplicate approvals, mismatching print
evidence, or any changed unrelated article. It confirms all original
article identities and XML IDs remain in order. Each operation is
individually reversible from its recorded before-values.

Run `.github/workflows/validate-1915-textual-reference-deltas.yml`
to reconstruct all four editorial stages in isolation and validate the
final, **NONPUBLISHABLE** TEI with the official pinned TEI P5 RELAX NG
and Schematron checks. Nothing is copied into the canonical master.

This is **not** an article-wide, let alone a 9,380-entry, historical
print certification. Neither human scholarly approval nor downstream
redistribution rights (#1) is implied. Full 1915 article collation,
including TAANACH's missing scanned folios, remains open (#9).
