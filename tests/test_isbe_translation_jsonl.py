"""Roundtrip and negative controls for grouped translation transport."""
import tempfile
import unittest
from pathlib import Path
from scripts.export_tei_markdown_corpus import export
from scripts.translation_markdown_layout import template
from scripts.isbe_translation_jsonl import source_record, slots, render, compile_group
from scripts.validate_translation_identity import sha256
from tests.test_export_tei_markdown_corpus import specimen


class CompactTransportTests(unittest.TestCase):
    def test_roundtrip_and_group_guards(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.xml"
            specimen(source)
            sha = sha256(source)
            archive = root / "corpus.zip"
            export(source, archive, report=root / "report.json", expected_sha=sha, expected_count=2)
            record = source_record(archive, "A", expected_sha=sha)
            values = [p[2] for p in slots(record)]
            self.assertEqual(render(record, values), template(archive, "A", expected_sha=sha))
            replacements = {"A": "Un titre", "In the ": "Dans le ", " and in ": " et en ",
                            " is written.": " est écrit.", "Original editor's note.": "Note de l'éditeur."}
            targets = [replacements.get(v, v) for v in values]
            target = {"article_id": record["article_id"], "targets": targets}
            batch, manuscripts, reports = compile_group(archive, [record], [target], expected_sha=sha)
            self.assertEqual(len(batch["articles"]), 1)
            self.assertEqual(len(manuscripts), 1)
            self.assertEqual(reports[0]["source_mutable_text_units"], 5)
            self.assertFalse(batch["publication_permitted"])
            with self.assertRaises(ValueError):
                render(record, targets[:-1])
            with self.assertRaises(ValueError):
                render(record, ["⟦ISBE:KEEP:99:x⟧", *targets[1:]])
            with self.assertRaises(ValueError):
                compile_group(archive, [record], [target, target], expected_sha=sha)
            with self.assertRaises(ValueError):
                compile_group(archive, [dict(record, source_article_sha256="changed")], [target], expected_sha=sha)
