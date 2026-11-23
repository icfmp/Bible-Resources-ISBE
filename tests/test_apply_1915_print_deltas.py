"""Reversible exact-reference print edits; fail closed on all ambiguous patches."""
import copy
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
        changed,ledger,added_ids=apply_operations(xml,spec())
        after=[ET.tostring(x) for x in bodies]
        self.assertEqual(changed,{"AALAR"})
        self.assertEqual(len(ledger),1)
        self.assertEqual(added_ids,set())
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


    def test_reject_modified_facsimile_digest(self):
        import json
        from pathlib import Path
        root_path = Path(__file__).resolve().parents[1]
        delta = json.loads((root_path / "workspace/reviews/1915-approved-print-deltas-v1.json")
                           .read_text(encoding="utf-8"))
        evidence = json.loads((root_path / "workspace/reviews/1915-nonempty-contrast-v1.json")
                              .read_text(encoding="utf-8"))
        self.assertEqual(validate_decisions(delta,evidence),1)
        tampered = copy.deepcopy(delta)
        tampered["decisions"][0]["evidence_rendered_jpeg_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"Unverified"):
            validate_decisions(tampered,evidence)
        tampered = copy.deepcopy(evidence)
        case = next(c for c in tampered["cases"] if c["source_key"]=="AALAR")
        case["original_pdf_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"Unverified"):
            validate_decisions(delta,tampered)


    def test_multiple_exact_prose_corrections_in_one_article(self):
        xml=ET.fromstring(f'''<TEI xmlns="{N}"><text><body><div type="entry" n="AARON"
            xml:id="aaron"><p xml:id="p-aaron">Moses hands: Yahweh had called them.
            <ref xml:id="rr" cRef="Bible:Exod.4.27" type="scripture">Ex 4:27</ref>.</p>
            </div><div type="entry" n="OTHER" xml:id="other">
            <p xml:id="other-p">Unrelated article</p></div></body></text></TEI>''')
        other=xml.find(f".//{{{N}}}div[@n='OTHER']")
        old_other=ET.tostring(other)
        edits=[
            {"operation":"replace_text_span","source_key":"AARON",
             "source_unit_xml_id":"p-aaron","original_visible":"Yahweh had called them",
             "printed_visible":"Jehovah had called them",
             "approved_for_separate_editorial_tei":True},
            {"operation":"replace_text_span","source_key":"AARON",
             "source_unit_xml_id":"p-aaron","original_visible":"Moses hands",
             "printed_visible":"Moses' hands",
             "approved_for_separate_editorial_tei":True},
        ]
        changed,records,added=apply_operations(xml,edits)
        self.assertEqual(changed,{"AARON"})
        self.assertEqual(len(records),2)
        self.assertFalse(added)
        p=xml.find(f".//{{{N}}}p[@xml:id='p-aaron']") if False else list(xml.iter(f"{{{N}}}p"))[0]
        self.assertIn("Moses' hands: Jehovah had called them", "".join(p.itertext()))
        self.assertEqual(ET.tostring(other),old_other)
        with self.assertRaisesRegex(ValueError,"Repeated"):
            apply_operations(root(),spec()+spec())

    def test_three_references_restore_two_new_stable_ids(self):
        xml=ET.fromstring(f'''<TEI xmlns="{N}"><text><body>
          <div type="entry" n="AB (1)" xml:id="ab">
            <p xml:id="ab-p">Used three times (<ref xml:id="old-ref"
             cRef="Bible:Mark.4.6" type="scripture">Mr 4:6</ref>), and elsewhere.</p>
          </div></body></text></TEI>''')
        row={"operation":"replace_scripture_ref_series",
             "source_key":"AB (1)","source_unit_xml_id":"ab-p","source_ref_xml_id":"old-ref",
             "original_visible":"Mr 4:6","original_c_ref":"Bible:Mark.4.6",
             "printed_visible":"Mk 14:36; Rom 8:15; Gal 4:6",
             "replacements":[
                {"visible":"Mk 14:36","cRef":"Bible:Mark.14.36"},
                {"visible":"Rom 8:15","cRef":"Bible:Rom.8.15"},
                {"visible":"Gal 4:6","cRef":"Bible:Gal.4.6"}],
             "approved_for_separate_editorial_tei":True}
        changed,records,added=apply_operations(xml,[row])
        self.assertEqual(changed,{"AB (1)"})
        self.assertEqual(added,{"old-ref-print-001","old-ref-print-002"})
        self.assertEqual(len(records),1)
        p=list(xml.iter(f"{{{N}}}p"))[0]
        refs=list(p.iter(f"{{{N}}}ref"))
        self.assertEqual([r.get("{http://www.w3.org/XML/1998/namespace}id") for r in refs],
                         ["old-ref","old-ref-print-001","old-ref-print-002"])
        self.assertEqual([r.get("cRef") for r in refs],
                         ["Bible:Mark.14.36","Bible:Rom.8.15","Bible:Gal.4.6"])
        self.assertEqual("".join(p.itertext()),
                         "Used three times (Mk 14:36; Rom 8:15; Gal 4:6), and elsewhere.")
        broken=copy.deepcopy(row)
        broken["original_c_ref"]="Bible:Mark.14.36"
        with self.assertRaisesRegex(ValueError,"reference or target mismatch"):
            apply_operations(ET.fromstring(f'''<TEI xmlns="{N}"><text><body>
              <div n="AB (1)" xml:id="ab"><p xml:id="ab-p"><ref xml:id="old-ref"
              cRef="Bible:Mark.4.6" type="scripture">Mr 4:6</ref></p></div>
              </body></text></TEI>'''),[broken])

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
