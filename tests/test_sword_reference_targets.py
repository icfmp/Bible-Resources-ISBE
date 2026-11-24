"""Regression tests for original-to-native SWORD reference navigation provenance."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET
from scripts.audit_sword_reference_targets import analyze, N, XML

def fixture(path,adapted=False,corrupt=None):
    root=ET.Element(N+"TEI")
    text=ET.SubElement(root,N+"text")
    body=ET.SubElement(text,N+"body")
    for key,id_ in [("AARON","a"),("ABIDE","b")]:
        attrs={"n":key,XML+"id":id_}
        if not adapted:attrs["type"]="entry"
        entry=ET.SubElement(body,N+("entryFree" if adapted else "div"),attrs)
        ET.SubElement(entry,N+"head").text=key
        if key=="ABIDE":
            div=ET.SubElement(entry,N+"div",{XML+"id":"b_section"})
            ET.SubElement(div,N+"head").text="Third part"
        else:
            paragraph=ET.SubElement(entry,N+"p")
            a=ET.SubElement(paragraph,N+"ref",{"target":("TESTLD:ABIDE" if adapted else "#b"),
                                              **({"corresp":"#b"} if adapted else {})})
            a.text="ABIDE"
            b=ET.SubElement(paragraph,N+"ref",{"type":"section",
                       "target":("TESTLD:ABIDE" if adapted else "#b_section"),
                       **({"corresp":"#b_section"} if adapted else {})})
            b.text="Third part"
            c=ET.SubElement(paragraph,N+"ref",{"cRef":"Exod.6.20",
                                               **({"osisRef":"Exod.6.20"} if adapted else {})})
            c.text="Ex 6:20"
    if corrupt=="target":
        for r in root.iter(N+"ref"):
            if r.get("type")=="section":r.set("target","TESTLD:AARON")
    if corrupt=="bible":
        for r in root.iter(N+"ref"):
            if r.get("cRef"):r.set("osisRef","Exod.6.21")
    ET.ElementTree(root).write(path,encoding="utf-8",xml_declaration=True)

class NavigationAuditTests(unittest.TestCase):
    def prepare(self,temp,corrupt=None):
        orig,adapter,report=(temp/"original.xml",temp/"adapted.xml",temp/"report.json")
        fixture(orig)
        fixture(adapter,adapted=True,corrupt=corrupt)
        return orig,adapter,report
    def test_complete_section_and_biblical_provenance(self):
        with TemporaryDirectory() as tempdir:
            orig,adapter,report=self.prepare(Path(tempdir))
            value=analyze(orig,adapter,report,"TESTLD")
            self.assertEqual(value["source_article_count"],2)
            self.assertEqual(value["internal_dictionary_refs"],2)
            self.assertEqual(value["article_target_refs"],1)
            self.assertEqual(value["nested_target_refs"],1)
            self.assertEqual(value["section_typed_refs"],1)
            self.assertEqual(value["bible_osis_references"],1)
            self.assertEqual(value["section_ref_register_count"],1)
            self.assertEqual(value["section_scroll_precision_limited_count"],1)
            self.assertEqual(value["section_ref_register"][0]["destination_heading"],"Third part")
            self.assertEqual(value["section_ref_register"][0]["original_target"],"#b_section")
            self.assertTrue(value["source_and_adapter_attributes_verified"])
            self.assertTrue(report.is_file())
    def test_corrupt_section_navigation_is_rejected(self):
        with TemporaryDirectory() as tempdir:
            orig,adapter,report=self.prepare(Path(tempdir),"target")
            with self.assertRaisesRegex(ValueError,"attributes changed"):
                analyze(orig,adapter,report,"TESTLD")
    def test_corrupt_biblical_target_is_rejected(self):
        with TemporaryDirectory() as tempdir:
            orig,adapter,report=self.prepare(Path(tempdir),"bible")
            with self.assertRaisesRegex(ValueError,"attributes changed"):
                analyze(orig,adapter,report,"TESTLD")

if __name__=="__main__":
    unittest.main()
