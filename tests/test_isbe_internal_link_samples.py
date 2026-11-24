"""Regression checks for source-attested internal dictionary link samples."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET
from scripts.select_isbe_internal_link_samples import analyse, ref_offsets, TEI, XML

def fixture(path,adapter=False,wrong=False):
    root=ET.Element(TEI+"TEI")
    body=ET.SubElement(ET.SubElement(root,TEI+"text"),TEI+"body")
    for key in ("INTRO","NEXT"):
        attrs={"n":key,XML+"id":key.lower()}
        if not adapter:attrs["type"]="entry"
        entry=ET.SubElement(body,TEI+("entryFree" if adapter else "div"),attrs)
        ET.SubElement(entry,TEI+"head").text=key
        p=ET.SubElement(entry,TEI+"p")
        if key=="INTRO":
            p.text="Read "
            link=ET.SubElement(p,TEI+"ref",{"target":(
                "TESTLD:INTRO" if wrong else "TESTLD:NEXT"
            ) if adapter else "#next",**({"corresp":"#next"} if adapter else {})})
            link.text="NEXT"
            link.tail=" for background."
        else:p.text="A distinct dictionary article."
    ET.ElementTree(root).write(path,encoding="utf-8",xml_declaration=True)

class SelectedLinksTests(unittest.TestCase):
    def test_first_real_cross_article_link(self):
        with TemporaryDirectory() as d:
            src,out,rep=(Path(d)/x for x in ("source.xml","native.xml","links.json"))
            fixture(src)
            fixture(out,adapter=True)
            result=analyse(src,out,rep,module_id="TESTLD")
            self.assertEqual(result["source_article_count"],2)
            self.assertEqual(result["cross_article_reference_count"],1)
            self.assertEqual(result["articles_with_cross_article_references"],1)
            sample=result["chosen_samples"][0]
            self.assertEqual((sample["source_article"],sample["destination_article"]),("INTRO","NEXT"))
            self.assertEqual(sample["first_cross_article_link_text_offset"],len("INTRORead "))
            self.assertTrue(sample["is_first_clickable_reference"])
            self.assertFalse(result["actual_GUI_dictionary_link_click_verified"])
            self.assertTrue(rep.is_file())
    def test_corrupt_native_target_fails(self):
        with TemporaryDirectory() as d:
            src,out,rep=(Path(d)/x for x in ("source.xml","native.xml","links.json"))
            fixture(src);fixture(out,adapter=True,wrong=True)
            with self.assertRaisesRegex(ValueError,"not correctly mapped"):
                analyse(src,out,rep,module_id="TESTLD")
    def test_offset_counts_nested_link_text_once(self):
        root=ET.Element(TEI+"entryFree")
        p=ET.SubElement(root,TEI+"p")
        p.text="Hello "
        r=ET.SubElement(p,TEI+"ref",{"target":"TESTLD:NEXT"})
        ET.SubElement(r,TEI+"hi").text="NEXT"
        r.tail=" after"
        self.assertEqual(ref_offsets(root)[0][0],6)

if __name__=="__main__":
    unittest.main()
