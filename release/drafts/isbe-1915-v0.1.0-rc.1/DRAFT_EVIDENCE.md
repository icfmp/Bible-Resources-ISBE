# Release draft evidence — ISBE 1915 v0.1.0-rc.1

**GitHub state: DRAFT ONLY, unpublished. This file is not a publication authorization.**

- Draft tag descriptor: `isbe-1915-v0.1.0-rc.1`
- GitHub release draft ID: `455869112` (GitHub's internal draft tag path: `untagged-6333d5e100eb6157f83a`)
- Draft URL (requires collaborator access): https://github.com/icfmp/Bible-Resources-ISBE/releases/tag/untagged-6333d5e100eb6157f83a
- Historical source target commit: `0853bc904acc24de50fb49ab75a32a5b2bb3c339`
- Created and explicitly **verified unpublished** by [GitHub Actions draft-only run #45246202666](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45246202666)
- `draft: true`, `prerelease: true`, `published_at: null` checked using the authenticated GitHub releases API.
- Release assets (private while draft):
  - `ISBE-1915-corrected-historical-source-v0.1.0-rc.1.zip` — 10,779,993 bytes; SHA-256 `431bc45a7d2583887939bc162c20b630afdd09790ba14600a19210ceccb9bcc5`.
  - `ISBE-1915-v0.1.0-rc.1-SHA256SUMS.txt` — 338 bytes, references the archive and the exact uncompressed original/cleaned source fingerprints.
- Additional **unpublished draft assets added after native SWORD compilation**, verified by [archive workflow #45262814840](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45262814840):
  - `BRISBE1915-native-candidate-NOT-FOR-PUBLICATION.tar.gz` — 11,728,811 bytes; SHA-256 `6993937ffcdba83348dc0f0cc510613a42f85d3e4c5423f19355a1cf65ee9c9b`. Contains a **real corrected** SWORD ZIP-compressed zLD module: `mods.d/brisbe1915.conf` and `modules/lexdict/zld/brisbe1915/dict.{zdt,zdx,idx,dat}`.
  - `BRISBE1915-NATIVE-SHA256SUMS.txt` — source-pinned binary checksum.
  - `sword-native-roundtrip.json` — complete native `mod2imp` readback summary, 9,380 entries and zero missing, extra, text or XML errors.
- The previous time-limited public Actions binary artifact was deleted **after** its SHA-verified private draft copy existed.
- Inside the ZIP: full historical English `ISBE.xml` (37,062,851 uncompressed bytes, SHA-256 `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`), `CLEANUP_MANIFEST.json`, `CROSSWIRE_PROVENANCE.json` and source/rights README files.

The **TEI ZIP** is source only; separately, the **same unpublished draft now contains a real compiled SWORD binary candidate**. The draft is not a public SWORD distribution or the future modernized English edition. In particular it is not guaranteed to reproduce all original 1915 Greek/Hebrew spellings.

## Immutable safeguards

The draft Action checked out the exact previously validated source commit, verified the real original and cleaned file bytes, executed the full source-reconstruction pipeline, validated against official TEI P5, compared the rebuilt files to tracked masters, and built a deterministic ZIP before attaching draft assets. The release command **always used `--draft` and `--prerelease`**. It read back `isDraft=true` and `isPrerelease=true` after creation.

The one-shot Actions workflows for the initial source draft and later native binary staging were removed after success. Their exact source SHA checks and runs remain referenced here; the permanent source-integrity workflow `.github/workflows/validate-retained-isbe-sources.yml` remains in `main`.

## Publication restrictions

**Maintainer decision (2026-11-24):** The owner accepts the historical 1915 edition and CrossWire's declared `Public Domain` license as the project's distribution basis. An independent additional France/EU contributor or digitization-layer audit is **not required** and is no longer a publication blocker. This is a maintainer policy decision, not a claim that a jurisdiction-by-jurisdiction legal review was completed; see [provenance issue #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1).

**The draft remains unpublished** because final reader/editorial acceptance and explicit approval of the actual release are still pending ([#79](https://github.com/icfmp/Bible-Resources-ISBE/issues/79), [#9](https://github.com/icfmp/Bible-Resources-ISBE/issues/9)). No automated workflow may publish this draft unilaterally.

Release content and version metadata are documented in `RELEASE_NOTES.md` and `PUBLICATION_GATES.md`.
