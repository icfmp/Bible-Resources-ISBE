import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_tei_structure import analyze

TEI = "http://www.tei-c.org/ns/1.0"


class TeiInventoryTests(unittest.TestCase):
    def test_mixed_source_namespace_and_link_semantics_are_reported(self):
        xml = f'''<TEI xmlns="{TEI}">
          <teiHeader><fileDesc><titleStmt><title>Sample</title></titleStmt>
          <publicationStmt><p>Draft</p></publicationStmt><sourceDesc><p>Sample</p>
          </sourceDesc></fileDesc></teiHeader>
          <text><body><div type="entry" xml:id="isbe-x" n="SAMPLE">
            <head xml:id="isbe-x-head">SAMPLE</head>
            <p xmlns="" xml:id="isbe-x-n1">A
              <ref xml:id="isbe-x-n2" osisRef="Bible:Gen.1.1">Genesis</ref>
              <hi rend="underline">one</hi>.
            </p>
            <seg type="unlinked-source-reference" n="ISBE:MISSING"
                 xml:id="isbe-x-n4">Missing</seg>
          </div></body></text>
        </TEI>'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, "sample.xml")
            path.write_text(xml, encoding="utf-8")
            report = analyze(path)
        self.assertEqual(report["entry_count"], 1)
        self.assertEqual(report["elements_by_namespace"]["(none)"], 3)
        self.assertEqual(report["link_classes"]["source_osisRef"], 1)
        self.assertEqual(report["link_classes"]["inert_original_isbe_reference"], 1)
        self.assertEqual(report["inline_rendering_values"]["underline"], 1)
        self.assertEqual(report["duplicate_xml_ids"], [])
        self.assertEqual(report["schema_validation"], "NOT_PERFORMED")
        self.assertEqual(report["profile_status"], "migration_required")
        self.assertEqual(report["profile_rule_findings"]["legacy_crosswire_osisRef_attribute"]["count"], 1)
        self.assertEqual(report["profile_rule_findings"]["untyped_reference"]["count"], 1)
        self.assertEqual(report["profile_rule_findings"]["index_head_not_typed"]["count"], 1)

    def test_proposed_subset_rules_can_pass_without_claiming_official_schema(self):
        xml = f'''<TEI xmlns="{TEI}" xml:lang="en">
          <teiHeader><fileDesc><titleStmt><title>Sample</title></titleStmt>
          <publicationStmt><p>Draft</p></publicationStmt><sourceDesc><p>Sample</p>
          </sourceDesc></fileDesc><encodingDesc><refsDecl><p>Bible canonical references</p>
          </refsDecl></encodingDesc><revisionDesc><change>Initial draft</change></revisionDesc>
          </teiHeader><text><body><div type="entry" xml:id="isbe-x" n="SAMPLE">
            <head type="index" xml:id="isbe-x-head">SAMPLE</head>
            <p xml:id="isbe-x-n1">A <ref type="scripture" cRef="Bible:Gen.1.1"
            xml:id="isbe-x-n2">Genesis</ref>.</p>
          </div></body></text></TEI>'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, "candidate.xml")
            path.write_text(xml, encoding="utf-8")
            report = analyze(path)
        self.assertEqual(report["profile_status"], "candidate_subset_conformant")
        self.assertEqual(report["profile_rule_findings"], {})
        self.assertEqual(report["schema_validation"], "NOT_PERFORMED")

    def test_reject_non_tei_document(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, "bad.xml")
            path.write_text("<data/>", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Expected a TEI root"):
                analyze(path)


if __name__ == "__main__":
    unittest.main()
