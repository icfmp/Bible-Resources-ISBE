# ISBE TEI P5 candidate migration — version 1

**State: full-corpus candidate with automated official TEI validation; not promoted
to the canonical master.** The canonical faithful reconstruction and the
preserved CrossWire input are unchanged. The migration does not certify
historical print fidelity, distribution rights or translation readiness.

## Reproducible inputs and source lock

- Preserved original SWORD ZIP: sources/crosswire/isbe-2.2/ISBE.zip.
- Preserved IMP export: workspace/exports/isbe-2.2.imp.
- Faithful unmodified reconstruction: cleaned/en/ISBE.xml.
- Version-1 source lock and official schema digests:
  workspace/changes/tei-p5-candidate-v1.json.
- Input reconstruction SHA-256:
  98b07b64019601a8ad1eb13feff5b336c870fd80adfecd670bd9b7e3be7b8575.
- Generated, unpromoted candidate: workspace/candidates/en/ISBE.xml.
- Reports: tei-p5-candidate-report.json and tei-p5-official-validation.json
  beside the generated candidate, saved as a GitHub Actions artifact.

The preferred source-first build reconstructs the faithful legacy witness from
the preserved IMP in an **ignored temporary directory** and checks its source
SHA-256 before normalizing. This works even if the canonical master is later
promoted to TEI P5 and is no longer a legacy normalization input.

    mkdir -p workspace/tmp/isbe-legacy workspace/candidates/en
    python3 scripts/rebuild_tei.py \
      --input workspace/exports/isbe-2.2.imp \
      --accepted-aliases workspace/reviews/accepted-title-aliases.json \
      --output workspace/tmp/isbe-legacy/ISBE.xml \
      --index workspace/tmp/isbe-legacy/article-index.json \
      --report workspace/tmp/isbe-legacy/tei-reconstruction.json
    python3 scripts/normalize_tei_p5.py \
      --input workspace/tmp/isbe-legacy/ISBE.xml \
      --index workspace/tmp/isbe-legacy/article-index.json \
      --manifest workspace/changes/tei-p5-candidate-v1.json \
      --output workspace/candidates/en/ISBE.xml \
      --report workspace/candidates/en/tei-p5-candidate-report.json

The workflow also independently verifies that the temporary legacy witness
matches the pinned SHA-256 and that the resulting candidate bytes have the
previously validated SHA-256
a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25.

Run the official format gates using the pinned, reviewed
.github/workflows/tei-p5-candidate.yml GitHub Actions workflow. The schema
downloads must match the exact SHA-256 in the version-1 lock, or CI fails.

## Official schema provenance and validator tooling

**TEI P5 release 4.12.0**, using the official TEI Vault (not latest aliases):

- RELAX NG tei_all.rng:
  https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/custom/schema/relaxng/tei_all.rng
  SHA-256 b0f115095ead2ccc6933aa3365c6f4a82cba3b2ec7eee7f76bb616d7a63b7e48.
- ISO Schematron tei_all.isosch:
  https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/Exemplars/tei_all.isosch
  SHA-256 500f231ac32d12827bdbdd4168e88743848656bc46cc83286d39bd1f396113d5.
  The file contains 120 TEI rules/patterns.
- Schematron ISO compilation resources pinned to commit
  77dcd36c53d12ed786c144ece3b2af7694abdc56 of
  https://github.com/Schematron/schematron; source list is in the lock.
- Validation engines: jing for RELAX NG and Saxon HE XSLT2 for compiled
  Schematron/SVRL. The workflow logs installed Debian package versions.
- Negative controls: invalid p/@type for RELAX NG, and a ref with both
  @target and @cRef for Schematron. Invalid controls **must be rejected**
  or CI fails.
- scripts/check_tei_p5_svrl.py checks official schema byte-level digests,
  source parity report, SVRL execution and the failing negative control,
  and produces a separate machine-readable official verification report.

## Authorized changes and reversibility

1. Add document xml:lang="en", teiHeader/encodingDesc/refsDecl with
   **source reference provenance** (not an invented external Bible resolver),
   and revisionDesc. Keep the original fileDesc byte-equivalent in XML terms.
2. Transfer all 93,162 original Scripture ref/@osisRef values unchanged into
   @cRef, assign type=scripture, preserve every reference ID and visible word.
3. Assign type=article or type=section to 5,906 existing verified internal
   links based on their actual destination; keep @target and the CrossWire
   original @n unchanged.
4. Mark 9,380 generated headwords type=index only after verifying their keys.
5. Wrap 27 existing bibliography heads plus 2 source-marked bibliography
   lead paragraphs (29 in total) in div type=bibliography. TEI P5 disallows
   type on p, so only the two p type=bibliography-lead attributes are removed
   as their source classification is transferred to the containing div.
   Original paragraph/head nodes, visible text, tails, child order and XML
   identifiers are preserved. No invented list, bibl, head or quotation.
6. Preserve all 144 intentionally inert original source links exactly, along
   with their original @n and source-identifying XML IDs.

The full **serialized** candidate is checked against all 9,380 original
articles, article-index hashes, 185,657 existing IDs, source fileDesc,
individual original node attributes and text/tail, original order, paragraph
nesting except the 29 documented wrappers, Scripture values and internal
targets. Every unapproved change causes an error.

To roll back, delete the separate candidate and use the unchanged cleaned
master. No reverse patching of the source is necessary.

## Approval boundaries

- A successful source-fidelity report does not itself mean official TEI
  validation passed. Both machine-readable reports must be reviewed.
- An automated official format PASS is a technical result; it does not prove
  agreement with the historic print edition or independent authorization to
  distribute and translate the digital source.
- Do not move the candidate to cleaned/en/ISBE.xml until complete acceptance
  checks, human review and an explicit editorial decision. Do not begin the
  modern-English edition based merely on a successful extraction.
- Unresolved source-derived empty paragraphs, unverified historical structure
  (lists, quotations, notes, poetry) and source rights remain independent
  review tasks; this mechanical conversion does not silently edit them.
