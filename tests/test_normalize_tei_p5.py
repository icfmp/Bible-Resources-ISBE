import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from normalize_tei_p5 import (
    Q, XMLID, build_candidate, original_indexed_text, sha256, survey,
)

SAMPLE = '''<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader><fileDesc>
    <titleStmt><title>ISBE source fixture</title></titleStmt>
    <publicationStmt><p>Unpublished</p></publicationStmt>
    <sourceDesc><p>CrossWire test fixture</p></sourceDesc>
  </fileDesc></teiHeader>
  <text><body>
    <div type="entry" xml:id="isbe-example" n="EXAMPLE">
      <head xml:id="isbe-example-head">EXAMPLE</head>
      <p xml:id="p1">Alpha <ref xml:id="r1" osisRef="Bible:Gen.1.1">Gen 1:1</ref>
        <hi xml:id="h1" rend="italic">important</hi>.</p>
      <p xml:id="p2">See <ref xml:id="r2" n="ISBE:EXAMPLE"
        target="#isbe-example">this entry</ref>.</p>
      <p xml:id="p3">See <seg xml:id="s1"
        n="ISBE:LOST" type="unlinked-source-reference"
        subtype="unverified">unknown</seg>.</p>
      <head xml:id="bh1" type="bibliography"><hi xml:id="hi1"
        n="ISBE:LITERATURE." rend="bibliography-heading">LITERATURE.</hi></head>
      <p xml:id="p4">A bibliography. <ref xml:id="r3"
        osisRef="Bible:Exod.20.1-Exod.20.17">Ex 20</ref></p>
    </div>
  </body></text>
</TEI>'''


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.source, self.candidate = root / "source.xml", root / "candidate.xml"
        self.index, self.manifest, self.report = (
            root / "index.json", root / "manifest.json", root / "report.json"
        )
        self.prepare(SAMPLE)

    def prepare(self, xml):
        self.source.write_text(xml, encoding="utf-8")
        root = ET.fromstring(xml)
        articles, _, counts = survey(root)
        self.index.write_text(json.dumps([
            {"key": art.get("n"), "id": art.get(XMLID), "text_sha256":
             hashlib.sha256(original_indexed_text(art).encode("utf-8")).hexdigest()}
            for art in articles
        ]), encoding="utf-8")
        self.manifest.write_text(json.dumps({
            "version": 1, "source_sha256": sha256(self.source),
            "expected": dict(counts),
        }), encoding="utf-8")

    def run_candidate(self):
        return build_candidate(
            self.source, self.candidate, self.index, self.manifest, self.report
        )

    def test_lossless_candidate_including_serialization_and_bibliography(self):
        report = self.run_candidate()
        original = ET.parse(self.source).getroot()
        output = ET.parse(self.candidate).getroot()
        article = next(node for node in output.iter() if node.get(XMLID) == "isbe-example")
        self.assertEqual(report["article_parity"], "PASS")
        self.assertEqual(report["source_index_text_sha256_all_articles"], "PASS")
        self.assertEqual(report["official_tei_schema_validation"], "NOT_PERFORMED")
        self.assertEqual(original_indexed_text(
            next(node for node in original.iter() if node.get(XMLID) == "isbe-example")),
            original_indexed_text(article))
        self.assertEqual(output.get("{http://www.w3.org/XML/1998/namespace}lang"), "en")
        self.assertIsNotNone(output.find(".//" + Q("refsDecl")))
        self.assertIsNotNone(output.find(".//" + Q("revisionDesc")))
        self.assertEqual(article[0].get("type"), "index")
        self.assertEqual([node.get("cRef") for node in article.iter(Q("ref"))
                          if node.get("type") == "scripture"],
                         ["Bible:Gen.1.1", "Bible:Exod.20.1-Exod.20.17"])
        self.assertFalse(any(node.get("osisRef") is not None
                             for node in article.iter()))
        section = next(node for node in article.iter(Q("div"))
                       if node.get("type") == "bibliography")
        self.assertEqual(section[0].get(XMLID), "bh1")
        self.assertEqual(section[1].get(XMLID), "p4")
        self.assertEqual(report["bibliography_wrappers"], 1)
        self.assertEqual(report["source_inventory"]["source_links"], 3)
        self.assertEqual(report["source_inventory"]["bibliography_leads"], 0)
        self.assertEqual(
            next(node for node in article.iter() if node.get(XMLID) == "r2").get("type"),
            "article",
        )

    def test_bibliography_lead_keeps_paragraph_in_valid_section(self):
        inline = SAMPLE.replace(
            '<head xml:id="bh1" type="bibliography">',
            '<p xml:id="bh1" type="bibliography-lead">'
        ).replace(
            '</head>\n      <p xml:id="p4">',
            '</p>\n      <p xml:id="p4">'
        )
        self.prepare(inline)
        report = self.run_candidate()
        output = ET.parse(self.candidate).getroot()
        moved = next(node for node in output.iter() if node.get(XMLID) == "bh1")
        self.assertEqual(moved.tag, Q("p"))
        self.assertIsNone(moved.get("type"))
        self.assertEqual(report["transformation_counts"]["bibliography_leads"], 1)
        self.assertEqual(report["bibliography_wrappers"], 1)
        self.assertEqual(report["source_inventory"].get("bibliography_heads", 0), 0)
        section = next(node for node in output.iter(Q("div"))
                       if node.get("type") == "bibliography")
        self.assertIs(section[0], moved)
        self.assertEqual(section[1].get(XMLID), "p4")

    def test_original_file_is_never_overwritten(self):
        previous = self.source.read_bytes()
        with self.assertRaisesRegex(ValueError, "distinct candidate"):
            build_candidate(self.source, self.source, self.index,
                            self.manifest, self.report)
        self.assertEqual(previous, self.source.read_bytes())

    def test_hash_lock_fails_closed(self):
        with self.source.open("a", encoding="utf-8") as out:
            out.write("\n")
        with self.assertRaisesRegex(ValueError, "SHA-256 changed"):
            self.run_candidate()
        self.assertFalse(self.candidate.exists())

    def test_dual_target_reference_rejected(self):
        self.prepare(SAMPLE.replace(
            'osisRef="Bible:Gen.1.1"', 'osisRef="Bible:Gen.1.1" target="#isbe-example"'))
        with self.assertRaisesRegex(ValueError, "conflicting destinations"):
            self.run_candidate()
        self.assertFalse(self.candidate.exists())

    def test_unknown_active_target_rejected(self):
        self.prepare(SAMPLE.replace('target="#isbe-example"', 'target="#not-real"'))
        with self.assertRaisesRegex(ValueError, "Broken source target"):
            self.run_candidate()

    def test_unreviewed_new_heading_rejected(self):
        self.prepare(SAMPLE.replace(
            '<head xml:id="bh1" type="bibliography">',
            '<head xml:id="bh1" type="newly-invented">'))
        with self.assertRaisesRegex(ValueError, "Unexpected source heading"):
            self.run_candidate()

    def test_manifest_incorrect_count_rejected(self):
        metadata = json.loads(self.manifest.read_text(encoding="utf-8"))
        metadata["expected"]["scripture_refs"] += 1
        self.manifest.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Pinned source inventory changed"):
            self.run_candidate()


if __name__ == "__main__":
    unittest.main()
