import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rebuild_tei import build, XMLID


class ScriptureDisambiguationTests(unittest.TestCase):
    def test_unique_shared_osis_reference_selects_numbered_article(self):
        imp = """$$$ABIJAH
<entryFree n="ABIJAH"><p>Mother (see <ref osisRef="Bible:2Chr.29.1">2Ch 29:1</ref>) <ref target="ISBE:ABI">ABI</ref>.</p></entryFree>
$$$ABI (1)
<entryFree n="ABI (1)"><p>Mother of Hezekiah <ref osisRef="Bible:2Chr.29.1">2Ch 29:1</ref>.</p></entryFree>
$$$ABI (2)
<entryFree n="ABI (2)"><p>Different person <ref osisRef="Bible:Gen.1.1">Ge 1:1</ref>.</p></entryFree>"""
        root, _, report = build(imp)
        source = next(x for x in root.iter() if x.tag.endswith("div") and x.get("n") == "ABIJAH")
        destination = next(x for x in root.iter() if x.tag.endswith("div") and x.get("n") == "ABI (1)")
        ref = next(x for x in source.iter() if x.get("target", "").startswith("#"))
        self.assertEqual(ref.get("target"), "#" + destination.get(XMLID))
        self.assertEqual(report["resolved_scripture_disambiguation_occurrences"], 1)

    def test_repeated_citation_in_both_entries_remains_ambiguous(self):
        imp = """$$$SOURCE
<entryFree n="SOURCE"><p><ref osisRef="Bible:Exod.1.1">Ex 1:1</ref> <ref target="ISBE:NAME">NAME</ref></p></entryFree>
$$$NAME (1)
<entryFree n="NAME (1)"><p><ref osisRef="Bible:Exod.1.1">Ex 1:1</ref></p></entryFree>
$$$NAME (2)
<entryFree n="NAME (2)"><p><ref osisRef="Bible:Exod.1.1">Ex 1:1</ref></p></entryFree>"""
        _, _, report = build(imp)
        self.assertEqual(report["resolved_scripture_disambiguation_occurrences"], 0)
        self.assertEqual(report["unresolved_link_occurrences"], 1)

    def test_explicit_see_number_anchors_within_selected_article(self):
        imp = """$$$ELONITES
<entryFree n="ELONITES"><p><ref osisRef="Bible:Num.26.26">Num 26:26</ref> <ref target="ISBE:ELON">ELON</ref> (which see (2) Num 26:26).</p></entryFree>
$$$ELON (1)
<entryFree n="ELON (1)"><p>(1) Another person.</p><p>(2) The son of Zebulun <ref osisRef="Bible:Num.26.26">Num 26:26</ref>.</p></entryFree>
$$$ELON (2)
<entryFree n="ELON (2)"><p>A place <ref osisRef="Bible:Josh.1.1">Josh 1:1</ref>.</p></entryFree>"""
        root, _, report = build(imp)
        source = next(x for x in root.iter() if x.tag.endswith("div") and x.get("n") == "ELONITES")
        target_article = next(x for x in root.iter() if x.tag.endswith("div") and x.get("n") == "ELON (1)")
        section = next(x for x in target_article.iter() if x.tag == "p" and (x.text or "").startswith("(2)"))
        ref = next(x for x in source.iter() if x.get("target", "").startswith("#"))
        self.assertEqual(ref.get("target"), "#" + section.get(XMLID))
        self.assertEqual(report["resolved_scripture_disambiguation_occurrences"], 1)


if __name__ == "__main__":
    unittest.main()
