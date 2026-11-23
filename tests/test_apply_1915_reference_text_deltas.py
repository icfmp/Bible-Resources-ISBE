"""Regression and fail-closed controls for source-image-backed Scripture prose repairs."""
import copy
from hashlib import sha256
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.apply_1915_reference_text_deltas import (
    apply_deltas, validate_decisions,
)

ROOT = Path(__file__).resolve().parents[1]
T = "{http://www.tei-c.org/ns/1.0}"
ID = "{http://www.w3.org/XML/1998/namespace}id"


def fixture():
    root = ET.fromstring("""<TEI xmlns="http://www.tei-c.org/ns/1.0">
      <text><body>
        <div n="ESCHATOLOGY OF THE OLD TESTAMENT" xml:id="a">
          <p xml:id="p">A <ref xml:id="first" type="scripture"
            cRef="Bible:Zeph.3.13">Ze 3:13</ref>,<ref xml:id="next"
            type="scripture" cRef="Bible:Zech.3.10">10</ref>, etc.</p>
        </div><div n="UNRELATED" xml:id="b"><p xml:id="b-p">Preserve.</p></div>
      </body></text></TEI>""")
    paragraph = next(root.iter(T + "p"))
    original = "".join(paragraph.itertext())
    row = {
        "source_key": "ESCHATOLOGY OF THE OLD TESTAMENT",
        "source_unit_xml_id": "p",
        "source_unit_text_sha256": sha256(original.encode()).hexdigest(),
        "preceding_ref_xml_id": "first", "preceding_ref_visible": "Ze 3:13",
        "preceding_ref_cRef": "Bible:Zeph.3.13", "preceding_ref_tail": ",",
        "source_ref_xml_id": "next", "original_visible": "10",
        "corrected_visible": "20",
        "original_cRef": "Bible:Zech.3.10",
        "corrected_cRef": "Bible:Zeph.3.20",
    }
    return root, row


class PrintReferenceTextDeltaTests(unittest.TestCase):
    def test_exact_ref_text_and_target_change_only(self):
        root, row = fixture()
        unchanged = ET.tostring(next(a for a in root.iter(T + "div")
                                     if a.get("n") == "UNRELATED"))
        changed, records = apply_deltas(root, [row])
        self.assertEqual(changed, {"ESCHATOLOGY OF THE OLD TESTAMENT"})
        self.assertEqual(len(records), 1)
        para = next(root.iter(T + "p"))
        self.assertEqual("".join(para.itertext()), "A Ze 3:13,20, etc.")
        refs = list(para)
        self.assertEqual(refs[0].text, "Ze 3:13")
        self.assertEqual(refs[0].tail, ",")
        self.assertEqual(refs[1].text, "20")
        self.assertEqual(refs[1].get("cRef"), "Bible:Zeph.3.20")
        self.assertEqual(ET.tostring(next(a for a in root.iter(T + "div")
                                      if a.get("n") == "UNRELATED")), unchanged)
        with self.assertRaises(ValueError):
            apply_deltas(root, [row])

    def test_drift_and_incorrect_segmentation_fail_closed(self):
        root, row = fixture()
        for field, value in (("source_unit_text_sha256", "0"*64),
                             ("source_ref_xml_id", "other"),
                             ("preceding_ref_tail", ";"),
                             ("original_cRef", "Bible:Zech.3.20"),
                             ("original_visible", "11")):
            bad = copy.deepcopy(row)
            bad[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                apply_deltas(copy.deepcopy(root), [bad])

    def test_original_historical_image_ledger_provenance_required(self):
        spec = json.loads((ROOT / "workspace/reviews/1915-approved-reference-text-deltas-v1.json")
                          .read_text(encoding="utf-8"))
        evidence = json.loads((ROOT / spec["source_image_ledger"])
                              .read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / spec["original_1915_witness_manifest"])
                              .read_text(encoding="utf-8"))
        self.assertEqual(len(validate_decisions(spec, evidence, manifest)), 1)
        for field, value in (("print_jpeg_sha256", "0"*64),
                             ("print_pdf_sha256", "0"*64),
                             ("source_image_job_id", 99),
                             ("print_reading", "Zeph 3 13.10"),
                             ("approved_for_separate_editorial_tei", False)):
            bad = copy.deepcopy(spec)
            bad["decisions"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_decisions(bad, evidence, manifest)
        bad = copy.deepcopy(spec)
        bad["decisions"] = bad["decisions"] * 2
        with self.assertRaisesRegex(ValueError, "Repeated"):
            validate_decisions(bad, evidence, manifest)
        bad = copy.deepcopy(spec)
        bad["publication_permitted"] = True
        with self.assertRaisesRegex(ValueError, "Unrecognized"):
            validate_decisions(bad, evidence, manifest)


if __name__ == "__main__":
    unittest.main()
