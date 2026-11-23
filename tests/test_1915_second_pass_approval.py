"""Hard-fail if any recovered 1915 text drifts from second visual approval."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from finalize_1915_recovery import approved_records

REVIEWS = ROOT / "workspace/reviews"
def load(name):
    return json.loads((REVIEWS / name).read_text(encoding="utf-8"))

class SecondPrintReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.approval = load("1915-second-pass-visual-approval-v1.json")
        cls.prose = load("print-prose-candidate-v1.json")
        cls.redirect = load("redirect-candidate-v1.json")
        cls.pages = load("1915-visual-page-collation-v1.json")

    def validate(self, approval=None, prose=None):
        return approved_records(
            approval if approval is not None else self.approval,
            prose if prose is not None else self.prose,
            self.redirect, self.pages
        )

    def test_every_print_entry_has_matching_provenance_and_exact_text(self):
        self.assertEqual(self.validate(), 31)

    def test_one_character_prose_change_is_rejected(self):
        altered = copy.deepcopy(self.prose)
        altered["records"][0]["blocks"][0] += "x"
        with self.assertRaisesRegex(ValueError, "transcription changed"):
            self.validate(prose=altered)

    def test_missing_or_duplicate_second_reading_rejected(self):
        altered = copy.deepcopy(self.approval)
        altered["records"].pop()
        with self.assertRaisesRegex(ValueError, "Missing original image evidence"):
            self.validate(approval=altered)
        altered = copy.deepcopy(self.approval)
        altered["records"][0] = altered["records"][1]
        with self.assertRaisesRegex(ValueError, "repeated approval"):
            self.validate(approval=altered)

    def test_wrong_original_page_hash_rejected(self):
        altered = copy.deepcopy(self.approval)
        altered["records"][0]["rendered_image_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.validate(approval=altered)

    def test_not_independent_human_or_redistribution_approval(self):
        altered = copy.deepcopy(self.approval)
        altered["independent_human_peer_review"] = True
        with self.assertRaisesRegex(ValueError, "independent human"):
            self.validate(approval=altered)
        altered = copy.deepcopy(self.approval)
        altered["legal_redistribution_clearance"] = True
        with self.assertRaisesRegex(ValueError, "redistribution rights"):
            self.validate(approval=altered)

if __name__ == "__main__":
    unittest.main()
