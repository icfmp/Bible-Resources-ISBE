"""Source-locked Greek/Hebrew and nested TEI GUI fixture selection."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET
from scripts.audit_sword_presentation_samples import N, analyse, classified

def fixture(path, adapted=False, mutate=False):
    root=ET.Element(N+"TEI")
    body=ET.SubElement(ET.SubElement(root,N+"text"),N+"body")
    for key,text in (("GREEK","ἀγάπη is Greek"),("HEBREW","שָׁלוֹם is Hebrew"),
                     ("NESTED","A section"),("ORDINARY","No original script")):
        attrs={"n":key}
        if not adapted:attrs["type"]="entry"
        e=ET.SubElement(body,N+("entryFree" if adapted else "div"),attrs)
        if key=="NESTED":
            section=ET.SubElement(e,N+"div")
            ET.SubElement(section,N+"p").text=text
        else:
            ET.SubElement(e,N+"p").text=("altered" if mutate and key=="GREEK" else text)
    ET.ElementTree(root).write(path,encoding="utf-8",xml_declaration=True)

class ScriptSelectionTests(unittest.TestCase):
    def test_classifier_and_full_parity(self):
        self.assertEqual(classified("ἀ"),"greek")
        self.assertEqual(classified("ש"),"hebrew")
        self.assertIsNone(classified("A"))
        with TemporaryDirectory() as name:
            tmp=Path(name);src=tmp/"src.xml";out=tmp/"import.xml";report=tmp/"r.json"
            fixture(src);fixture(out,adapted=True)
            result=analyse(src,out,report)
            self.assertEqual(result["source_article_count"],4)
            self.assertEqual(result["greek_character_article_count"],1)
            self.assertEqual(result["hebrew_character_article_count"],1)
            self.assertEqual(result["nested_division_article_count"],1)
            self.assertEqual(result["nested_division_count"],1)
            self.assertEqual(result["gui_candidate_samples"]["greek"][0]["key"],"GREEK")
            self.assertEqual(result["gui_candidate_samples"]["hebrew"][0]["key"],"HEBREW")
            self.assertFalse(result["actual_gui_greek_rendering_verified"])
            self.assertTrue(report.is_file())
    def test_changed_original_script_fails(self):
        with TemporaryDirectory() as name:
            tmp=Path(name);src=tmp/"src.xml";out=tmp/"import.xml"
            fixture(src);fixture(out,adapted=True,mutate=True)
            with self.assertRaisesRegex(ValueError,"Source script/text changed"):
                analyse(src,out,tmp/"r.json")

if __name__=="__main__":
    unittest.main()
