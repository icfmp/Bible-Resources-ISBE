import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rebuild_tei import resolve_key, separator_key


class LinkResolutionTests(unittest.TestCase):
    def setUp(self):
        self.ids = {key: "id" for key in ("ABRAHAM", "BILL, BOND, ETC.", "BAAL (1)", "BAAL (2)", "FAITH")}
        self.lookup = {}
        for key in self.ids:
            self.lookup.setdefault(key.strip().casefold(), []).append(key)

    def test_exact(self):
        self.assertEqual(resolve_key("ABRAHAM", self.ids, self.lookup), ("ABRAHAM", "exact"))

    def test_casefold(self):
        self.assertEqual(resolve_key("abraham", self.ids, self.lookup), ("ABRAHAM", "case_or_space"))

    def test_period(self):
        self.assertEqual(resolve_key("FAITH.", self.ids, self.lookup), ("FAITH", "terminal_period"))

    def test_ambiguous_names_never_guessed(self):
        self.assertEqual(resolve_key("BAAL", self.ids, self.lookup), (None, "not_found"))

    def test_unique_separator_variant(self):
        ids = {"ARMY, ROMAN": "a", "ARMY, GREEK": "b"}
        normalized = {k.casefold(): [k] for k in ids}
        sep = {}
        for k in ids:
            sep.setdefault(separator_key(k), []).append(k)
        self.assertEqual(resolve_key("ARMY (ROMAN)", ids, normalized, sep),
                         ("ARMY, ROMAN", "unique_separator_variant"))

    def test_separator_normalization_keeps_letters(self):
        self.assertEqual(separator_key("BUILD; BUILDING"), separator_key("BUILD, BUILDING"))
        self.assertNotEqual(separator_key("GOD'S"), separator_key("GODS"))

    def test_missing_stays_missing(self):
        self.assertEqual(resolve_key("LITERATURE", self.ids, self.lookup), (None, "not_found"))


if __name__ == "__main__":
    unittest.main()
