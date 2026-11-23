"""Regression guards for retained original+historical-cleaned ISBE sources."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch
from scripts import persist_1915_cleaned_master as master

class HistoricalSourceRetentionTests(unittest.TestCase):
    def test_exact_source_and_edited_hashes_are_not_interchangeable(self):
        self.assertEqual(master.CANONICAL_SHA,"a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25")
        self.assertEqual(master.ORIGINAL_ZIP_SHA,"4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32")
        self.assertEqual(master.EXPECTED_CLEANED_SHA,"5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c")
        self.assertEqual(len({master.CANONICAL_SHA,master.ORIGINAL_ZIP_SHA,master.EXPECTED_CLEANED_SHA}),3)
        self.assertNotEqual(master.CANONICAL,master.CLEANED_DIR/"ISBE.xml")
        self.assertEqual(master.SOURCE_ZIP,master.ORIGINAL_DIR/"ISBE.zip")

    def test_no_original_source_can_be_accepted_with_wrong_sha(self):
        with TemporaryDirectory() as temp:
            p=Path(temp)
            (p/"ISBE.zip").write_bytes(b"forged archive")
            (p/"ISBE.xml").write_text("<TEI/>",encoding="utf-8")
            (p/"MANIFEST.json").write_text(json.dumps({
               "archive_sha256":master.ORIGINAL_ZIP_SHA,
               "archive_bytes":len(b"forged archive")}))
            with patch.object(master,"SOURCE_ZIP",p/"ISBE.zip"), \
                 patch.object(master,"CANONICAL",p/"ISBE.xml"), \
                 patch.object(master,"SOURCE_MANIFEST",p/"MANIFEST.json"):
                with self.assertRaises(ValueError):
                    master.check_source()

    def test_final_edition_is_never_auto_approved_for_release(self):
        # The two manifests are materialized only by the explicit validated
        # production pipeline. Tests exercise them whenever present.
        provenance=master.ORIGINAL_DIR/"PROVENANCE.json"
        report=master.CLEANED_DIR/"CLEANUP_MANIFEST.json"
        if not provenance.exists() or not report.exists():
            self.skipTest("Source masters have not yet been staged by retention workflow")
        a=json.loads(provenance.read_text(encoding="utf-8"))
        b=json.loads(report.read_text(encoding="utf-8"))
        self.assertFalse(b["publication_permitted"])
        self.assertFalse(b["rights_redistribution_cleared"])
        self.assertFalse(b["modernized"])
        self.assertEqual(a["sha256"],master.ORIGINAL_ZIP_SHA)
        self.assertEqual(b["cleaned_sha256"],master.EXPECTED_CLEANED_SHA)
        self.assertTrue(master.verify_saved())

if __name__=="__main__":
    unittest.main()
