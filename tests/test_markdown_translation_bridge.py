"""Small fixture smoke tests for the source-locked Markdown bridge."""
import tempfile
import unittest
from pathlib import Path
from scripts.export_tei_markdown_corpus import export
from scripts.translation_markdown_layout import template, read_draft
from scripts.markdown_translation_bridge import compile_draft
from scripts.validate_translation_identity import sha256
from tests.test_export_tei_markdown_corpus import specimen

class BridgeSmokeTests(unittest.TestCase):
    def test_french_paragraph_and_protected_scripture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.xml"
            specimen(source)
            sha = sha256(source)
            archive = root / "corpus.zip"
            export(source, archive, report=root / "report.json",
                   expected_sha=sha, expected_count=2)
            draft = template(archive, "A", expected_sha=sha)
            self.assertEqual(len(read_draft(draft)[1]), 3)
            self.assertIn("λόγος", draft)
            self.assertIn("Joh 1:1", draft)
            for old, new in [
                ("# A\n", "# Un titre\n"),
                ("In the ", "Dans le "),
                (" and in ", " et en "),
                (" is written.", " est écrit."),
                ("Original editor's note.", "Note de l'éditeur."),
            ]:
                self.assertIn(old, draft)
                draft = draft.replace(old, new, 1)
            patch, report = compile_draft(archive, draft, expected_sha=sha)
            self.assertEqual(report["source_mutable_text_units"], 5)
            self.assertFalse(report["publication_permitted"])
            self.assertEqual(patch["articles"][0]["source_key"], "A")
            self.assertTrue(all(u["action"] == "translate" for u in patch["articles"][0]["units"]))

if __name__ == "__main__":
    unittest.main()
