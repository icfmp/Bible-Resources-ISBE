"""Source-tree invariants: one original, one edited master, no fake SWORD module."""
from hashlib import sha256
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"sources/original/encyclopedias/en/isbe-crosswire-2.2"
CLEANED=ROOT/"sources/cleaned/encyclopedias/en/isbe-1915"
WITNESS=ROOT/"workspace/witnesses/crosswire-2.2"

def digest(path):
    result=sha256()
    with path.open("rb") as source:
        for block in iter(lambda:source.read(1024*1024),b""):
            result.update(block)
    return result.hexdigest()

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

class CleanSourceTreeTests(unittest.TestCase):
    def test_all_original_witness_and_editorial_bytes_are_exact(self):
        self.assertEqual(digest(ORIGINAL/"ISBE.zip"),"4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32")
        self.assertEqual(digest(WITNESS/"ISBE.xml"),"a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25")
        self.assertEqual(digest(CLEANED/"ISBE.xml"),"5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c")
        self.assertEqual(digest(WITNESS/"article-index.json"),"bdfa352af5b372874e6d2578e86ebae38a70efb64489a91e8985f3b09f2e18e1")

    def test_paths_and_rights_match_pinned_original_and_edited_manifests(self):
        acquired=read_json(ORIGINAL/"ACQUISITION_MANIFEST.json")
        provenance=read_json(ORIGINAL/"PROVENANCE.json")
        edited=read_json(CLEANED/"CLEANUP_MANIFEST.json")
        self.assertEqual(acquired["archive_sha256"],digest(ORIGINAL/"ISBE.zip"))
        self.assertEqual(provenance["source_path"],(ORIGINAL/"ISBE.zip").relative_to(ROOT).as_posix())
        self.assertEqual(provenance["source_manifest_path"],(ORIGINAL/"ACQUISITION_MANIFEST.json").relative_to(ROOT).as_posix())
        self.assertEqual(edited["source_faithful_canonical_path"],(WITNESS/"ISBE.xml").relative_to(ROOT).as_posix())
        self.assertEqual(edited["source_article_index_path"],(WITNESS/"article-index.json").relative_to(ROOT).as_posix())
        self.assertEqual(edited["original_module_sha256"],acquired["archive_sha256"])
        self.assertEqual(edited["cleaned_sha256"],digest(CLEANED/"ISBE.xml"))
        self.assertEqual(edited["article_count"],9380)
        self.assertFalse(edited["publication_permitted"])
        self.assertFalse(edited["rights_redistribution_cleared"])

    def test_no_legacy_source_roots_or_duplicated_original(self):
        for path in ("cleaned","modern","translations","sources/crosswire","sources/print"):
            self.assertFalse((ROOT/path).exists(),path)
        self.assertEqual(len(list((ROOT/"sources").rglob("ISBE.zip"))),1)

    def test_module_staging_is_not_falsely_presented_as_compiled_or_published(self):
        folder=ROOT/"modules/isbe-1915"
        record=read_json(folder/"metadata.json")
        self.assertFalse((folder/"payload").exists())
        self.assertEqual(record["category"],"encyclopedia")
        self.assertEqual(record["origin"]["entries"],9380)
        self.assertEqual(record["origin"]["cleaned_master_sha256"],digest(CLEANED/"ISBE.xml"))
        self.assertIn(record["quality"]["status"],(
            "source_validated_not_compiled",
            "native_candidate_verified_not_reader_approved",
        ))
        if record["quality"]["status"]=="native_candidate_verified_not_reader_approved":
            self.assertEqual(record["quality"]["native_sword_readback"],
                             "complete_9380_exact_unicode_and_xml")
            self.assertEqual(record["quality"]["native_readback_text_mismatches"],0)
            self.assertEqual(record["quality"]["native_readback_xml_mismatches"],0)
            self.assertEqual(record["quality"]["two_reader_acceptance"],
                             "partial_article_display_verified_interactive_pending")
            self.assertEqual(record["quality"]["gui_article_display_verified_in"],
                             ["Xiphos","BibleTime"])
            self.assertEqual(record["quality"]["gui_article_headword_sample"],"AARON")
            self.assertFalse(record["quality"]["interactive_gui_hyperlink_click_verified"])
            validation=read_json(folder/"SOURCE_VALIDATION.json")
            self.assertEqual(validation["independently_tested_gui_readers"],
                             ["Xiphos","BibleTime"])
            self.assertEqual(validation["gui_article_display"]["headword"],"AARON")
            self.assertFalse(validation["gui_article_display"]["actual_clicked_links_verified"])
            self.assertFalse(validation["gui_article_display"]["two_reader_full_acceptance"])
            self.assertFalse(validation["xiphos_accepted"])
            self.assertFalse(validation["second_reader_accepted"])
            self.assertFalse(validation["publication_permitted"])
        self.assertFalse(record["distribution"]["payload_present"])
        self.assertFalse(record["distribution"]["release_published"])
        distribution=record["distribution"]
        if distribution.get("draft_binary_asset"):
            self.assertFalse(distribution["draft_source_release_only"])
            self.assertTrue(distribution["draft_contains_source_and_native_candidate"])
            self.assertNotEqual(distribution["status"],
                                "compiled_candidate_in_unpublished_actions_artifact")
        if distribution.get("temporary_actions_binary_deleted"):
            self.assertNotIn("actions_artifact",distribution["status"])
        self.assertFalse(record["rights"]["redistribution_allowed"])

    def test_no_active_script_or_workflow_uses_retired_paths(self):
        disallowed=("cleaned/en/","sources/crosswire/","sources/print/","modern/en/")
        active=[]
        for folder in (ROOT/"scripts",ROOT/"tests",ROOT/".github/workflows"):
            for path in folder.rglob("*"):
                if path.is_file() and path.suffix in (".py",".yml",".yaml",".sh") and path!=Path(__file__):
                    active.append(path)
        for path in active:
            text=path.read_text(encoding="utf-8")
            for obsolete in disallowed:
                self.assertNotIn(obsolete,text,f"{path}: retired path")
if __name__=="__main__":
    unittest.main()
