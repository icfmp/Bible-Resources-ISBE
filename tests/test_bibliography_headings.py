import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rebuild_tei import build, XMLID

TEI = "http://www.tei-c.org/ns/1.0"


class BibliographyHeadingTests(unittest.TestCase):
    def test_source_bibliography_link_is_heading_and_toc_points_to_it(self):
        imp = ("$" * 3 + 'ARTICLE\n'
               '<entryFree n="ARTICLE">'
               '<p><ref target="ISBE:LITERATURE">LITERATURE</ref></p>'
               '<p>Discussion.</p>'
               '<p><ref target="ISBE:LITERATURE.">LITERATURE.</ref></p>'
               '<p>Bibliography: Smith, 1910.</p>'
               '</entryFree>')
        root, _, report = build(imp)
        article = next(x for x in root.iter() if x.tag == f"{{{TEI}}}div" and x.get("n") == "ARTICLE")
        bib = next(x for x in article.iter() if x.tag == f"{{{TEI}}}head" and x.get("type") == "bibliography")
        original = next(x for x in bib.iter() if x.get("n") == "ISBE:LITERATURE.")
        self.assertEqual(original.tag, f"{{{TEI}}}hi")
        self.assertIsNone(original.get("target"))
        toc = next(x for x in article.iter() if x.get("n") == "ISBE:LITERATURE")
        self.assertEqual(toc.get("target"), "#" + bib.get(XMLID))
        self.assertEqual(report["reclassified_bibliography_occurrences"], 1)
        self.assertEqual(report["resolved_bibliography_toc_occurrences"], 1)
        self.assertEqual(report["unresolved_link_occurrences"], 0)

    def test_bibliography_label_with_citations_in_same_paragraph(self):
        imp = ("$" * 3 + 'ARTICLE\n'
               '<entryFree n="ARTICLE">'
               '<p>Discussion.</p>'
               '<p><ref target="ISBE:LITERATURE.">LITERATURE.</ref> Smith, Journal, 1900.</p>'
               '<p>Author.</p></entryFree>')
        root, _, report = build(imp)
        paragraph = next(x for x in root.iter() if x.tag.split("}")[-1] == "p" and x.get("type") == "bibliography-lead")
        original = next(x for x in paragraph.iter() if x.get("n") == "ISBE:LITERATURE.")
        self.assertIsNone(original.get("target"))
        self.assertEqual(report["reclassified_bibliography_occurrences"], 1)

    def test_inline_prose_reference_not_reclassified(self):
        imp = ("$" * 3 + 'ARTICLE\n'
               '<entryFree n="ARTICLE">'
               '<p>See <ref target="ISBE:LITERATURE.">LITERATURE.</ref> for details.</p>'
               '<p>Author.</p></entryFree>')
        _, _, report = build(imp)
        self.assertEqual(report["reclassified_bibliography_occurrences"], 0)
        self.assertEqual(report["unresolved_link_occurrences"], 1)


if __name__ == "__main__":
    unittest.main()
