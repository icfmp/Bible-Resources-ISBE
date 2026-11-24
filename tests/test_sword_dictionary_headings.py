"""No-silent-edit tests for source/adapter dictionary direct headings."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET

from scripts.audit_sword_dictionary_headings import TEI, analyze

def fixture(path, adapted=False):
    root = ET.Element(TEI + "TEI")
    text = ET.SubElement(root, TEI + "text")
    body = ET.SubElement(text, TEI + "body")
    for key, head in (("AARON", "AARON"), ("GRACE", "Grace"),
                      ("AALAR", None), ("BETH", "BETH")):
        attrs = {"n": key}
        if not adapted:
            attrs["type"] = "entry"
        article = ET.SubElement(body, TEI + ("entryFree" if adapted else "div"), attrs)
        if head is not None:
            ET.SubElement(article, TEI + "head").text = head
        ET.SubElement(article, TEI + "p").text = "Independent example with source text."
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

class HeadingAuditTests(unittest.TestCase):
    def test_counts_and_repeated_key_not_automatically_deleted(self):
        with TemporaryDirectory() as temp:
            temp = Path(temp)
            src, adapted, report = (temp / name for name in
                                    ("source.xml", "sword.xml", "report.json"))
            fixture(src)
            fixture(adapted, adapted=True)
            r = analyze(src, adapted, report)
            self.assertEqual(r["article_count"], 4)
            self.assertEqual(r["direct_heading_present_count"], 3)
            self.assertEqual(r["direct_heading_absent_count"], 1)
            self.assertEqual(r["first_direct_heading_equals_key_exact_count"], 2)
            self.assertEqual(r["first_direct_heading_equals_key_whitespace_normalized_count"], 2)
            self.assertEqual(r["direct_headings_changed_by_adapter_count"], 0)
            self.assertEqual(r["sample_articles"]["AARON"]["direct_headings"], ["AARON"])
            self.assertFalse(r["editorial_corrections_applied"])
            self.assertFalse(r["gui_duplicate_title_verified"])
            self.assertTrue(report.is_file())
    def test_rejects_changed_source_heading_even_with_identical_paragraph(self):
        with TemporaryDirectory() as temp:
            temp = Path(temp)
            src, adapted = temp / "source.xml", temp / "sword.xml"
            fixture(src)
            fixture(adapted, adapted=True)
            tree = ET.parse(adapted)
            article = next(a for a in tree.getroot().iter(TEI + "entryFree")
                           if a.get("n") == "AARON")
            article.find(TEI + "head").text = "CORRUPTED"
            tree.write(adapted, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Direct heading changed"):
                analyze(src, adapted, temp / "report.json")
    def test_rejects_changed_entry_set(self):
        with TemporaryDirectory() as temp:
            temp = Path(temp)
            src, adapted = temp / "source.xml", temp / "sword.xml"
            fixture(src)
            fixture(adapted, adapted=True)
            tree = ET.parse(adapted)
            body = tree.getroot().find("./" + TEI + "text/" + TEI + "body")
            body.remove(body[-1])
            tree.write(adapted, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "article keys changed"):
                analyze(src, adapted, temp / "report.json")

if __name__ == "__main__":
    unittest.main()
