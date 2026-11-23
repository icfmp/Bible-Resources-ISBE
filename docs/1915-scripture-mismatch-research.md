# Five-volume 1915 print research — Scripture metadata inconsistencies

PR #49 established 13 candidate inconsistencies, affecting 12 distinct
article headwords (PORCUPINE has two reference occurrences). The canonical
source remains SHA-locked and immutable. PR #49 scanned 93,162 references with
cRef, comparing 50,821 unambiguous chapter/verse labels; 42,341 complex or
implicit expressions were not assessed.

This follow-up research queue records each original TEI reference identifier,
exact displayed and encoded reference, full-article text digest, reproducible
neighboring digital context, and its expected original 1915 print volume.

The optional five-volume research job downloads **exact SHA-256-pinned**
1915 PDFs, verifies page counts, extracts OCR headword candidates, and
collects possible page locations for **later image collation**. OCR, even from
a byte-verified historical scan, cannot certify an article's typography or
contents and must **never** authorize an editorial correction.

Use the artifacts of
`.github/workflows/research-1915-scripture-mismatches.yml` to find the
original page images, then inspect each and record the PDF/page/image digest,
exact printed text, the decision (retain / correct / ambiguous), and any
separate approved editoral delta. Do not conflate an erroneous `cRef`
with erroneous printed text. An apparent mismatch can also arise from an
ambiguous book abbreviation, truncation, segmentation, or a scanner false
positive. Keep the rights and human-review gates of #1 open.

This complements #9, not a claim that all 9,380 articles are print-collated.
