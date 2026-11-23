# Contrasting 1915 print with existing ISBE digital text

This is an editorial research sample, **not** a certified print transcription or publication authorization. It is separate from the recovery of the 31 originally empty records.

## AARON, printed folio 1 (1915 volume I)

The opening historical page appears at page index 2 (zero-based) in [this scanned-page excerpt](https://static1.squarespace.com/static/590be125ff7c502a07752a5b/t/63759c53c0d31f5097c0dc6e/1668652115916/Wilson%2C%2BRobert%2BDick%2C%2BBelshazzar.pdf). The same printed page was subsequently retrieved from the **SHA-pinned original 1915 volume I** as 1-based PDF page 25 (printed folio 1) and visually examined in [source-image GitHub Actions run](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45116299265). Original PDF SHA-256: f1232371fec1df1382692b2f1be8993fb1d594eda46170aaccd6337ce98a29f5; rendered page JPEG SHA-256: e87dee75f8d24da8f863d9446d7c686e37f35db0c18403afe9179b1aca0f0c4a. This is an AI-assisted image review, not independent human scholarly peer review.

- Printed wording: **Jehovah had called them**. CrossWire-derived canonical wording: **Yahweh had called them**.
- The printed bold run-in side heading is **1. Family**, while CrossWire encodes **1. Family:** as a separate underlined paragraph. Its source representation retains its characters but not all historical layout semantics.


## AALAR, the same printed folio 1

The printed **AALAR** cross-reference visibly points to **ALLAR**, while the preserved CrossWire module text reads **ALTAR** and encodes navigation to that different entry. This is a **potentially materially wrong encyclopedia link**, not merely display typography. It must be corrected only by an explicit, source-pinned and reversible editorial delta in a separate edition, after confirming the target's identity; the immutable CrossWire witness remains preserved.

Primary print evidence: [source-locked 1915 volume-I, PDF page 25](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45116299265), SHA-256 f1232371fec1df1382692b2f1be8993fb1d594eda46170aaccd6337ce98a29f5. The ledger records the exact source paragraph ID and both readings, with no approved text replacement or publication.

The versioned source-locked comparison evidence is in workspace/reviews/1915-nonempty-contrast-v1.json. The reusable read-only check in scripts/audit_print_parity.py locates exact digital anchors, stable unit IDs and Unicode content digests, rejecting drift and unauthorized changes.

**Next gate:** verify the target ALLAR as a distinct encyclopedia entry, compare other representative printed entries across volumes, and implement only reviewed, reversible editorial deltas in a separately revised TEI. Preserve the digital canonical witness. Issues #9 (content/structure) and #1 (rights) remain open.
