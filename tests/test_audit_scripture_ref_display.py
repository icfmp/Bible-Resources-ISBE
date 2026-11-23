import tempfile
import unittest
from pathlib import Path
from scripts.audit_scripture_ref_display import scan

NS = "http://www.tei-c.org/ns/1.0"


class ScriptureReferenceScanTests(unittest.TestCase):
    def test_flags_only_unambiguous_mismatch_without_mutation(self):
        xml = f'''<TEI xmlns="{NS}"><text><body><div n="AB" xml:id="a">
        <p xml:id="p"><ref xml:id="r1" cRef="Bible:Mark.4.6">Mr 14:36</ref>
        <ref xml:id="r2" cRef="Bible:Rom.8.15">Rom 8:15</ref>
        <ref xml:id="r3" cRef="Bible:Mark.4.6">4:6</ref>
        <ref xml:id="r4" cRef="Bible:Mark.4.6-Bible:Mark.4.7">Mr 4:6-7</ref>
        </p></div></body></text></TEI>'''
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fixture.xml"
            path.write_text(xml, encoding="utf-8")
            original = path.read_bytes()
            result = scan(path)
            self.assertEqual(result["articles_scanned"], 1)
            self.assertEqual(result["counts"]["references_with_cRef"], 4)
            self.assertEqual(result["counts"]["explicit_single_verse_assessed"], 2)
            self.assertEqual(result["candidate_count"], 1)
            self.assertEqual(result["cases"][0]["ref_xml_id"], "r1")
            self.assertFalse(result["cases"][0]["approved_change"])
            self.assertEqual(path.read_bytes(), original)

    def test_rejects_missing_article_identity(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fixture.xml"
            path.write_text(f'<TEI xmlns="{NS}"><text><body><div n="A"><p>x</p></div></body></text></TEI>')
            with self.assertRaisesRegex(ValueError, "identity"):
                scan(path)


if __name__ == "__main__":
    unittest.main()
