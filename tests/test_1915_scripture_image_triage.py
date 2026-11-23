"""Review-ledger fidelity controls for original 1915 print-image triage."""
import json
import unittest
from pathlib import Path
from scripts.audit_scripture_ref_display import scan

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"workspace/reviews/1915-scripture-reference-image-triage-v1.json"

class OriginalPrintCandidateLedgerTests(unittest.TestCase):
    def test_complete_canonical_coverage_and_sources(self):
        d=json.loads(LEDGER.read_text(encoding="utf-8"))
        report=scan(ROOT/"cleaned/en/ISBE.xml")
        self.assertEqual(d["canonical_sha256"],report["input_sha256"])
        self.assertEqual(report["candidate_count"],13)
        self.assertFalse(d["publication_permitted"])
        self.assertFalse(d["canonical_modified"])
        by_id={x["ref_xml_id"]:x for x in report["cases"]}
        rows=d["cases"]
        self.assertEqual(len(rows),13)
        self.assertEqual({x["ref_xml_id"] for x in rows},set(by_id))
        from scripts.research_1915_print_pages import expected_volume
        manifest=json.loads((ROOT/"sources/print/1915-volume-witnesses.json").read_text())
        pdfs={v["volume"]:v["pdf_sha256"] for v in manifest["volumes"]}
        for r in rows:
            baseline=by_id[r["ref_xml_id"]]
            self.assertEqual((r["source_key"],r["visible"],r["original_cRef"]),
                             (baseline["article_key"],baseline["visible"],baseline["cRef"]))
            self.assertEqual(r["print_volume"],expected_volume(r["source_key"]))
            self.assertEqual(r["source_pdf_sha256"],pdfs[r["print_volume"]])
            self.assertEqual(r["approval"],"research_only_no_edit")
            if r["disposition"]=="visually_attested_candidate":
                self.assertIsInstance(r["pdf_page_1_based"],int)
                self.assertRegex(r["source_image_jpeg_sha256"],r"^[a-f0-9]{64}$")
                self.assertTrue(r["source_image_workflow_run"])
                self.assertTrue(r["proposed_cRef"].startswith("Bible:"))
                self.assertNotEqual(r["original_cRef"],r["proposed_cRef"])
            else:
                self.assertEqual(r["disposition"],"unresolved_no_adequate_print_page")
                self.assertIsNone(r["proposed_cRef"])
                self.assertIsNone(r["source_image_jpeg_sha256"])
        self.assertEqual(sum(r["disposition"]=="visually_attested_candidate" for r in rows),12)
        self.assertEqual([r["source_key"] for r in rows if r["proposed_cRef"] is None],["TAANACH"])

if __name__=="__main__":
    unittest.main()
