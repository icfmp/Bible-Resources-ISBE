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


    def test_paratext_profile_includes_boundaries_and_surroundings(self):
        xml=f'''<TEI xmlns="{NS}"><text><body><div type="entry" n="A" xml:id="a">
        <head xml:id="h" type="index">A</head>
        <p xml:id="p1">Article about ancient copyright law.</p>
        <p xml:id="p2">Click here to read more.</p>
        <list><item xml:id="i1">Privacy Policy</item></list>
        <p xml:id="p3">https://example.org/fictitious-edition</p>
        </div></body></text></TEI>'''
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"x.xml"
            path.write_text(xml,encoding="utf-8")
            before=path.read_bytes()
            result=scan(path,profile="paratext")
            self.assertEqual(result["articles_scanned"],1)
            self.assertEqual(result["units_scanned"],5)
            self.assertEqual([c["unit_xml_id"] for c in result["cases"]],
                             ["p2","i1","p3"])
            self.assertEqual(result["cases"][0]["unit_position_zero_based"],2)
            self.assertIn("ancient copyright law",
                          result["cases"][0]["previous_unit_excerpt"])
            self.assertEqual(result["cases"][1]["next_unit_excerpt"],
                             "https://example.org/fictitious-edition")
            self.assertTrue(all(case["remove"] is False for case in result["cases"]))
            self.assertEqual(path.read_bytes(),before)

    def test_unknown_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            scan("not-an-existing-file.xml",profile="unsupported")

    def test_missing_article_id_rejected(self):
        xml=f'<TEI xmlns="{NS}"><text><body><div type="entry" n="A"><p>OCR</p></div></body></text></TEI>'
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"x.xml"
            path.write_text(xml,encoding="utf-8")
            with self.assertRaises(ValueError):
                scan(path)

if __name__=="__main__":
    unittest.main()
