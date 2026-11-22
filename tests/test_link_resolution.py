import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rebuild_tei import resolve_key, separator_key, semicolon_alias_index, inverted_definite_article_index


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

    def test_explicit_semicolon_alias_unique(self):
        ids = {"ABGAR; ABGARUS; ABAGARUS": "entry"}
        normalized = {k.casefold(): [k] for k in ids}
        aliases = semicolon_alias_index(ids)
        actual = resolve_key("ABGARUS", ids, normalized, aliases=aliases)
        self.assertEqual(actual, ("ABGAR; ABGARUS; ABAGARUS",
                                  "explicit_semicolon_title_alias"))

    def test_ambiguous_semicolon_alias_is_not_resolved(self):
        ids = {"A; B": "one", "B; C": "two"}
        normalized = {k.casefold(): [k] for k in ids}
        aliases = semicolon_alias_index(ids)
        self.assertEqual(resolve_key("B", ids, normalized, aliases=aliases),
                         (None, "ambiguous"))

    def test_indexed_complete_article_wins_over_alias(self):
        ids = {"CLOPAS": "separate", "CLOPAS; CLEOPHAS": "compound"}
        normalized = {k.casefold(): [k] for k in ids}
        aliases = semicolon_alias_index(ids)
        self.assertEqual(resolve_key("CLOPAS", ids, normalized, aliases=aliases),
                         ("CLOPAS", "exact"))

    def test_self_ambiguous_alias_redirects_to_only_other_article(self):
        from rebuild_tei import build
        imp = """$$$ATHANASIAN; CREED
<entryFree n="ATHANASIAN; CREED"><p>See <ref target="ISBE:CREED">CREED</ref>.</p></entryFree>
$$$CREED; CREEDS
<entryFree n="CREED; CREEDS"><p>A general creed entry.</p></entryFree>"""
        root, _, report = build(imp)
        source = next(el for el in root.iter() if el.tag.endswith("div") and el.get("n") == "ATHANASIAN; CREED")
        dest = next(el for el in root.iter() if el.tag.endswith("div") and el.get("n") == "CREED; CREEDS")
        ref = next(el for el in source.iter() if el.get("n") == "ISBE:CREED")
        self.assertEqual(ref.get("target"), "#" + dest.get("{http://www.w3.org/XML/1998/namespace}id"))
        self.assertEqual(report["resolved_redirect_alias_occurrences"], 1)

    def test_ambiguous_alias_from_other_article_stays_unresolved(self):
        from rebuild_tei import build
        imp = """$$$OTHER
<entryFree n="OTHER"><p>See <ref target="ISBE:CREED">CREED</ref>.</p></entryFree>
$$$ATHANASIAN; CREED
<entryFree n="ATHANASIAN; CREED"><p>One subject.</p></entryFree>
$$$CREED; CREEDS
<entryFree n="CREED; CREEDS"><p>Another subject.</p></entryFree>"""
        _, _, report = build(imp)
        self.assertEqual(report["resolved_redirect_alias_occurrences"], 0)
        self.assertEqual(report["unresolved_link_occurrences"], 1)

    def test_unique_inverted_definite_article(self):
        ids = {"DEAD SEA, THE": "entry"}
        normalized = {k.casefold(): [k] for k in ids}
        inversions = inverted_definite_article_index(ids)
        self.assertEqual(resolve_key("DEAD SEA", ids, normalized, inversions=inversions),
                         ("DEAD SEA, THE", "inverted_definite_article"))

    def test_other_comma_qualified_topics_are_not_inverted(self):
        ids = {"EVE, GOSPEL OF": "entry"}
        normalized = {k.casefold(): [k] for k in ids}
        inversions = inverted_definite_article_index(ids)
        self.assertEqual(resolve_key("EVE", ids, normalized, inversions=inversions),
                         (None, "not_found"))

    def test_explicit_approved_title_alias(self):
        from rebuild_tei import build
        imp = """$$$BOND
<entryFree n="BOND"><p>See <ref target="ISBE:BILL">BILL</ref>.</p></entryFree>
$$$BILL, BOND, ETC.
<entryFree n="BILL, BOND, ETC."><p>A written bond.</p></entryFree>"""
        root, _, report = build(imp, reviewed={"BILL": "BILL, BOND, ETC."})
        bond = next(x for x in root.iter() if x.tag.endswith("div") and x.get("n") == "BOND")
        ref = next(x for x in bond.iter() if x.get("n") == "ISBE:BILL")
        self.assertTrue(ref.get("target").startswith("#isbe-"))
        self.assertEqual(report["resolved_variant_occurrences"], 1)

    def test_reviewed_title_alias_cannot_invent_missing_entry(self):
        from rebuild_tei import build
        with self.assertRaisesRegex(ValueError, "Unknown reviewed alias destination"):
            build('$$$SOURCE\\n<entryFree n="SOURCE"><p>Text.</p></entryFree>',
                  reviewed={"MISSING": "NOT AN ARTICLE"})

    def test_missing_stays_missing(self):
        self.assertEqual(resolve_key("LITERATURE", self.ids, self.lookup), (None, "not_found"))


if __name__ == "__main__":
    unittest.main()
