import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.audit_1915_scripture_candidates import attach_ocr_hints

class HistoricalPrintTriageTests(unittest.TestCase):
    def test_requires_exact_manifest_digest_before_ocr(self):
        import json
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            pdf = d / "v.pdf"
            pdf.write_bytes(b"%PDF-fake")
            m = d / "manifest.json"
            m.write_text(json.dumps({
                "canonical_tei_sha256": "a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25",
                "volumes": [{"volume": "2", "pdf_sha256": "wrong", "pages": 739}]
            }))
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                attach_ocr_hints({"cases": []}, pdf, m, "2")

    def test_rejects_mismatched_canonical_lock(self):
        import json
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            pdf = d / "v.pdf"
            pdf.write_bytes(b"%PDF-fake")
            m = d / "manifest.json"
            m.write_text(json.dumps({"canonical_tei_sha256": "wrong", "volumes": []}))
            with self.assertRaisesRegex(ValueError, "manifest mismatch"):
                attach_ocr_hints({"cases": []}, pdf, m, "2")


if __name__ == "__main__":
    unittest.main()
