# Grouped ISBE translation transport

JSONL is a transport layer, not a new resource format. The original TEI,
source maps and existing compiler remain authoritative.

Each staged queue retains its Markdown templates and manifest, with an
additional SOURCE.jsonl. Each line contains canonical identity, fingerprints,
and complete ordered blocks. Within each block, a triple [node, part, English
text] is an editable slot; a string is an immutable anchor. Read all blocks
for context. Source export checks byte-for-byte reconstruction.

Return one line per article with article_id, targets (ordered translated
strings) and preserve (explicit unchanged-text reasons keyed by node:part).
Do not repeat English or manually reproduce markup.

Compile with:
```sh
python3 -m scripts.isbe_translation_jsonl compile --archive corpus.zip --source SOURCE.jsonl --translations targets.jsonl --output empty-output
```

The existing batch JSON, Markdown drafts and reports are generated only after
every submitted article compiles. Groups may be partial; never label a
partial cohort complete. Source records can be reused across languages;
the current compiler emits French drafts.

Accumulate groups in a provisional Git tree and commit the complete cohort
and checkpoint once, verifying the starting branch head. Keep independent
editorial review separate, leave unreviewed checkboxes unchecked, and do
not open a translation PR before 9,380 first drafts exist.
