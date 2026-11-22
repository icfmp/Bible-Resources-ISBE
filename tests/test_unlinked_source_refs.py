import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rebuild_tei import build, XMLID
from audit_link_contexts import scan

TEI = "http://www.tei-c.org/ns/1.0"


class SourceReferenceRetirementTests(unittest.TestCase):
    def test_missing_link_is_unlinked_without_losing_text_or_target(self):
        imp = ('$$$ARTICLE\n'
               '<entryFree n="ARTICLE"><p>Compare <ref target="ISBE:UNATTESTED">'
               'UNATTESTED</ref> and the next word.</p></entryFree>')
        root, _, report = build(imp)
        article = next(x for x in root.iter() if x.get("n") == "ARTICLE")
        paragraph = next(x for x in article.iter() if x.tag == "p")
        self.assertEqual("".join(paragraph.itertext()), "Compare UNATTESTED and the next word.")
        segment = next(x for x in paragraph.iter() if x.get("type") == "unlinked-source-reference")
        self.assertEqual(segment.tag, f"{{{TEI}}}seg")
        self.assertEqual(segment.get("n"), "ISBE:UNATTESTED")
        self.assertIsNone(segment.get("target"))
        self.assertTrue(segment.get(XMLID))
        self.assertEqual(report["unlinked_source_reference_occurrences"], 1)
        self.assertEqual(report["unresolved_link_occurrences"], 1)
        self.assertEqual(report["unlinked_source_references"][0]["ref_id"], segment.get(XMLID))

    def test_ambiguous_reference_has_no_guess_and_retains_provenance(self):
        imp = ('$$$SOURCE\n'
               '<entryFree n="SOURCE"><p><ref target="ISBE:JOHN">JOHN</ref></p></entryFree>\n'
               '$$$JOHN (1)\n<entryFree n="JOHN (1)"><p>Person A</p></entryFree>\n'
               '$$$JOHN (2)\n<entryFree n="JOHN (2)"><p>Person B</p></entryFree>')
        root, _, report = build(imp)
        seg = next(x for x in root.iter() if x.get("type") == "unlinked-source-reference")
        self.assertEqual(seg.get("subtype"), "ambiguous_numbered_headword")
        self.assertEqual(seg.get("n"), "ISBE:JOHN")
        self.assertEqual(report["unresolved_link_occurrences"], 1)

    def test_resolved_internal_link_remains_clickable(self):
        imp = ('$$$SOURCE\n'
               '<entryFree n="SOURCE"><p><ref target="ISBE:TARGET">TARGET</ref></p></entryFree>\n'
               '$$$TARGET\n<entryFree n="TARGET"><p>Content</p></entryFree>')
        root, _, report = build(imp)
        ref = next(x for x in root.iter() if x.get("n") == "ISBE:TARGET")
        self.assertEqual(ref.tag, "ref")
        self.assertTrue(ref.get("target", "").startswith("#"))
        self.assertEqual(report["unlinked_source_reference_occurrences"], 0)

    def test_review_audit_includes_preserved_unlinked_source(self):
        imp = ('$$$SOURCE\n'
               '<entryFree n="SOURCE"><p><ref target="ISBE:LOST">LOST</ref></p></entryFree>')
        root, _, _ = build(imp)
        with tempfile.TemporaryDirectory() as tmp:
            xml_path = Path(tmp) / "ISBE.xml"
            ET.ElementTree(root).write(xml_path, encoding="utf-8", xml_declaration=True)
            audit = scan(xml_path)
        self.assertEqual(audit["total_unresolved_occurrences"], 1)
        self.assertEqual(audit["occurrences"][0]["original_target"], "LOST")
        self.assertEqual(audit["navigation_status"], "unlinked_not_clickable")


if __name__ == "__main__":
    unittest.main()
