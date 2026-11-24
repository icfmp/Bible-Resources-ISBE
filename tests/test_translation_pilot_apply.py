"""Real-source and negative regression coverage for partial FR translation drafts."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.apply_translation_pilot import apply
from scripts.validate_translation_identity import TEI, XML_ID, XML_LANG, read_body

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources/cleaned/encyclopedias/en/isbe-1915/ISBE.xml"
PILOT = ROOT / "workspace/pilots/isbe-1915-fr"
ROSTER = PILOT / "roster.json"
PATCHES = PILOT / "draft-patches.json"


class FrenchPilotDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roster = json.loads(ROSTER.read_text(encoding="utf-8"))
        cls.patches = json.loads(PATCHES.read_text(encoding="utf-8"))

    def run_draft(self, patch_data=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        target = Path(tmp.name) / "draft.xml"
        report = Path(tmp.name) / "report.json"
        source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        patches = PATCHES
        if patch_data is not None:
            patches = Path(tmp.name) / "altered-patches.json"
            patches.write_text(json.dumps(patch_data, ensure_ascii=False),
                               encoding="utf-8")
        result = apply(SOURCE, ROSTER, patches,
                       output=target, report_path=report)
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                         source_hash)
        return result, target

    def test_eight_real_drafts_and_all_fifty_source_identity_rows_survive(self):
        result, target = self.run_draft()
        self.assertEqual(result["pilot_article_count"], 50)
        self.assertEqual(result["unreviewed_drafts"], 8)
        self.assertEqual(result["pending"], 42)
        self.assertFalse(result["publication_permitted"])
        self.assertEqual(result["human_reviewed"], 0)
        root, body = read_body(target)
        self.assertEqual(root.get(XML_LANG), "mul")
        self.assertEqual(len(body), 50)
        self.assertEqual(
            [(node.get("n"), node.get(XML_ID)) for node in body],
            [(x["source_key"], x["article_id"]) for x in self.roster["articles"]])
        self.assertEqual(
            {x["translation_status"] for x in result["articles"]},
            {"pending", "complete_unreviewed_draft"})
        ark = next(x for x in body if x.get("n") == "ARK")
        self.assertEqual(ark.find(TEI + "head").text, "ARCHE")
        self.assertEqual(ark.find(TEI + "p").find(TEI + "ref").text,
                         "ARCHE DE JONCS")
        chorbe = next(x for x in body if x.get("n") == "CHORBE")
        self.assertIn("Χορβέ", "".join(chorbe.itertext()))
        self.assertIn("Zaccaï", "".join(chorbe.itertext()))

    def test_reject_stale_translation_source_text(self):
        patches = copy.deepcopy(self.patches)
        patches["articles"][0]["units"][0]["source"] = "not the original text"
        with self.assertRaisesRegex(ValueError, "Source text mismatch"):
            self.run_draft(patches)

    def test_reject_missing_original_script_spans(self):
        patches = copy.deepcopy(self.patches)
        chorbe = next(p for p in patches["articles"] if p["source_key"] == "CHORBE")
        paragraph = next(u for u in chorbe["units"] if u["node"] == 2)
        paragraph["target"] = paragraph["target"].replace("Χορβέ", "CHORBE")
        with self.assertRaisesRegex(ValueError, "Greek/Hebrew"):
            self.run_draft(patches)

    def test_reject_forged_canonical_article_id_or_source_hash(self):
        for field, value in (
            ("article_id", "isbe-fr-translation-reindexed"),
            ("source_article_sha256", "0" * 64),
        ):
            patches = copy.deepcopy(self.patches)
            patches["articles"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.run_draft(patches)

    def test_reject_duplicate_unit_and_tampered_scripture_locator(self):
        patches = copy.deepcopy(self.patches)
        patches["articles"][0]["units"].append(
            copy.deepcopy(patches["articles"][0]["units"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate translation unit"):
            self.run_draft(patches)

        patches = copy.deepcopy(self.patches)
        bul = next(p for p in patches["articles"] if p["source_key"] == "BUL")
        bul["units"].append({
            "node": 3, "part": "text", "source": "1Ki 6:38",
            "target": "1 R 6.39", "action": "translate",
        })
        with self.assertRaisesRegex(ValueError, "Scripture"):
            self.run_draft(patches)

    def test_no_publication_claim_is_possible_from_unreviewed_drafts(self):
        patches = copy.deepcopy(self.patches)
        patches["status"] = "editorially_reviewed"
        with self.assertRaisesRegex(ValueError, "status/language"):
            self.run_draft(patches)


if __name__ == "__main__":
    unittest.main()
