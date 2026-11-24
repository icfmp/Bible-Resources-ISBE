"""Native SWORD adapter's source/markup/key fail-closed regression tests."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET

from scripts.export_tei_dictionary_for_sword import convert, read_entries, NS, XML, digest
from scripts.validate_sword_dictionary_roundtrip import analyze

def make_source(path, duplicates=False):
    root=ET.Element(NS+"TEI")
    header=ET.SubElement(root,NS+"teiHeader")
    desc=ET.SubElement(header,NS+"fileDesc")
    title=ET.SubElement(desc,NS+"titleStmt")
    ET.SubElement(title,NS+"title").text="Synthetic unit-test-only TEI"
    text=ET.SubElement(root,NS+"text")
    body=ET.SubElement(text,NS+"body")
    for i,key in enumerate(("ALPHA","ALPHA" if duplicates else "BETA")):
        entry=ET.SubElement(body,NS+"div",{"type":"entry","n":key,f"{{{XML}}}id":f"entry-{i}"})
        ET.SubElement(entry,NS+"head").text=key
        para=ET.SubElement(entry,NS+"p")
        para.text="café Καὶ עברית "
        ref=ET.SubElement(para,NS+"ref",{"cRef":"Bible:John.3.16","type":"scripture"})
        ref.text="Jn 3:16"
        ref.tail=" content."
    # Source-owned internal navigation is by xml:id; the SWORD adapter must
    # rewrite to an actual dictionary headword without losing the original ID.
    first=body[0].find(NS+"p")
    anchor=ET.SubElement(first,NS+"ref",{"target":"#entry-1","type":"entry"})
    anchor.text="BETA"
    ET.ElementTree(root).write(path,encoding="utf-8",xml_declaration=True)

class SwordAdapterTests(unittest.TestCase):
    def test_source_conversion_keeps_every_text_character_and_entry_id(self):
        with TemporaryDirectory() as folder:
            folder=Path(folder)
            source=folder/"source.xml"
            produced=folder/"sword.xml"
            report=folder/"report.json"
            make_source(source)
            result=convert(source,produced,report,digest(source),2,"TESTLD")
            self.assertEqual(result["source_entry_count"],2)
            self.assertEqual(result["converted_entry_count"],2)
            self.assertTrue(result["article_ids_preserved"])
            self.assertTrue(result["entry_visible_text_preserved"])
            self.assertFalse(result["publication_permitted"])
            self.assertEqual(result["nested_divisions_preserved_unadapted"],0)
            text=produced.read_text(encoding="utf-8")
            self.assertIn("entryFree",text)
            self.assertIn("café Καὶ עברית",text)
            self.assertEqual(len(ET.parse(produced).find("./"+NS+"text/"+NS+"body")),2)
            self.assertEqual(result["internal_references_retargeted_to_source_key"],1)
            self.assertEqual(result["scripture_references_exposed_via_osisRef"],2)
            entry=ET.parse(produced).find("./"+NS+"text/"+NS+"body")[0]
            refs=list(entry.iter(NS+"ref"))
            self.assertEqual(refs[0].get("osisRef"),"Bible:John.3.16")
            self.assertEqual(refs[1].get("target"),"TESTLD:BETA")
            self.assertEqual(refs[1].get("corresp"),"#entry-1")

    def test_wrong_hash_missing_keys_and_duplicated_keys_fail(self):
        with TemporaryDirectory() as folder:
            folder=Path(folder)
            src=folder/"source.xml"
            make_source(src)
            with self.assertRaises(ValueError):
                read_entries(src,"0"*64,2)
            with self.assertRaises(ValueError):
                read_entries(src,digest(src),9380)
            make_source(src,duplicates=True)
            with self.assertRaises(ValueError):
                read_entries(src,digest(src),2)

    def test_broken_internal_target_fails_instead_of_silently_dropping_reference(self):
        with TemporaryDirectory() as folder:
            folder=Path(folder)
            src=folder/"source.xml"
            make_source(src)
            root=ET.parse(src)
            internal=next(ref for ref in root.getroot().iter(NS+"ref")
                          if ref.get("target")=="#entry-1")
            self.assertEqual(internal.get("target"),"#entry-1")
            internal.set("target","#missing-target")
            root.write(src,encoding="utf-8",xml_declaration=True)
            with self.assertRaisesRegex(ValueError,"Unresolved"):
                convert(src,folder/"sword.xml",folder/"report.json",digest(src),2,"TESTLD")

    def test_native_readback_detects_full_text_and_markup_corruption(self):
        with TemporaryDirectory() as folder:
            folder=Path(folder)
            src=folder/"source.xml"
            target=folder/"sword.xml"
            report=folder/"report.json"
            imp=folder/"native.imp"
            make_source(src)
            convert(src,target,report,digest(src),2,"TESTLD")
            root=ET.parse(target).getroot()
            entries=list(root.find("./"+NS+"text/"+NS+"body"))
            imp.write_text("".join("$$$"+e.get("n")+"\n"+ET.tostring(e,encoding="unicode")+"\n" for e in entries),
                           encoding="utf-8")
            audit=analyze(target,imp,folder/"native-report.json")
            self.assertTrue(audit["native_roundtrip_verified"])
            self.assertEqual(audit["native_keys"],2)
            imp.write_text(imp.read_text(encoding="utf-8").replace("Καὶ","NOT ORIGINAL"),
                           encoding="utf-8")
            tampered=analyze(target,imp,folder/"tampered.json")
            self.assertFalse(tampered["native_roundtrip_verified"])
            self.assertGreater(tampered["unicode_text_mismatch_count"],0)

    def test_native_readback_requires_all_keys(self):
        with TemporaryDirectory() as folder:
            folder=Path(folder)
            src=folder/"source.xml"
            target=folder/"sword.xml"
            report=folder/"report.json"
            imp=folder/"native.imp"
            make_source(src)
            convert(src,target,report,digest(src),2,"TESTLD")
            entry=ET.parse(target).find("./"+NS+"text/"+NS+"body")[0]
            imp.write_text("$$$ALPHA\n"+ET.tostring(entry,encoding="unicode")+"\n",encoding="utf-8")
            audit=analyze(target,imp,folder/"native-report.json")
            self.assertFalse(audit["native_roundtrip_verified"])
            self.assertEqual(audit["missing_key_count"],1)

if __name__=="__main__":
    unittest.main()
