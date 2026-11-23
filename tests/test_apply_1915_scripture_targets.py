"""Negative controls for isolated, source-locked Scripture-target edits."""
import copy
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.apply_1915_scripture_targets import apply_target_changes, validate_ledger

N="http://www.tei-c.org/ns/1.0"
ROOT=Path(__file__).resolve().parents[1]

def fixture():
    return ET.fromstring(f'''<TEI xmlns="{N}"><text><body>
    <div n="A" xml:id="a"><p xml:id="p1">First <ref xml:id="r1" type="scripture"
    cRef="Bible:Zech.3.2">Ze 2:15</ref> after.</p></div>
    <div n="B" xml:id="b"><p xml:id="p2">Leave unchanged.</p></div>
    </body></text></TEI>''')

def choice():
    return {"source_key":"A","unit_xml_id":"p1","ref_xml_id":"r1",
            "visible":"Ze 2:15","original_cRef":"Bible:Zech.3.2",
            "proposed_cRef":"Bible:Zeph.2.15","print_volume":"1",
            "pdf_page_1_based":618,"source_pdf_sha256":"a"*64,
            "source_image_jpeg_sha256":"b"*64}

class SourceBackedNavigationTests(unittest.TestCase):
    def test_single_target_preserves_visible_text(self):
        # The complete production ledger has twelve distinct rows. For a
        # minimal fixture, create distinct references and source anchors.
        root=fixture()
        a=choice()
        # A small unit test exercises one exact operation using a mock set
        # of 12 distinct independent records in the same paragraph.
        p=root.find(f".//{{{N}}}p[@{{http://www.w3.org/XML/1998/namespace}}id='p1']")
        for i in range(2,13):
            ref=ET.SubElement(p,f"{{{N}}}ref",{
                "{http://www.w3.org/XML/1998/namespace}id":f"r{i}",
                "type":"scripture","cRef":"Bible:Zech.3.2"})
            ref.text="Ze 2:15"
        rows=[dict(a,ref_xml_id=f"r{i}") for i in range(1,13)]
        before="".join(root.itertext())
        changed,records=apply_target_changes(root,rows)
        self.assertEqual(changed,{"A"})
        self.assertEqual(len(records),12)
        self.assertEqual("".join(root.itertext()),before)
        self.assertEqual({n.get("cRef") for n in root.iter(f"{{{N}}}ref")},{"Bible:Zeph.2.15"})
        with self.assertRaisesRegex(ValueError,"drift"):
            apply_target_changes(root,rows)

    def test_ledger_unresolved_case_refuses_approval(self):
        d=json.loads((ROOT/"workspace/reviews/1915-scripture-reference-image-triage-v1.json").read_text())
        m=json.loads((ROOT/"workspace/witnesses/print/1915-volume-witnesses.json").read_text())
        self.assertEqual(len(validate_ledger(d,m)),12)
        bad=copy.deepcopy(d)
        next(x for x in bad["cases"] if x["source_key"]=="TAANACH")["proposed_cRef"]="Bible:Judg.1.27"
        with self.assertRaisesRegex(ValueError,"must not be edited"):
            validate_ledger(bad,m)
        bad=copy.deepcopy(d)
        bad["cases"][0]["source_image_jpeg_sha256"]="bad"
        with self.assertRaisesRegex(ValueError,"page evidence"):
            validate_ledger(bad,m)
        bad=copy.deepcopy(d)
        bad["cases"][0]["source_pdf_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"PDF digest"):
            validate_ledger(bad,m)

if __name__=="__main__":
    unittest.main()
