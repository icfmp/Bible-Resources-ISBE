"""Regression controls for the read-only editorial inventory."""
import tempfile
import unittest
from pathlib import Path
from scripts.audit_empty_paragraphs import inventory

NS = "http://www.tei-c.org/ns/1.0"

class EmptyParagraphAuditTest(unittest.TestCase):
    def test_detects_empty_nodes_without_changing_source(self):
        xml = f'''<TEI xmlns="{NS}"><teiHeader/><text><body>
        <div type="entry" n="TEST" xml:id="test-entry">
        <head xml:id="test-head">TEST</head>
        <p xml:id="test-1">Before.</p>
        <p xml:id="test-2"></p>
        <p xml:id="test-3">  </p>
        <p xml:id="test-4">A <ref cRef="Bible:Gen.1.1">citation</ref></p>
        <p xml:id="test-5">After.</p>
        </div></body></text></TEI>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.xml"
            path.write_text(xml, encoding="utf-8")
            before = path.read_bytes()
            result = inventory(path)
            self.assertEqual(result["count"], 2)
            self.assertEqual(
                [entry["paragraph_xml_id"] for entry in result["cases"]],
                ["test-2", "test-3"],
            )
            self.assertEqual(result["cases"][0]["previous_text_excerpt"], "Before.")
            self.assertEqual(result["cases"][1]["next_text_excerpt"], "After.")
            self.assertEqual(path.read_bytes(), before)

    def test_rejects_missing_article_identity(self):
        xml = f'''<TEI xmlns="{NS}"><text><body><div type="entry">
          <p xml:id="p1"/></div></body></text></TEI>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.xml"
            path.write_text(xml, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source key or stable ID"):
                inventory(path)

if __name__ == "__main__":
    unittest.main()
