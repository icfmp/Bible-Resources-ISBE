"""Regression tests: translated ISBE must never be independently reindexed."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_translation_identity import compare

NS = "{http://www.tei-c.org/ns/1.0}"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
XMLLANG = "{http://www.w3.org/XML/1998/namespace}lang"


def fixture(language, *, title="ALPHA", paragraph="Original prose."):
    root = ET.Element(NS + "TEI", {XMLLANG: language})
    header = ET.SubElement(root, NS + "teiHeader")
    ET.SubElement(header, NS + "fileDesc")
    body = ET.SubElement(ET.SubElement(root, NS + "text"), NS + "body")
    for name in ("ALPHA", "BETA"):
        article = ET.SubElement(body, NS + "div", {
            "type": "entry", "n": name, XMLID: "isbe-" + name.lower()
        })
        head = ET.SubElement(article, NS + "head", {
            "type": "index", XMLID: "isbe-" + name.lower() + "-head"
        })
        head.text = title if name == "ALPHA" else "BETA"
        paragraph_node = ET.SubElement(article, NS + "p", {
            XMLID: "isbe-" + name.lower() + "-p"
        })
        paragraph_node.text = paragraph
        ref = ET.SubElement(paragraph_node, NS + "ref", {
            XMLID: "isbe-" + name.lower() + "-ref",
            "type": "article", "target": "#isbe-beta", "n": "ISBE:BETA",
        })
        ref.text = "see BETA"
        ref.tail = "."
        scripture = ET.SubElement(article, NS + "ref", {
            XMLID: "isbe-" + name.lower() + "-scripture",
            "type": "scripture", "cRef": "Bible:Gen.1.1"
        })
        scripture.text = "Ge 1:1"
        foreign = ET.SubElement(article, NS + "foreign", {
            XMLID: "isbe-" + name.lower() + "-greek", XMLLANG: "grc",
        })
        foreign.text = "λόγος"
        note = ET.SubElement(article, NS + "note", {
            XMLID: "isbe-" + name.lower() + "-note"
        })
        note.text = "Historical note."
    return root


class SharedISBEIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.source = self.folder / "en.xml"
        self.target = self.folder / "translated.xml"
        self.write(self.source, fixture("en"))

    def write(self, path, root):
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

    def assert_valid(self, target, target_lang="fr"):
        self.write(self.target, target)
        locked = hashlib.sha256(self.source.read_bytes()).hexdigest()
        return compare(self.source, self.target,
                       expected_source_sha256=locked, expected_count=2,
                       target_language=target_lang)

    def test_french_and_german_can_share_index_with_translated_display(self):
        for language, title, paragraph in (
            ("fr", "Alpha en français", "Prose en français."),
            ("de", "Alpha auf Deutsch", "Prosa auf Deutsch."),
        ):
            with self.subTest(language=language):
                report = self.assert_valid(
                    fixture(language, title=title, paragraph=paragraph),
                    target_lang=language)
                self.assertTrue(report["canonical_article_index_identical"])
                self.assertEqual(report["article_count"], 2)
                self.assertEqual(report["stable_body_xml_ids"], 12)
                self.assertFalse(report["publication_approved"])

    def test_reject_translated_source_key(self):
        target = fixture("fr")
        target.find(".//" + NS + "div").set("n", "ALPHA FRANÇAIS")
        with self.assertRaisesRegex(ValueError, "index differs"):
            self.assert_valid(target)

    def test_reject_article_id_change(self):
        target = fixture("fr")
        target.find(".//" + NS + "div").set(XMLID, "french-alpha")
        with self.assertRaisesRegex(ValueError, "index differs"):
            self.assert_valid(target)

    def test_reject_duplicate_missing_and_reordered_entries(self):
        for mode in ("duplicate", "missing", "reorder"):
            target = fixture("fr")
            body = target.find("./" + NS + "text/" + NS + "body")
            if mode == "duplicate":
                body[1].set("n", "ALPHA")
                body[1].set(XMLID, "isbe-alpha")
            elif mode == "missing":
                body.remove(body[1])
            else:
                body[:] = list(reversed(list(body)))
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.assert_valid(target)

    def test_reject_removed_paragraph_and_section_identity(self):
        target = fixture("fr")
        paragraph = target.find(".//" + NS + "p")
        paragraph.set(XMLID, "translated-paragraph")
        with self.assertRaisesRegex(ValueError, "attributes or canonical IDs"):
            self.assert_valid(target)
        target = fixture("fr")
        article = target.find(".//" + NS + "div")
        article.remove(article.find(NS + "p"))
        with self.assertRaisesRegex(ValueError, "structure|order/type"):
            self.assert_valid(target)

    def test_reject_link_target_reference_or_provenance_change(self):
        for attribute, new_value in (
            ("target", "#isbe-missing"), ("target", "#isbe-alpha"),
            ("n", "ISBE:ALPHA"),
        ):
            target = fixture("fr")
            ref = target.find(".//" + NS + "ref[@type='article']")
            ref.set(attribute, new_value)
            with self.subTest(attribute=attribute, new_value=new_value):
                with self.assertRaisesRegex(ValueError, "attributes"):
                    self.assert_valid(target)

        target = fixture("fr")
        target.find(".//" + NS + "ref[@type='scripture']").set(
            "cRef", "Bible:Gen.1.2")
        with self.assertRaisesRegex(ValueError, "attributes"):
            self.assert_valid(target)

    def test_reject_changed_original_language_text(self):
        target = fixture("fr")
        target.find(".//" + NS + "foreign").text = "parole"
        with self.assertRaisesRegex(ValueError, "foreign text"):
            self.assert_valid(target)

    def test_reject_wrong_source_checksum_and_wrong_target_language(self):
        target = fixture("fr")
        self.write(self.target, target)
        with self.assertRaisesRegex(ValueError, "SHA-256 changed"):
            compare(self.source, self.target,
                    expected_source_sha256="0" * 64, expected_count=2,
                    target_language="fr")
        with self.assertRaisesRegex(ValueError, "root language"):
            self.assert_valid(target, target_lang="de")


if __name__ == "__main__":
    unittest.main()
