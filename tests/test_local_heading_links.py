import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rebuild_tei import build, resolve_local_heading, XMLID


class LocalHeadingTests(unittest.TestCase):
    def test_unique_explicit_underlined_section(self):
        imp = """$$$ARTICLE
<entryFree n="ARTICLE"><p><hi rend="underline">I. Introductory:</hi> Body.</p><p>See <ref target="ISBE:I. INTRODUCTORY">above</ref>.</p></entryFree>"""
        root, index, report = build(imp)
        article = root.find(".//{http://www.tei-c.org/ns/1.0}div[@type='entry']")
        heading = next(x for x in article.iter() if x.tag == "hi" and x.get("rend") == "underline")
        ref = next(x for x in article.iter() if x.tag == "ref")
        self.assertEqual(ref.get("target"), "#" + heading.get(XMLID))
        self.assertEqual(ref.get("n"), "ISBE:I. INTRODUCTORY")
        self.assertEqual(report["resolved_local_section_occurrences"], 1)
        self.assertEqual(report["unresolved_link_occurrences"], 0)

    def test_ambiguous_repeated_local_heading_remains_unresolved(self):
        imp = """$$$ARTICLE
<entryFree n="ARTICLE"><p><hi rend="underline">Literature:</hi> A</p><p><hi rend="underline">Literature:</hi> B</p><p><ref target="ISBE:LITERATURE">Here</ref></p></entryFree>"""
        root, index, report = build(imp)
        self.assertEqual(report["resolved_local_section_occurrences"], 0)
        self.assertEqual(report["unresolved_link_occurrences"], 1)

    def test_inline_emphasis_is_not_section_heading(self):
        imp = """$$$ARTICLE
<entryFree n="ARTICLE"><p>Text <hi rend="underline">Literature:</hi> words.</p><p><ref target="ISBE:LITERATURE">Here</ref></p></entryFree>"""
        _, _, report = build(imp)
        self.assertEqual(report["resolved_local_section_occurrences"], 0)


if __name__ == "__main__":
    unittest.main()
