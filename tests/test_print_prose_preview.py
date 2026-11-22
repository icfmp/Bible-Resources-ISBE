"""Canonical data stay unchanged while historically attested text is proposed."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts.preview_print_prose import apply, q

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"cleaned/en/ISBE.xml"
REDIRECTS=ROOT/"workspace/reviews/redirect-candidate-v1.json"
PROSE=ROOT/"workspace/reviews/print-prose-candidate-v1.json"

class PrintProsePreviewTests(unittest.TestCase):
    def test_nine_historical_article_candidates_and_eleven_redirects(self):
        source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as folder:
            dest=Path(folder)/"candidate.xml"
            report=Path(folder)/"report.json"
            result=apply(SOURCE,REDIRECTS,PROSE,dest,report)
            self.assertEqual(result["unchanged_articles_verified"],9360)
            self.assertEqual(result["proposed_historical_text_entries"],9)
            self.assertEqual(result["proposed_redirects"],11)
            self.assertEqual(result["new_xml_ids"],2)
            self.assertFalse(result["publication_permitted"])
            self.assertTrue(result["noncanonical"])
            self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),source_hash)
            body=ET.parse(dest).getroot().find("./"+q("text")+"/"+q("body"))
            records={a.get("n"):a for a in body}
            self.assertIn("An ancestor of Ezra", "".join(records["ABISSEI"].itertext()))
            self.assertIn("(2) A name in the genealogy of Judah", "".join(records["AMNON"].itertext()))
            self.assertIn("whose origin is from the days of the olden time", "".join(records["ANTIQUITY"].itertext()))
            self.assertEqual(len([p for p in records["AMNON"] if p.tag==q("p")]),3)
            self.assertIn("descendant of Asher", "".join(records["BEERA"].itertext()))
            self.assertIn("In 1 Esdras 8:2", "".join(records["SAVIAS"].itertext()))
            self.assertIn("Grandfather of Shallum", "".join(records["HASRAH"].itertext()))
            self.assertIn("JOSHIBIAH", "".join(records["JOSIBIAH"].itertext()))

    def test_rejects_changed_source_lock(self):
        with tempfile.TemporaryDirectory() as folder:
            data=json.loads(PROSE.read_text(encoding="utf-8"))
            data["document_base_sha256"]="x"*64
            bad=Path(folder)/"bad.json"
            bad.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"source SHA256"):
                apply(SOURCE,REDIRECTS,bad,Path(folder)/"out.xml",Path(folder)/"report.json")

if __name__=="__main__":
    unittest.main()
