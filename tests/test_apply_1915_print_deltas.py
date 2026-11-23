"""Reversible exact-reference print edits; fail closed on all ambiguous patches."""
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from apply_1915_print_deltas import apply_operations, validate_decisions

N="http://www.tei-c.org/ns/1.0"
def root():
    return ET.fromstring(f'''<TEI xmlns="{N}"><text><body>
      <div type="entry" n="AALAR" xml:id="aalar"><head type="index" xml:id="aalar-head">AALAR</head>
      <p xml:id="p-aalar">a'-a-lar. See <ref xml:id="ref1" type="article"
      n="ISBE:ALTAR" target="#altar">ALTAR</ref>.</p></div>
      <div type="entry" n="ALTAR" xml:id="altar"><head xml:id="altar-head">ALTAR</head><p xml:id="p-altar">Old.</p></div>
      <div type="entry" n="ALLAR" xml:id="allar"><head xml:id="allar-head">ALLAR</head><p xml:id="p-allar">Actual.</p></div>
    </body></text></TEI>''')
def spec():
    return [{"operation":"replace_article_ref","source_key":"AALAR",
             "source_unit_xml_id":"p-aalar","original_visible":"ALTAR","printed_visible":"ALLAR",
             "original_target_key":"ALTAR","printed_target_key":"ALLAR",
             "approved_for_separate_editorial_tei":True,"rationale":"Original 1915 print"}]

class PrintDeltasTests(unittest.TestCase):
    def test_only_original_referenced_element_changes(self):
        xml=root()
        bodies=list(xml.find(f"./{{{N}}}text/{{{N}}}body"))
        before=[ET.tostring(x) for x in bodies]
        changed,ledger=apply_operations(xml,spec())
        after=[ET.tostring(x) for x in bodies]
        self.assertEqual(changed,{"AALAR"})
        self.assertEqual(len(ledger),1)
        self.assertNotEqual(after[0],before[0])
        self.assertEqual(after[1:],before[1:])
        ref=xml.find(f".//{{{N}}}ref")
        self.assertEqual(ref.text,"ALLAR")
        self.assertEqual(ref.get("target"),"#allar")
        self.assertEqual(ref.get("n"),"ISBE:ALTAR")
        self.assertEqual(ledger[0]["original_active_target"],"#altar")

    def test_original_reading_and_active_destination_are_preconditions(self):
        for field,val in [("original_visible","ARALT"),("original_target_key","ALLAR"),
                          ("source_unit_xml_id","wrong")]:
            d=spec()
            d[0][field]=val
            with self.assertRaises(ValueError):
                apply_operations(root(),d)

    def test_no_unapproved_or_duplicate_edits(self):
        d=spec()
        d[0]["approved_for_separate_editorial_tei"]=False
        with self.assertRaisesRegex(ValueError,"Unreviewed"):
            apply_operations(root(),d)
        d=spec()
        with self.assertRaisesRegex(ValueError,"Repeated"):
            apply_operations(root(),d+d)

if __name__=="__main__":
    unittest.main()
