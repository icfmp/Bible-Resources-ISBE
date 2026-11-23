# Twelve source-backed navigation repairs in a separate 1915 editorial witness

The 1915 printed-facsimile research captured in
`workspace/reviews/1915-scripture-reference-image-triage-v1.json`
supports twelve **individual changes to the encoded Scripture navigation
targets**. One further candidate (TAANACH) stays explicitly unresolved.

The generator `scripts/apply_1915_scripture_targets.py` accepts the
separate edited TEI produced by first reconstructing the 31 lost records
and then replaying the six earlier approved 1915 source deltas. It never
writes to the original CrossWire ZIP, IMP, source-locked canonical
`cleaned/en/ISBE.xml`, or either preceding editorial witness.

Each correction requires the original article key, source paragraph XML ID,
reference XML ID, exact visible text and old encoded `cRef`, and the
observed printed page with exact PDF and rendered JPEG digests.
The algorithm changes **only** the `cRef` attribute, retaining 100% of
the original visible wording and the existing XML IDs and article order.
It checks unrelated article subtrees before and after serialization.
Any source drift, conflicting or repeated edit, altered printed witness
manifest or unresolved reference fails closed.

No silent cleanup of printed-versus-digital punctuation is attempted.
In particular the suspect `10` in the eschatology article's visible
continuation, and unusual markup segmentation of `Job 5:5`, require
separate textual review. Correcting navigation does not certify the rest
of those articles against the 1915 print.

The `validate-1915-scripture-targets.yml` workflow regenerates the
entire chain, runs negative controls, validates official pinned TEI P5,
and retains a distinctly marked **NONPUBLISHABLE** review artifact.

**Status:** AI-assisted comparison to 1915 images, not independent human
peer review; neither copyright clearance nor a publishable ISBE edition
has been achieved. Issues #9 and #1 remain open.
