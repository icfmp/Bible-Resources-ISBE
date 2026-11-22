"""Trace 1915 print-image observations to exact original source paragraphs."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT/"workspace/reviews/1915-visual-page-collation-v1.json"
LEDGER = ROOT/"workspace/reviews/empty-article-recovery-ledger.json"
VOLUMES = ROOT/"sources/print/1915-volume-witnesses.json"
CANONICAL = ROOT/"cleaned/en/ISBE.xml"

class PrintedPageCollationTests(unittest.TestCase):
    def test_all_twenty_one_visual_observations_are_source_locked_and_reversible(self):
        data=json.loads(REVIEW.read_text(encoding="utf-8"))
        baseline=json.loads(LEDGER.read_text(encoding="utf-8"))
        volumes={v["volume"]:v for v in json.loads(VOLUMES.read_text(encoding="utf-8"))["volumes"]}
        source_sha=hashlib.sha256(CANONICAL.read_bytes()).hexdigest()
        self.assertEqual(data["sample_size"],21)
        self.assertEqual(data["visual_page_inspected_count"],21)
        self.assertEqual(data["complete_article_transcriptions_certified"],0)
        self.assertTrue(data["no_canonical_change"])
        self.assertEqual(source_sha,data["canonical_source_sha256"])
        self.assertEqual(source_sha,baseline["baseline_canonical_tei_sha256"])
        by_key={row["source_key"]:row for row in baseline["cases"]}
        self.assertEqual(len(data["records"]),len({r["source_key"] for r in data["records"]}))
        for row in data["records"]:
            with self.subTest(key=row["source_key"]):
                key=row["source_key"]
                entry=by_key[key]
                self.assertEqual(row["original_source_paragraph_xml_id"],entry["paragraph_xml_id"])
                self.assertTrue(row["visual_page_inspected"])
                self.assertFalse(row["all_text_punctuation_and_foreign_script_certified"])
                self.assertFalse(row["canonical_modification_approved"])
                self.assertTrue(entry["print_image_reviewed"])
                self.assertFalse(entry["source_recovery_approved"])
                self.assertFalse(entry["print_transcription_fully_certified"])
                self.assertEqual(entry["printed_page"],row["printed_page_number"])
                self.assertEqual(entry["scan_page"],row["pdf_page_1_based"])
                self.assertEqual(str(entry["print_volume"]),row["scan_volume"])
                self.assertEqual(row["original_pdf_sha256"],volumes[row["scan_volume"]]["pdf_sha256"])
                self.assertTrue(0 < row["pdf_page_1_based"] <= volumes[row["scan_volume"]]["pages"])
                self.assertEqual(len(row["rendered_jpeg_sha256"]),64)
                self.assertTrue(row["observed_print_fact"].strip())

    def test_six_ocr_misses_now_have_source_image_verified_print_locations(self):
        mapping=json.loads((ROOT/"workspace/reviews/1915-printed-headword-ocr-locations.json").read_text(encoding="utf-8"))
        by_key={row["source_key"]:row for row in mapping["cases"]}
        expected={
            "ASTARTE; ASTORETH":(1,329,295),
            "CHORBE":(1,654,614),
            "JOSIBIAH":(3,393,1753),
            "PATRIARCHS, TESTAMENTS OF THE TWELVE":(4,176,2264),
            "REGENERATION, BAPTISMAL":(4,466,2550),
            "THOCANUS":(5,169,2973),
        }
        self.assertEqual(mapping["located_heading_evidence_total"],31)
        self.assertEqual(mapping["ocr_unlocated_keys_resolved_by_original_print_visual_inspection"],6)
        self.assertEqual(mapping["strict_ocr_locations_found"],25)
        for key,(volume,pdf_page,folio) in expected.items():
            with self.subTest(key=key):
                row=by_key[key]
                self.assertIsNone(row["pdf_page_1_based"])
                self.assertTrue(row["visually_verified_heading"])
                self.assertEqual(row["expected_print_volume"],str(volume))
                self.assertEqual(row["visual_heading_page_1_based"],pdf_page)
                self.assertEqual(row["visual_print_folio_page"],folio)
                self.assertFalse(row["print_witness_excerpt_certified"])

    def test_recovered_candidates_apply_only_reversible_print_observations(self):
        redirects=json.loads((ROOT/"workspace/reviews/redirect-candidate-v1.json").read_text(encoding="utf-8"))
        prose=json.loads((ROOT/"workspace/reviews/print-prose-candidate-v1.json").read_text(encoding="utf-8"))
        rr={r["article_key"]:r for r in redirects["records"]}
        pp={r["source_key"]:r for r in prose["records"]}
        self.assertEqual(rr["JOSIBIAH"]["proposed_print_collated_text"],"jos-i-bi'a. See JOSHIBIAH.")
        self.assertEqual(rr["PATRIARCHS, TESTAMENTS OF THE TWELVE"]["proposed_print_collated_text"],
                         "See APOCALYPTIC LITERATURE, IV, 1.")
        self.assertIn("ASTORETH. See ASHTAROTH.",rr["ASTARTE; ASTORETH"]["proposed_print_collated_text"])
        self.assertFalse(any(r["approved"] for r in redirects["records"]))
        self.assertIn("Χορβέ",pp["CHORBE"]["blocks"][0])
        self.assertNotIn("vits>",pp["SEPHARVITES"]["blocks"][0])
        self.assertIn("AV is a transcription",pp["SYCHEM"]["blocks"][0])
        self.assertIn("Θόκανος",pp["THOCANUS"]["blocks"][0])
        self.assertIn('margin "is."',pp["FROWARDNESS"]["blocks"][0])
        for key in ("CHORBE","SEPHARVITES","SYCHEM","THOCANUS","FROWARDNESS"):
            self.assertTrue(pp[key]["print_image_reviewed"])
            self.assertFalse(pp[key]["approved"])
            self.assertFalse(pp[key]["print_text_fully_certified"])

if __name__=="__main__":
    unittest.main()
