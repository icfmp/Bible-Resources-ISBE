"""Tests for source-locked, read-only editorial notice scanning."""
import tempfile
import unittest
from pathlib import Path

from scripts.audit_editorial_notices import scan

NS="http://www.tei-c.org/ns/1.0"

class AuditEditorialNoticesTests(unittest.TestCase):
    def test_matching_is_candidate_only_and_non_destructive(self):
        xml=f'''<TEI xmlns="{NS}"><text><body><div type="entry" n="A" xml:id="a">
        <head xml:id="h">A</head><p xml:id="p1">CrossWire digitized this.</p>
        <p xml:id="p2">Editors of the ancient canon differed.</p>
        <p xml:id="p3">This is an editor's note.</p>
        </div></body></text></TEI>'''
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"x.xml"
            path.write_text(xml,encoding="utf-8")
            original=path.read_bytes()
            result=scan(path)
            self.assertEqual(len(result["cases"]),2)
            self.assertEqual(result["cases"][0]["unit_xml_id"],"p1")
            self.assertEqual(result["cases"][1]["unit_xml_id"],"p3")
            self.assertTrue(all(case["remove"] is False for case in result["cases"]))
            self.assertEqual(path.read_bytes(),original)

    def test_missing_article_id_rejected(self):
        xml=f'<TEI xmlns="{NS}"><text><body><div type="entry" n="A"><p>OCR</p></div></body></text></TEI>'
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"x.xml"
            path.write_text(xml,encoding="utf-8")
            with self.assertRaises(ValueError):
                scan(path)

if __name__=="__main__":
    unittest.main()
