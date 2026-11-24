"""Fifty existing ISBE French drafts plus Abraham need full reading copies."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.render_translation_review_corpus import build

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml"
PILOT = ROOT / "workspace/pilots/isbe-1915-fr/draft-patches.json"
ABRAHAM = ROOT / "workspace/translations/isbe-1915/fr/batches/0001-abraham.json"
FLAGS = ROOT / "workspace/pilots/isbe-1915-fr/SOURCE_REVIEW_FLAGS.json"


class TranslationReviewCorpusTests(unittest.TestCase):
    def test_all_50_first_pilot_drafts_are_readable_and_unreviewed(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            report = build(SOURCE, [PILOT, ABRAHAM], folder / "proofs",
                           folder / "audit.json", flags_file=FLAGS)
            self.assertEqual(report["selected_complete_unreviewed_drafts"], 51)
            self.assertEqual(report["pilot_drafts_count"], 50)
            self.assertEqual(report["batch_drafts_count"], 1)
            self.assertEqual(report["source_article_count"], 9380)
            self.assertEqual(report["source_flags_pending_witness_review"], 12)
            self.assertEqual(report["source_flag_affected_articles"], 6)
            self.assertEqual(report["human_editorially_approved"], 0)
            self.assertEqual(report["article_checkboxes_marked_complete"], 0)
            self.assertFalse(report["publication_permitted"])
            self.assertEqual(len(list((folder / "proofs").glob("isbe-*.md"))), 51)
            index=(folder / "proofs" / "INDEX.md").read_text(encoding="utf-8")
            self.assertIn("HOLY OF HOLIES", index)
            self.assertIn("DEUTERO-CANONICAL, BOOKS", index)
            self.assertIn("GRACE", index)
            self.assertIn("ABRAHAM", index)
            for article in report["articles"]:
                preview = folder / "proofs" / article["preview"]
                self.assertTrue(preview.is_file())
                self.assertIn(article["title_fr"], preview.read_text(encoding="utf-8"))
                self.assertEqual(article["style_and_editorial_review"], "pending")
                self.assertFalse(article["publication_permitted"])
            abraham=next(a for a in report["articles"] if a["source_key"]=="ABRAHAM")
            canonical=(ROOT / "workspace/translations/isbe-1915/fr/reviews/ABRAHAM.md"
                       ).read_text(encoding="utf-8")
            self.assertEqual((folder / "proofs" / abraham["preview"]
                              ).read_text(encoding="utf-8"), canonical)
            self.assertEqual(json.loads((folder/"audit.json").read_text(
                encoding="utf-8")), report)


if __name__ == "__main__":
    unittest.main()
