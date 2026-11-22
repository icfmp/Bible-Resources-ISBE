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

    def test_standalone_marked_paragraph_heading(self):
        imp = """$$$EDUCATION
<entryFree n="EDUCATION"><p><ref target="ISBE:I. EDUCATION DEFINED">I. EDUCATION DEFINED</ref></p><p><hi rend="bold">I. Education Defined.</hi></p><p>Teaching follows.</p></entryFree>"""
        root, _, report = build(imp)
        article = root.find(".//{http://www.tei-c.org/ns/1.0}div[@type='entry']")
        title = next(x for x in article.iter() if x.tag == "hi")
        ref = next(x for x in article.iter() if x.tag == "ref")
        self.assertEqual(ref.get("target"), "#" + title.get(XMLID))
        self.assertEqual(report["resolved_local_section_occurrences"], 1)

    def test_plain_standalone_section_title(self):
        imp = """$$$ANTHROPOMORPHISM
<entryFree n="ANTHROPOMORPHISM"><p><ref target="ISBE:1. DEFINITION OF THE TERM">1. DEFINITION OF THE TERM</ref></p><p>1. Definition of the Term</p><p>Discussion follows.</p></entryFree>"""
        root, _, report = build(imp)
        article = root.find(".//{http://www.tei-c.org/ns/1.0}div[@type='entry']")
        paragraphs = [el for el in article.iter() if el.tag == "p"]
        ref = next(x for x in article.iter() if x.tag == "ref")
        self.assertEqual(ref.get("target"), "#" + paragraphs[1].get(XMLID))
        self.assertEqual(report["resolved_local_section_occurrences"], 1)

    def test_numbered_bold_heading_with_paragraph_content(self):
        imp = """$$$ARTICLE
<entryFree n="ARTICLE"><p><ref target="ISBE:I. DEFINITION">I. DEFINITION</ref></p><p><hi rend="bold">I. Definition:</hi> An introductory explanation.</p></entryFree>"""
        root, _, report = build(imp)
        article = root.find(".//{http://www.tei-c.org/ns/1.0}div[@type='entry']")
        heading = next(el for el in article.iter() if el.tag == "hi")
        ref = next(el for el in article.iter() if el.tag == "ref")
        self.assertEqual(ref.get("target"), "#" + heading.get(XMLID))
        self.assertEqual(report["resolved_local_section_occurrences"], 1)

    def test_no_guess_for_repeated_plain_section_title(self):
        imp = """$$$ARTICLE
<entryFree n="ARTICLE"><p><ref target="ISBE:LITERATURE">Literature</ref></p><p>Literature</p><p>Literature</p></entryFree>"""
        _, _, report = build(imp)
        self.assertEqual(report["unresolved_link_occurrences"], 1)

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
