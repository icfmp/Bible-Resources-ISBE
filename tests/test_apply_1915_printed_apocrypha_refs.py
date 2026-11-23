"""Exact original-1915 GAINSAY AddEsth reference proof, rollback and fail-closed tests."""
import copy
import hashlib
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from scripts.apply_1915_printed_apocrypha_refs import (
    apply, read, validate_ledger, index, LOCK
)

ROOT=Path(__file__).resolve().parents[1]


class PrintedApocryphaReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=read(ROOT/"workspace/reviews/1915-gainsay-additions-esther-reference-v1.json")
        cls.witness=read(ROOT/"sources/print/1915-volume-witnesses.json")
        cls.canonical=ET.parse(ROOT/"cleaned/en/ISBE.xml").getroot()

    def rejects(self, change):
        data=copy.deepcopy(self.spec)
        change(data)
        with self.assertRaises(ValueError):
            validate_ledger(data,self.witness,self.canonical)

    def test_original_print_and_crosswire_wrong_esther_location(self):
        rows=validate_ledger(self.spec,self.witness,self.canonical)
        self.assertEqual(len(rows),1)
        d=rows[0]
        self.assertEqual(d["print_reading"],"Ad Est 13 9")
        self.assertEqual(d["source_ref_original_cRef"],"Bible:Esth.9.13")
        self.assertEqual(d["source_ref_new_cRef"],"Bible:AddEsth.13.9")
        self.assertFalse(self.spec["redistribution_authorized"])

    def test_exact_reversal_on_original_prior_paragraph_without_other_changes(self):
        # Stand-in reproducing the previous *printed-stage paragraph* while
        # the workflow validates the genuine 36MB prior TEI SHA and whole file.
        root=ET.parse(ROOT/"cleaned/en/ISBE.xml").getroot()
        article=index(root)["GAINSAY"]
        para=next(p for p in article if p.get("{http://www.w3.org/XML/1998/namespace}id")==
                 self.spec["decisions"][0]["source_paragraph_xml_id"])
        oldref=next(c for c in para if c.get("{http://www.w3.org/XML/1998/namespace}id")==
                    self.spec["decisions"][0]["preceding_ref_xml_id"])
        oldref.tail=self.spec["decisions"][0]["preceding_ref_original_tail"]
        self.assertEqual(
            hashlib.sha256("".join(para.itertext()).encode()).hexdigest(),
            self.spec["decisions"][0]["previous_paragraph_text_sha256"]
        )
        original=ET.tostring(article,encoding="utf-8")
        unchanged=ET.tostring(index(root)["REPAIR"],encoding="utf-8")
        affected,records=apply(root,self.spec["decisions"])
        self.assertEqual(affected,{"GAINSAY"})
        self.assertEqual(len(records),1)
        updated=index(root)["GAINSAY"]
        self.assertIn("Ad Est 13 9", "".join(updated.itertext()))
        self.assertNotIn("Additions to  Esther 9:13", "".join(updated.itertext()))
        self.assertEqual(ET.tostring(index(root)["REPAIR"],encoding="utf-8"),unchanged)
        ref=next(n for n in updated.iter() if n.get("{http://www.w3.org/XML/1998/namespace}id")==
                 self.spec["decisions"][0]["source_ref_xml_id"])
        self.assertEqual(ref.get("cRef"),"Bible:AddEsth.13.9")
        self.assertNotEqual(ET.tostring(updated,encoding="utf-8"),original)

    def test_reject_false_release_or_crosswire_overwrite(self):
        self.rejects(lambda d:d.update(redistribution_authorized=True))
        self.rejects(lambda d:d.update(original_canonical_unchanged=False))
        self.rejects(lambda d:d.update(full_1915_historical_article_collation_certified=True))

    def test_reject_verse_target_and_source_quote_drift(self):
        self.rejects(lambda d:d["decisions"][0].update(source_ref_original_cRef="Bible:AddEsth.13.9"))
        self.rejects(lambda d:d["decisions"][0].update(source_ref_xml_id="invented"))
        self.rejects(lambda d:d["decisions"][0].update(pdf_page=504))
        self.rejects(lambda d:d.update(witness_pdf_sha256="0"*64))
        self.rejects(lambda d:d.update(witness_jpeg_sha256="abc"))

    def test_reject_mass_versification_change_and_duplicate_item(self):
        self.rejects(lambda d:d["decisions"][0].update(operation="replace_globally"))
        self.rejects(lambda d:d["decisions"].append(copy.deepcopy(d["decisions"][0])))


if __name__=="__main__":
    unittest.main()
