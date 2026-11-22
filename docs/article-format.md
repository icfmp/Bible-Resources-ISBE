# Article interchange format (working specification)

Canonical source: one UTF-8 JSON article per path `<article-id>.json` in each language directory. The example below **is illustrative only, not actual ISBE content**:

```json
{
  "id": "example-article",
  "language": "en",
  "title": "Example title",
  "segments": [
    { "id": "p001", "type": "paragraph", "text": "Example content." }
  ]
}
```

Stable `id` refers to the ISBE article regardless of language or displayed title. Stable `segments[].id` refers to the same editorial unit across revisions and translations. Source formatting / annotations may require additional typed fields decided after inspection of the actual source; **do not flatten or discard** footnotes, references, poetry, headings or markup to conform to this example.

Translated segments also include `source_hash`, computed as SHA-256 over UTF-8 bytes of the modern-English segment's `text` field. A mismatch signals translation staleness. If a segment is substantially split or merged, retain a mapping in an editorial decision record rather than recycling identifiers.

Avoid identifiers based solely on translated names; do not assume all dictionary headings represent independent articles. Determine alias and cross-reference behavior from the actual corpus before ingestion.
