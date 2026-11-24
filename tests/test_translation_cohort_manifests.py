"""Verify bounded French translation cohorts against the original ISBE worklist.

Cohorts are editorial scheduling records, not a second canonical index.
Each cohort member must resolve to the unchanged English source identity
and to exactly one complete unpublished source-locked draft.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.select_translation_pilot import SOURCE_SHA256


ROOT = Path(__file__).resolve().parents[1]
WORKLIST_DIR = ROOT / "workspace/translations/isbe-1915/fr/worklists/wave-01"
COHORT_DIR = ROOT / "workspace/translations/isbe-1915/fr/cohorts"
BATCH_PREFIX = "workspace/translations/isbe-1915/fr/batches/"


class TranslationCohortManifestTests(unittest.TestCase):
    def test_cohorts_are_frozen_unique_and_source_matched(self):
        worklist = json.loads((WORKLIST_DIR / "0001-1000.json").read_text(encoding="utf-8"))
        self.assertEqual(worklist["source_sha256"], SOURCE_SHA256)
        work_by_id = {row["article_id"]: row for row in worklist["entries"]}
        self.assertEqual(len(work_by_id), len(worklist["entries"]))

        manifests = sorted(COHORT_DIR.glob("COHORT_*.json"))
        self.assertTrue(manifests, "At least one frozen translation cohort expected")
        all_members = set()
        cached_batches = {}
        total = 0

        for file in manifests:
            manifest = json.loads(file.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(manifest["kind"], "bounded_editorial_translation_cohort")
            self.assertEqual(manifest["source_sha256"], SOURCE_SHA256)
            self.assertEqual(manifest["translation_language"], "fr")
            self.assertFalse(manifest["publication_permitted"])
            self.assertEqual(manifest["human_editorially_approved"], 0)
            self.assertEqual(manifest["status"],
                             "complete_first_drafts_pending_bilingual_editorial_acceptance")
            self.assertGreater(manifest["item_count"], 0)
            self.assertLessEqual(manifest["item_count"], 100)
            self.assertEqual(len(manifest["entries"]), manifest["item_count"])

            last_position = 0
            for row in manifest["entries"]:
                self.assertIn(row["article_id"], work_by_id)
                canonical = work_by_id[row["article_id"]]
                self.assertEqual(row["source_key"], canonical["source_key"])
                self.assertEqual(row["index"], canonical["index"])
                self.assertGreater(row["index"], last_position)
                last_position = row["index"]
                self.assertNotIn(row["article_id"], all_members,
                                 "An article appears in multiple editorial cohorts")
                all_members.add(row["article_id"])

                batch_path = row["patch_file"]
                self.assertTrue(batch_path.startswith(BATCH_PREFIX))
                self.assertEqual(Path(batch_path).suffix, ".json")
                self.assertTrue((ROOT / batch_path).is_file())
                if batch_path not in cached_batches:
                    batch = json.loads((ROOT / batch_path).read_text(encoding="utf-8"))
                    self.assertEqual(batch["source_sha256"], SOURCE_SHA256)
                    self.assertEqual(batch["status"], "unreviewed_drafts")
                    self.assertFalse(batch["publication_permitted"])
                    records = {item["article_id"]: item for item in batch["articles"]}
                    self.assertEqual(len(records), len(batch["articles"]))
                    cached_batches[batch_path] = records
                record = cached_batches[batch_path].get(row["article_id"])
                self.assertIsNotNone(record)
                self.assertEqual(record["source_key"], row["source_key"])
                self.assertEqual(record["source_article_sha256"],
                                 row["source_article_sha256"])
                self.assertTrue(record["units"])
                self.assertEqual(record["editorial_status"], "complete_unreviewed_draft")
            total += manifest["item_count"]

        self.assertEqual(len(all_members), total)


if __name__ == "__main__":
    unittest.main()
