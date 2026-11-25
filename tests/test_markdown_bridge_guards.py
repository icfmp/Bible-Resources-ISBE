"""Negative regression controls: never infer or drop original TEI source nodes."""
import json
import re
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.export_tei_markdown_corpus import export
from scripts.markdown_translation_bridge import compile_draft
from scripts.translation_markdown_layout import template
from scripts.validate_translation_identity import TEI, sha256
from tests.test_export_tei_markdown_corpus import specimen


class MarkdownBridgeGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source.xml"
        specimen(self.source)
        self.sha = sha256(self.source)
        self.archive = self.root / "archive.zip"
        self.build_archive(self.archive)

    def build_archive(self, destination):
        export(self.source, destination, report=self.root / "report.json",
               expected_sha=sha256(self.source), expected_count=2)

    def translated(self):
        md = template(self.archive, "A", expected_sha=self.sha)
        for old, new in [
            ("# A\n", "# Un titre\n"),
            ("In the ", "Dans le "),
            (" and in ", " et en "),
            (" is written.", " est écrit."),
            ("Original editor's note.", "Note française."),
        ]:
            md = md.replace(old, new, 1)
        return md

    def compile(self, markdown):
        return compile_draft(self.archive, markdown, expected_sha=self.sha)

    def test_deleted_scripture_and_original_language_anchors_fail(self):
        md = self.translated()
        anchors = re.findall(r"⟦ISBE:KEEP:[^⟧]+⟧", md)
        self.assertEqual(len(anchors), 2)
        for anchor in anchors:
            with self.subTest(anchor=anchor):
                with self.assertRaisesRegex(ValueError, "anchor"):
                    self.compile(md.replace(anchor, "", 1))
                with self.assertRaisesRegex(ValueError, "anchor"):
                    self.compile(md.replace(anchor, "⟦ISBE:KEEP:999:forged⟧", 1))

    def test_source_fingerprint_and_original_paragraph_layout_cannot_change(self):
        md = self.translated()
        with self.assertRaisesRegex(ValueError, "source revision"):
            self.compile(md.replace(self.sha, "f" * 64, 1))
        with self.assertRaisesRegex(ValueError, "TEI paragraph|Unexpected content"):
            self.compile(md.replace("<!-- ISBE-BLOCK:2 -->", "<!-- ISBE-BLOCK:22 -->", 1))
        with self.assertRaisesRegex(ValueError, "block marker"):
            self.compile(md.replace("<!-- ISBE-END:2 -->", "<!-- ISBE-END:22 -->", 1))

    def test_english_text_without_reason_and_undeclared_preserve_fail(self):
        md = template(self.archive, "A", expected_sha=self.sha)
        with self.assertRaisesRegex(ValueError, "English text still present"):
            self.compile(md)
        draft = self.translated()
        end = draft.find(" -->\n\n")
        meta = json.loads(draft[len("<!-- ISBE-TRANSLATION-V1 "):end])
        meta["preserve"] = {"999:tail": "Invented anchor"}
        changed = ("<!-- ISBE-TRANSLATION-V1 "
                   + json.dumps(meta, ensure_ascii=False, sort_keys=True) + draft[end:])
        with self.assertRaisesRegex(ValueError, "unused"):
            self.compile(changed)

    def test_greek_embedded_in_editable_prose_must_remain_byte_exact(self):
        document = ET.parse(self.source)
        p = document.getroot().find(".//" + TEI + "p")
        p.text = "Greek λόγος in the "
        document.write(self.source, encoding="utf-8", xml_declaration=True)
        sha = sha256(self.source)
        archive = self.root / "greek.zip"
        self.build_archive(archive)
        md = template(archive, "A", expected_sha=sha)
        for old, new in [
            ("# A\n", "# Titre\n"),
            ("Greek λόγος in the ", "Le grec λογος dans le "),
            (" and in ", " et en "),
            (" is written.", " est écrit."),
            ("Original editor's note.", "Note française."),
        ]:
            md = md.replace(old, new, 1)
        with self.assertRaisesRegex(ValueError, "Greek script"):
            compile_draft(archive, md, expected_sha=sha)

    def test_extra_prose_without_original_source_slot_fails(self):
        document = ET.parse(self.source)
        p = document.getroot().find(".//" + TEI + "p")
        p.text = None
        for child in p:
            child.tail = None
        document.write(self.source, encoding="utf-8", xml_declaration=True)
        sha = sha256(self.source)
        archive = self.root / "only-immutable.zip"
        self.build_archive(archive)
        md = template(archive, "A", expected_sha=sha)
        md = md.replace("# A\n", "# Titre\n", 1)
        md = md.replace("Original editor's note.", "Note française.", 1)
        first = re.search(r"⟦ISBE:KEEP:[^⟧]+⟧", md).group()
        with self.assertRaisesRegex(ValueError, "without a source slot"):
            compile_draft(archive, md.replace(first, "Texte inventé " + first, 1),
                          expected_sha=sha)

    def test_tampered_archive_english_markdown_is_rejected(self):
        modified = self.root / "tampered.zip"
        with zipfile.ZipFile(self.archive) as original, zipfile.ZipFile(modified, "w") as dest:
            for name in original.namelist():
                data = original.read(name)
                if name == "en/articles/isbe-test-a.md":
                    data += b"\nUnauthorised amendment\n"
                dest.writestr(name, data)
        with self.assertRaisesRegex(ValueError, "checksum"):
            template(modified, "A", expected_sha=self.sha)


if __name__ == "__main__":
    unittest.main()
