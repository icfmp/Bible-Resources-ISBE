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
- Inside the ZIP: full historical English `ISBE.xml` (37,062,851 uncompressed bytes, SHA-256 `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`), `CLEANUP_MANIFEST.json`, `CROSSWIRE_PROVENANCE.json` and source/rights README files.

The ZIP is a **TEI source candidate only**, neither a new compiled SWORD module nor the future modernized English edition. In particular it is not guaranteed to reproduce all original 1915 Greek/Hebrew spellings.

## Immutable safeguards

The draft Action checked out the exact previously validated source commit, verified the real original and cleaned file bytes, executed the full source-reconstruction pipeline, validated against official TEI P5, compared the rebuilt files to tracked masters, and built a deterministic ZIP before attaching draft assets. The release command **always used `--draft` and `--prerelease`**. It read back `isDraft=true` and `isPrerelease=true` after creation.

The one-shot GitHub Actions creation workflow was removed after successful staging, to follow the project's no-retained-one-off-tools policy; the permanent source-integrity workflow `.github/workflows/validate-retained-isbe-sources.yml` remains in `main`.

## Publication restrictions

[Rights #1](https://github.com/icfmp/Bible-Resources-ISBE/issues/1) and the original multi-author EU/France/CrossWire digitization-layer rights review are unresolved. **Do not click Publish release or use `gh release edit --draft=false` until the source-specific legal rights have been cleared and approved.** No other automated job is permitted to publish this asset. The source file is already retained in a **public repository**, which is independently relevant to the same rights analysis and does not resolve the outstanding legal question.

Release content and version metadata are documented in `RELEASE_NOTES.md` and `PUBLICATION_GATES.md`.
