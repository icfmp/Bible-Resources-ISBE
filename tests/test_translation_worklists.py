"""Full canonical worklists must match corrected source entries 1–4,000."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_translation_worklists import (
    load_worklist, render_ticket, validate,
)
from scripts.select_translation_pilot import SOURCE_SHA256
from scripts.validate_translation_identity import sha256

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml"
FOLDER = ROOT / "workspace/translations/isbe-1915/fr/worklists/wave-01"
ROSTERS = sorted(FOLDER.glob("*.json"))


class FrenchTranslationWorklistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = validate(SOURCE, ROSTERS, expected_start=1,
                               expected_entries=4000)

    def test_pinned_historical_english_master_and_4000_unique_tasks(self):
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(self.summary["canonical_article_count"], 9380)
        self.assertEqual(self.summary["assigned_count"], 4000)
        self.assertEqual([x["start"] for x in self.summary["lots"]],
                         [1, 1001, 2001, 3001])
        self.assertEqual([x["end"] for x in self.summary["lots"]],
                         [1000, 2000, 3000, 4000])
        self.assertFalse(self.summary["published"])
        self.assertFalse(self.summary["editorial_approval_implied"])

    def test_each_ticket_contains_exactly_1000_unchecked_canonical_keys(self):
        for path in ROSTERS:
            roster = load_worklist(path)
            ticket = render_ticket(roster)
            checklist = [line for line in ticket.splitlines()
                         if line.startswith("- [ ] ")]
            self.assertEqual(len(checklist), 1000)
            self.assertNotIn("- [x] ", ticket)
            tick = chr(96)
            self.assertEqual(checklist[0],
                             f"- [ ] {roster['start']:04d} "
                             f"{tick}{roster['entries'][0]['source_key']}{tick}")
            self.assertEqual(checklist[-1],
                             f"- [ ] {roster['end']:04d} "
                             f"{tick}{roster['entries'][-1]['source_key']}{tick}")
            self.assertIn("Drafted ≠ reviewed ≠ published.", ticket)
            self.assertIn("MHCC-derived", ticket)
            self.assertLess(len(ticket), 65000)

    def test_canonical_source_id_change_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            roster = copy.deepcopy(load_worklist(ROSTERS[0]))
            roster["entries"][20]["article_id"] = "isbe-fabricated"
            p = Path(td) / "changed.json"
            p.write_text(json.dumps(roster, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ID/SWORD key mismatch"):
                validate(SOURCE, [p], expected_start=1)

    def test_fabricated_key_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            roster = copy.deepcopy(load_worklist(ROSTERS[0]))
            roster["entries"][18]["source_key"] = "FRENCH TRANSLATION OF HEADWORD"
            p = Path(td) / "translated-key.json"
            p.write_text(json.dumps(roster), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ID/SWORD key mismatch"):
                validate(SOURCE, [p])

    def test_missing_or_reordered_or_duplicated_slot_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            roster = copy.deepcopy(load_worklist(ROSTERS[0]))
            roster["entries"][21], roster["entries"][22] = (
                roster["entries"][22], roster["entries"][21])
            p = Path(td) / "swapped.json"
            p.write_text(json.dumps(roster), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Out-of-order source index"):
                validate(SOURCE, [p])
            with self.assertRaisesRegex(ValueError, "gap/overlap"):
                validate(SOURCE, [ROSTERS[0], ROSTERS[0]])

    def test_wrong_master_revision_and_fake_completion_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            roster = copy.deepcopy(load_worklist(ROSTERS[0]))
            roster["source_sha256"] = "0" * 64
            p = Path(td) / "bad-hash.json"
            p.write_text(json.dumps(roster), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source_sha256"):
                load_worklist(p)
            roster = copy.deepcopy(load_worklist(ROSTERS[0]))
            roster["status"] = "published"
            p.write_text(json.dumps(roster), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid worklist status"):
                load_worklist(p)


if __name__ == "__main__":
    unittest.main()
