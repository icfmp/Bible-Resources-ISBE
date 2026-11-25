"""End-to-end lossless Markdown workspace tests with a synthetic TEI witness."""
from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.export_tei_markdown_corpus import (
    export, original_markdown, original_nodes, reassemble_nodes,
)
from scripts.select_translation_pilot import stable_xml_fingerprint
from scripts.validate_translation_identity import TEI, XML_ID, XML_LANG, sha256


def specimen(path: Path) -> None:
    root = ET.Element(TEI + "TEI", {XML_LANG: "en"})
    ET.SubElement(root, TEI + "teiHeader")
    body = ET.SubElement(ET.SubElement(root, TEI + "text"), TEI + "body")
    a = ET.SubElement(body, TEI + "div", {XML_ID: "isbe-test-a", "type": "entry", "n": "A"})
    ET.SubElement(a, TEI + "head", {XML_ID: "test-head"}).text = "A"
    p = ET.SubElement(a, TEI + "p", {XML_ID: "test-p"})
    p.text = "In the "
    foreign = ET.SubElement(p, TEI + "foreign", {"lang": "grc"})
    foreign.text = "λόγος"
    foreign.tail = " and in "
    ref = ET.SubElement(p, TEI + "ref", {"type": "scripture", "cRef": "Jn.1.1"})
    ref.text = "Joh 1:1"
    ref.tail = " is written."
    note = ET.SubElement(a, TEI + "note", {XML_ID: "test-note"})
    note.text = "Original editor's note."
    b = ET.SubElement(body, TEI + "div", {XML_ID: "isbe-test-b", "type": "entry", "n": "B"})
    ET.SubElement(b, TEI + "head").text = "B"
    child = ET.SubElement(b, TEI + "div", {XML_ID: "inner"})
    ET.SubElement(child, TEI + "head").text = "Section"
    ET.SubElement(child, TEI + "p").text = "A second paragraph."
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


class MarkdownCorpusTests(unittest.TestCase):
    def test_lossless_node_map_with_source_owned_references_and_scripts(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.xml"
            specimen(source)
            root = ET.parse(source).getroot()
            article = root.find(".//" + TEI + "div")
            nodes = original_nodes(article)
            self.assertEqual(stable_xml_fingerprint(reassemble_nodes(nodes)),
                             stable_xml_fingerprint(article))
            self.assertIn("λόγος", original_markdown(article, source_digest="a" * 64))
            self.assertIn("Joh 1:1", original_markdown(article, source_digest="a" * 64))
            self.assertEqual(
                [n["attributes"]["cRef"] for n in nodes if "cRef" in n["attributes"]],
                ["Jn.1.1"])
            self.assertTrue(any(n["attributes"].get(XML_ID) == "test-note" for n in nodes))

    def test_full_archive_is_reproducible_and_all_articles_mapped(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "source.xml"
            specimen(source)
            z1, z2 = base / "one.zip", base / "two.zip"
            report1, report2 = base / "one.json", base / "two.json"
            args = {"expected_sha": sha256(source), "expected_count": 2}
            first = export(source, z1, report=report1, **args)
            second = export(source, z2, report=report2, **args)
            self.assertEqual(first, second)
            self.assertEqual(first["canonical_article_count"], 2)
            self.assertEqual(first["lossless_source_maps"], 2)
            self.assertEqual(first["french_unreviewed_drafts"], 0)
            self.assertEqual(first["archive_sha256"], sha256(z1))
            self.assertEqual(z1.read_bytes(), z2.read_bytes())
            with zipfile.ZipFile(z1) as archive:
                manifest = json.loads(archive.read("MANIFEST.json"))
                self.assertEqual(manifest["canonical_article_count"], 2)
                self.assertEqual(
                    [row["source_key"] for row in manifest["articles"]], ["A", "B"])
                self.assertEqual(len([n for n in archive.namelist()
                                      if n.startswith("en/articles/")]), 2)
                for row in manifest["articles"]:
                    source_map = json.loads(archive.read(row["source_map"]))
                    self.assertEqual(stable_xml_fingerprint(
                        reassemble_nodes(source_map["nodes"])),
                        row["source_article_sha256"])
                    self.assertTrue(archive.read(row["markdown"]).startswith(b"# "))
                    self.assertEqual(source_map["source_key"], row["source_key"])
                    self.assertEqual(source_map["source_position"], row["source_position"])
                self.assertIn("not independently editorially", archive.read("README.md").decode())

    def test_source_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.xml"
            specimen(source)
            with self.assertRaisesRegex(ValueError, "unpinned"):
                export(source, root / "a.zip", report=root / "report.json",
                       expected_sha="0" * 64, expected_count=2)
            with self.assertRaisesRegex(ValueError, "count mismatch"):
                export(source, root / "a.zip", report=root / "report.json",
                       expected_sha=sha256(source), expected_count=9380)

    def test_corrupt_parent_map_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.xml"
            specimen(source)
            article = ET.parse(source).getroot().find(".//" + TEI + "div")
            nodes = original_nodes(article)
            nodes[1]["parent"] = 99
            with self.assertRaisesRegex(ValueError, "parent"):
                reassemble_nodes(nodes)


if __name__ == "__main__":
    unittest.main()
