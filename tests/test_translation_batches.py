"""Regression checks for generic source-locked ISBE translation batches."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.apply_translation_batches import apply, load_patches
from scripts.render_translation_reading_copy import render_article
from scripts.export_translation_source import extract
from scripts.select_translation_pilot import SOURCE_COUNT, SOURCE_SHA256
from scripts.validate_translation_identity import (
    XML_ID, entries, read_body, sha256,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml"
PILOT = ROOT / "workspace/pilots/isbe-1915-fr/draft-patches.json"
ABRAHAM = ROOT / "workspace/translations/isbe-1915/fr/batches/0001-abraham.json"
EARLY_WAVE01 = ROOT / "workspace/translations/isbe-1915/fr/batches/0002-early-a-entries.json"
FIRST_25 = ROOT / "workspace/translations/isbe-1915/fr/batches/0003-complete-first-25.json"
WAVE01_ROSTER = ROOT / "workspace/translations/isbe-1915/fr/worklists/wave-01/0001-1000.json"


class TranslationBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_hash = sha256(SOURCE)
        cls.abraham = json.loads(ABRAHAM.read_text(encoding="utf-8"))

    def _apply(self, paths):
        with tempfile.TemporaryDirectory() as root:
            output = Path(root) / "excerpt.xml"
            report = Path(root) / "report.json"
            proof = apply(SOURCE, paths, output=output, report_path=report)
            xml_root, body = read_body(output)
            self.assertEqual(proof, json.loads(report.read_text(encoding="utf-8")))
            self.assertEqual(xml_root.get("{http://www.w3.org/XML/1998/namespace}lang"),
                             "mul")
            return proof, entries(body), list(body)

    def test_start_from_exact_corrected_english_master(self):
        self.assertEqual(self.source_hash, SOURCE_SHA256)
        self.assertEqual(len(self.abraham["articles"]), 1)
        article = self.abraham["articles"][0]
        self.assertEqual(article["source_key"], "ABRAHAM")
        self.assertEqual(article["article_id"], "isbe-34a2976d25bc7d0f3d37")
        self.assertEqual(len(article["source_article_sha256"]), 64)
        self.assertFalse(self.abraham["publication_permitted"])

    def test_bounded_exporter_preserves_canonical_id_and_original_source_spans(self):
        first = extract(SOURCE, ["ABRAHAM"], start=0, limit=50)[0]
        self.assertEqual(first["article_id"], self.abraham["articles"][0]["article_id"])
        self.assertEqual(first["source_article_sha256"],
                         self.abraham["articles"][0]["source_article_sha256"])
        self.assertEqual(first["source_position"], 88)
        self.assertGreater(first["unit_count"], len(first["units"]))
        second = extract(SOURCE, ["ABRAHAM"], start=50, limit=5)[0]
        self.assertEqual(second["start"], 50)
        self.assertNotEqual(first["units"][0], second["units"][0])

    def test_abraham_full_draft_preserves_every_canonical_source_fragment(self):
        proof, index, body = self._apply([ABRAHAM])
        self.assertEqual(proof["master_entry_count"], SOURCE_COUNT)
        self.assertEqual(proof["excerpt_entries"], 1)
        self.assertEqual(proof["complete_unreviewed_drafts"], 1)
        self.assertEqual(proof["partial_unreviewed_drafts"], 0)
        self.assertFalse(proof["publication_permitted"])
        self.assertEqual(index, [("isbe-34a2976d25bc7d0f3d37", "ABRAHAM")])
        self.assertIn("La période de résidence", "".join(body[0].itertext()))
        readable = render_article(body[0], draft_status="complete_unreviewed_draft")
        self.assertIn("## I. Le nom.", readable)
        self.assertIn("## VII. Interprétations", readable)
        self.assertIn("J. Oscar Boyd", readable)
        self.assertNotIn("partial_unreviewed", readable)
        self.assertGreater(len(readable), 25000)
        self.assertEqual(readable, (
            ROOT / "workspace/translations/isbe-1915/fr/reviews/ABRAHAM.md"
        ).read_text(encoding="utf-8"))
        self.assertEqual(readable.count("\n### "), 21)
        self.assertEqual(self.source_hash, sha256(SOURCE))

    def test_pilot_and_new_batch_reuse_one_canonical_index(self):
        proof, index, _ = self._apply([PILOT, ABRAHAM])
        self.assertEqual(proof["excerpt_entries"], 51)
        self.assertEqual(proof["complete_unreviewed_drafts"], 51)
        self.assertEqual(proof["partial_unreviewed_drafts"], 0)
        self.assertEqual(len({ident for ident, _ in index}), 51)
        self.assertEqual(len({key for _, key in index}), 51)
        self.assertEqual([key for _, key in index],
                         sorted([key for _, key in index]))
        self.assertFalse(proof["publication_permitted"])

    def test_first_wave_entries_are_exactly_source_locked_and_unduplicated(self):
        new_batch = json.loads(EARLY_WAVE01.read_text(encoding="utf-8"))
        roster = json.loads(WAVE01_ROSTER.read_text(encoding="utf-8"))
        by_id = {row["article_id"]: row for row in roster["entries"]}
        self.assertEqual(new_batch["source_sha256"], SOURCE_SHA256)
        self.assertEqual(new_batch["language"], "fr")
        self.assertEqual(new_batch["status"], "unreviewed_drafts")
        self.assertFalse(new_batch["publication_permitted"])
        self.assertEqual(len(new_batch["articles"]), 16)
        for article in new_batch["articles"]:
            canonical = by_id[article["article_id"]]
            self.assertEqual(article["source_key"], canonical["source_key"])
            self.assertLessEqual(canonical["index"], 1000)
            self.assertTrue(article["units"])
            self.assertEqual(len(article["units"]),
                             len({(u["node"], u["part"]) for u in article["units"]}))

    def test_first_wave_entries_rebuild_complete_bilingual_preview_without_reindexing(self):
        proof, index, body = self._apply([PILOT, ABRAHAM, EARLY_WAVE01])
        self.assertEqual(proof["excerpt_entries"], 67)
        self.assertEqual(proof["complete_unreviewed_drafts"], 67)
        self.assertEqual(proof["partial_unreviewed_drafts"], 0)
        self.assertEqual(proof["human_reviewed"], 0)
        self.assertFalse(proof["publication_permitted"])
        self.assertEqual(len(index), len(set(index)))
        by_key = {key: article for (_, key), article in zip(index, body)}
        self.assertIn("BÂTON D'AARON", "".join(by_key["AARON'S ROD"].itertext()))
        self.assertIn("Dans les citations anglaises", "".join(by_key["ABIDE"].itertext()))
        self.assertIn("dames du palais", "".join(by_key["ARK OF BULRUSHES"].itertext()))
        self.assertEqual(self.source_hash, sha256(SOURCE))

    def test_first_25_canonical_entries_all_have_complete_drafts(self):
        initial = json.loads(FIRST_25.read_text(encoding="utf-8"))
        roster = json.loads(WAVE01_ROSTER.read_text(encoding="utf-8"))
        self.assertEqual(len(initial["articles"]), 8)
        self.assertEqual(initial["source_sha256"], SOURCE_SHA256)
        self.assertFalse(initial["publication_permitted"])
        self.assertEqual({a["source_key"] for a in initial["articles"]},
                         {"AB (1)", "ABADDON", "ABANAH", "ABARIM",
                          "ABASE", "ABBA", "ABDON (1)", "ABED-NEGO"})
        proof, index, _ = self._apply([PILOT, ABRAHAM, EARLY_WAVE01, FIRST_25])
        self.assertEqual(proof["excerpt_entries"], 75)
        self.assertEqual(proof["complete_unreviewed_drafts"], 75)
        self.assertEqual(proof["partial_unreviewed_drafts"], 0)
        self.assertEqual(proof["human_reviewed"], 0)
        self.assertFalse(proof["publication_permitted"])
        keys = [key for _, key in index]
        head_25 = [r["source_key"] for r in roster["entries"][:25]]
        self.assertEqual([key for key in keys if key in set(head_25)], head_25)
        self.assertEqual(self.source_hash, sha256(SOURCE))

    def test_wrong_master_wrong_entry_or_duplicate_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            temp = Path(root) / "bad.json"
            p = copy.deepcopy(self.abraham)
            p["source_sha256"] = "0" * 64
            temp.write_text(json.dumps(p), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Untrusted source"):
                load_patches([temp])
            p = copy.deepcopy(self.abraham)
            p["articles"][0]["article_id"] = "fabricated-fr-article"
            temp.write_text(json.dumps(p), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fabricated"):
                apply(SOURCE, [temp], output=Path(root) / "result.xml",
                      report_path=Path(root) / "report.json")
            with self.assertRaisesRegex(ValueError, "duplicated article ID"):
                load_patches([ABRAHAM, ABRAHAM])

    def test_source_changed_or_translatable_source_unit_mismatch_is_rejected(self):
        p = copy.deepcopy(self.abraham)
        p["articles"][0]["units"][0]["source"] = "Fake master"
        with tempfile.TemporaryDirectory() as root:
            temp = Path(root) / "modified.json"
            temp.write_text(json.dumps(p), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Source text mismatch"):
                apply(SOURCE, [temp], output=Path(root) / "result.xml",
                      report_path=Path(root) / "report.json")

    def test_ref_labels_and_greek_hebrew_are_not_fabricated(self):
        # The source-owned invariants apply equally to all future languages.
        p = copy.deepcopy(self.abraham)
        p["articles"][0]["units"][0]["target"] = ""
        with tempfile.TemporaryDirectory() as root:
            temp = Path(root) / "bad.json"
            temp.write_text(json.dumps(p), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must not erase"):
                apply(SOURCE, [temp], output=Path(root) / "out.xml",
                      report_path=Path(root) / "report.json")


if __name__ == "__main__":
    unittest.main()
