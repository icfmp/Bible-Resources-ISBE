# Contrasting 1915 print with existing ISBE digital text

This is an editorial research sample, **not** a certified print transcription or publication authorization. It is separate from the recovery of the 31 originally empty records.

## AARON, printed folio 1 (1915 volume I)

The opening historical page appears at page index 2 (zero-based) in [this scanned-page excerpt](https://static1.squarespace.com/static/590be125ff7c502a07752a5b/t/63759c53c0d31f5097c0dc6e/1668652115916/Wilson%2C%2BRobert%2BDick%2C%2BBelshazzar.pdf). It visibly reproduces an original 1915 page, but the excerpt has **not been byte-matched to the pinned full-volume Wikimedia facsimile**. Do not treat an excerpt as an independently validated primary-volume scan.

- Printed wording: **Jehovah had called them**. CrossWire-derived canonical wording: **Yahweh had called them**.
- The printed bold run-in side heading is **1. Family**, while CrossWire encodes **1. Family:** as a separate underlined paragraph. Its source representation retains its characters but not all historical layout semantics.

The versioned source-locked comparison evidence is in workspace/reviews/1915-nonempty-contrast-v1.json. The reusable read-only check in scripts/audit_print_parity.py locates exact digital anchors, stable unit IDs and Unicode content digests, rejecting drift and unauthorized changes.

**Next gate:** verify the same page against the original SHA-pinned full-volume facsimile; expand a representative print-formatting sample across volumes before choosing any semantic re-encoding in a separately revised TEI. Preserve the digital canonical witness. Issues #9 (content/structure) and #1 (rights) remain open.
