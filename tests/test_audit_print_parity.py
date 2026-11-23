"""Regression controls for source-locked comparison of existing ISBE entries."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit_print_parity import check

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"cleaned/en/ISBE.xml"
LEDGER=ROOT/"workspace/reviews/1915-nonempty-contrast-v1.json"

class PrintParityTests(unittest.TestCase):
    def test_exact_aaron_source_readings_located(self):
        original=SOURCE.read_bytes()
        result=check(SOURCE,LEDGER)
        self.assertEqual(result["article_count"],9380)
        self.assertEqual(result["case_count"],3)
        self.assertEqual(result["approved_change_count"],0)
        self.assertEqual({r["source_key"] for r in result["cases"]},{"AARON","AALAR"})
        self.assertEqual(len({r["unit_xml_id"] for r in result["cases"]}),3)
        self.assertEqual(SOURCE.read_bytes(),original)

    def test_reject_source_drift(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"wrong.xml"
            p.write_text("<TEI/>",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"digest"):
                check(p,LEDGER)

    def test_reject_unapproved_changes_and_unknown_status(self):
        with tempfile.TemporaryDirectory() as d:
            for field,value,message in (("approved",True,"cannot authorize"),
                                        ("review_status","print_certified","overstated")):
                data=json.loads(LEDGER.read_text(encoding="utf-8"))
                data["cases"][0][field]=value
                p=Path(d)/"changed.json"
                p.write_text(json.dumps(data),encoding="utf-8")
                with self.assertRaisesRegex(ValueError,message):
                    check(SOURCE,p)

if __name__=="__main__":
    unittest.main()
