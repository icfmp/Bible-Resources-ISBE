"""Negative controls and precise preservation for provisional ISBE redirects."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from scripts.preview_legacy_redirects import preview, Q, XMLID

class RedirectPreviewTests(unittest.TestCase):
    def test_real_corpus_preview_is_lossless_outside_approved_scope(self):
        root=Path(__file__).resolve().parents[1]
        source=root/"cleaned/en/ISBE.xml"
        before=hashlib.sha256(source.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"preview.xml"
            report=Path(tmp)/"report.json"
            result=preview(source,root/"workspace/reviews/redirect-candidate-v1.json",output,report)
            self.assertEqual(result["changed_articles"],10)
            self.assertEqual(result["untouched_articles_verified"],9370)
            self.assertTrue(result["original_ids_preserved"])
            self.assertTrue(result["noncanonical"])
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)
            self.assertTrue(report.is_file())
            self.assertEqual(len(ET.parse(output).getroot().find("./"+Q("text")+"/"+Q("body"))),9380)

    def test_rejects_unapproved_source_digest(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            manifest=json.loads((root/"workspace/reviews/redirect-candidate-v1.json").read_text())
            manifest["canonical_sha256"]="0"*64
            mf=Path(tmp)/"invalid.json"
            mf.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                preview(root/"cleaned/en/ISBE.xml",mf,Path(tmp)/"out.xml",Path(tmp)/"report.json")

if __name__=="__main__":
    unittest.main()
