"""Regression controls for the reusable Markdown translation work queue."""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import apply_translation_batches, prepare_isbe_markdown_queue
from scripts.export_tei_markdown_corpus import export
from scripts.validate_translation_identity import sha256
from tests.test_export_tei_markdown_corpus import specimen


class MarkdownQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "original.xml"
        specimen(self.source)
        self.source_hash = sha256(self.source)
        self.archive = self.root / "archive.zip"
        export(self.source, self.archive, report=self.root / "report.json",
               expected_sha=self.source_hash, expected_count=2)
        self.roster = self.root / "roster.json"
        self.roster_data = {
            "source_sha256": self.source_hash,
            "source_article_count": 2,
            "translation_language": "fr",
            "article_count": 2,
            "entries": [
                {"source_key":"A","article_id":"isbe-test-a","index":1},
                {"source_key":"B","article_id":"isbe-test-b","index":2},
            ],
        }
        self.save_roster()
        self.patch_file = self.root / "drafts.json"
        self.patch_file.write_text(json.dumps({
            "schema_version": 1,
            "source_sha256": self.source_hash,
            "language": "fr",
            "status": "unreviewed_drafts",
            "publication_permitted": False,
            "articles": [{
                "article_id": "isbe-test-a",
                "source_key": "A",
                "source_article_sha256": "source-hash-attested-by-main-validator",
            }],
        }), encoding="utf-8")

    def save_roster(self):
        self.roster.write_text(json.dumps(self.roster_data), encoding="utf-8")

    def run_prepare(self, *, output=None, reserved_manifests=None):
        with (patch.object(prepare_isbe_markdown_queue, "SOURCE_SHA256", self.source_hash),
              patch.object(prepare_isbe_markdown_queue, "SOURCE_COUNT", 2),
              patch.object(apply_translation_batches, "SOURCE_SHA256", self.source_hash)):
            return prepare_isbe_markdown_queue.prepare(
                archive=self.archive, source=self.source, roster=self.roster,
                patches=[self.patch_file],
                output=output or (self.root / "next-five"),
                reserved_manifests=reserved_manifests)

    def test_pending_only_original_source_identity_and_exact_checksums(self):
        result = self.run_prepare()
        self.assertEqual(result["drafted_wave_01"], 1)
        self.assertEqual(result["pending_wave_01"], 1)
        self.assertEqual(result["templates_prepared"], 1)
        self.assertEqual(result["human_editorial_approvals"], 0)
        self.assertFalse(result["publication_permitted"])
        article = result["articles"][0]
        self.assertEqual(article["source_key"], "B")
        self.assertEqual(article["article_id"], "isbe-test-b")
        self.assertEqual(article["source_position"], 1)
        markdown = (self.root / "next-five" / article["template"]).read_bytes()
        self.assertEqual(hashlib.sha256(markdown).hexdigest(), article["template_sha256"])
        self.assertIn(b"ISBE-BLOCK", markdown)
        self.assertEqual(json.loads((self.root / "next-five" / "MANIFEST.json").read_text())["articles"], result["articles"])

    def test_source_roster_modified_or_duplicate_is_rejected(self):
        self.roster_data["entries"][1]["source_key"] = "A"
        self.save_roster()
        with self.assertRaisesRegex(ValueError, "duplicated"):
            self.run_prepare()
        self.roster_data["entries"][1]["source_key"] = "B"
        self.roster_data["entries"][1]["index"] = 17
        self.save_roster()
        with self.assertRaisesRegex(ValueError, "position"):
            self.run_prepare()

    def test_reserved_queue_is_excluded_without_counting_as_drafted(self):
        first = self.run_prepare()
        manifest = self.root / "next-five" / "MANIFEST.json"
        second = self.run_prepare(output=self.root / "prefetch", reserved_manifests=[manifest])
        self.assertEqual(first["templates_prepared"], 1)
        self.assertEqual(second["templates_prepared"], 0)
        self.assertEqual(second["drafted_wave_01"], 1)
        self.assertEqual(second["pending_wave_01"], 1)
        with self.assertRaisesRegex(ValueError, "duplicated reserved"):
            self.run_prepare(output=self.root / "duplicate", reserved_manifests=[manifest, manifest])

    def test_never_overwrite_preexisting_editorial_files(self):
        directory = self.root / "next-five"
        directory.mkdir()
        (directory / "note.md").write_text("DO NOT ERASE")
        with self.assertRaisesRegex(ValueError, "empty output"):
            self.run_prepare(output=directory)
        self.assertEqual((directory / "note.md").read_text(), "DO NOT ERASE")


if __name__ == "__main__":
    unittest.main()
