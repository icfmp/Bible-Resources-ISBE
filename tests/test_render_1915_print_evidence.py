"""Guard historical image evidence against wrong source or page ranges."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.render_1915_print_evidence import render_pages
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]

class SourcePrintImageTests(unittest.TestCase):
    def test_all_original_witness_files_are_pinned(self):
        manifest=json.loads((ROOT/"sources/print/1915-volume-witnesses.json").read_text())
        self.assertEqual(len(manifest["volumes"]),5)
        for v in manifest["volumes"]:
            self.assertEqual(len(v["pdf_sha256"]),64)
            self.assertFalse(v["print_page_images_reviewed"])

    def test_fake_source_rejected_before_render(self):
        with tempfile.TemporaryDirectory() as d:
            fake=Path(d)/"wrong.pdf"
            fake.write_bytes(b"%PDF-1.4\nfake")
            with self.assertRaisesRegex(ValueError,"sha256"):
                render_pages(fake,"5",[67],ROOT/"sources/print/1915-volume-witnesses.json")
    def test_requested_page_must_be_inside_actual_volume(self):
        with tempfile.TemporaryDirectory() as d:
            fake=Path(d)/"wrong.pdf"
            fake.write_bytes(b"%PDF-1.4\nfake")
            with self.assertRaisesRegex(ValueError,"sha256"):
                render_pages(fake,"1",[9999],ROOT/"sources/print/1915-volume-witnesses.json")

if __name__=="__main__":
    unittest.main()
