# Recovery of 31 historically printed entries (1915)

## Editorial status

The CrossWire ISBE 2.2 source left 31 indexed articles with an empty body. The 1915 Orr/Howard-Severance facsimiles contain 20 substantive texts and 11 redirects at those locations.

The source-locked `workspace/witnesses/crosswire-2.2/ISBE.xml` is **never overwritten**. A separately generated editorial TEI witness restores the 31 readings and preserves the other 9,349 articles and their original XML identifiers. The original CrossWire ZIP and IMP remain intact.

The complete approved body readings are locked in `workspace/reviews/1915-second-pass-visual-approval-v1.json`, one record per entry. Each record identifies the canonical source paragraph, original printed volume/folio/PDF page, original PDF SHA-256, rendered source-image SHA-256, and the exact text visually rechecked against the printed page. The first-pass and pre-correction transcriptions remain in Git for comparison and reversal.

This is a **second AI-assisted visual collation** (2026-11-23) based on the recovered source images in the original GitHub Actions logs. It is an explicit editorial decision for the separate TEI witness, **not a claim of independent human scholarly peer review**. Optical character recognition concordance is not used as a certification threshold.

## Rebuild and validation

From the repository root:

```sh
python -m unittest discover -s tests -p 'test_1915_second_pass_approval.py'
python scripts/finalize_1915_recovery.py \
  --output workspace/tmp/ISBE-1915-editorial.xml \
  --report workspace/tmp/ISBE-1915-editorial-report.json \
  --validator-manifest workspace/tmp/1915-editorial-validator-manifest.json \
  --fidelity-report workspace/tmp/1915-editorial-fidelity.json
python scripts/validate_official_tei_p5.py \
  --candidate workspace/tmp/ISBE-1915-editorial.xml \
  --source-report workspace/tmp/1915-editorial-fidelity.json \
  --manifest workspace/tmp/1915-editorial-validator-manifest.json \
  --output workspace/tmp/1915-editorial-official-validation.json
```

The official P5 validator requires the documented system dependencies (including `jing`) and access to the pinned original schemas. The GitHub Actions workflow `validate-1915-editorial-edition.yml` executes these gates and stores the resulting corrected TEI as a **nonpublishable review artifact**. A missing approval, modified original page digest, candidate-text divergence, changed canonical SHA, failed schema validation, or original-ID loss blocks success.

## Rights and publication boundary

This print-text approval is **not** an authorization to redistribute the historical text or compile a public SWORD module. Issue #1 retains the separate rights decision. Native SWORD packaging, reader testing, and publication require a further release decision. Neither a working XML artifact nor passing schemas alone authorizes publication.

The original baseline can always be restored from its immutable Git/ZIP/IMP provenance. The historical candidates and both review ledgers are retained as the reversible editorial change record.
