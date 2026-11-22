"""Canonical data stay unchanged while historically attested text is proposed."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts.preview_print_prose import apply, q, reject_digital_paratext

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"cleaned/en/ISBE.xml"
REDIRECTS=ROOT/"workspace/reviews/redirect-candidate-v1.json"
PROSE=ROOT/"workspace/reviews/print-prose-candidate-v1.json"

class PrintProsePreviewTests(unittest.TestCase):
    def test_all_twenty_historical_article_candidates_and_eleven_redirects(self):
        source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as folder:
            dest=Path(folder)/"candidate.xml"
            report=Path(folder)/"report.json"
            result=apply(SOURCE,REDIRECTS,PROSE,dest,report)
            self.assertEqual(result["unchanged_articles_verified"],9349)
            self.assertEqual(result["proposed_historical_text_entries"],20)
            self.assertEqual(result["proposed_redirects"],11)
            self.assertEqual(result["new_xml_ids"],2)
            self.assertFalse(result["publication_permitted"])
            self.assertTrue(result["noncanonical"])
            self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),source_hash)
            body=ET.parse(dest).getroot().find("./"+q("text")+"/"+q("body"))
            records={a.get("n"):a for a in body}
            # The entire historical source gap must now have usable candidate
            # content, rather than just a correct article count.
            gaps=json.loads((ROOT/"workspace/reviews/empty-article-recovery-ledger.json").read_text(encoding="utf-8"))["cases"]
            self.assertEqual(len(gaps),31)
            for case in gaps:
                with self.subTest(recovered_key=case["source_key"]):
                    article=records[case["source_key"]]
                    old_p=[p for p in article.iter() if p.attrib.get("{http://www.w3.org/XML/1998/namespace}id")==case["paragraph_xml_id"]]
                    self.assertEqual(len(old_p),1)
                    self.assertTrue("".join(old_p[0].itertext()).strip())

            self.assertIn("An ancestor of Ezra", "".join(records["ABISSEI"].itertext()))
            self.assertIn("(2) A name in the genealogy of Judah", "".join(records["AMNON"].itertext()))
            self.assertIn("whose origin is from the days of the olden time", "".join(records["ANTIQUITY"].itertext()))
            self.assertEqual(len([p for p in records["AMNON"] if p.tag==q("p")]),3)
            self.assertIn("descendant of Asher", "".join(records["BEERA"].itertext()))
            self.assertIn("In 1 Esdras 8:2", "".join(records["SAVIAS"].itertext()))
            self.assertIn("AV Jethlah", "".join(records["ITHLAH"].itertext()))
            self.assertIn("ἀποστρέφω", "".join(records["DEHORT"].itertext()))
            self.assertIn("ἡ Τεφώ", "".join(records["TEPHON"].itertext()))
            self.assertIn("Grandfather of Shallum", "".join(records["HASRAH"].itertext()))
            self.assertIn("jos-i-bi'a. See JOSHIBIAH.", "".join(records["JOSIBIAH"].itertext()))
            for key in ("CHORBE", "DEHORT", "FROWARDNESS", "HEMDAN",
                        "MANKIND", "SEPHARVITES", "SHALLUN", "SYCHEM",
                        "TEPHON", "THOCANUS", "THOMEI"):
                with self.subTest(entry=key):
                    self.assertTrue("".join(records[key].itertext()).strip())
            self.assertNotIn("se-far'-vits>", "".join(records["SEPHARVITES"].itertext()))
            self.assertIn("Χορβέ", "".join(records["CHORBE"].itertext()))
            self.assertIn("AV is a transcription", "".join(records["SYCHEM"].itertext()))
            self.assertIn("Θόκανος", "".join(records["THOCANUS"].itertext()))
            self.assertIn('margin "is."', "".join(records["FROWARDNESS"].itertext()))

    def test_boilerplate_is_rejected_without_modifying_canonical_source(self):
        original=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as folder:
            data=json.loads(PROSE.read_text(encoding="utf-8"))
            data["records"][-1]["blocks"][0] += " Copyright Statement These files are public domain."
            injected=Path(folder)/"injected.json"
            injected.write_text(json.dumps(data),encoding="utf-8")
            out=Path(folder)/"out.xml"
            with self.assertRaisesRegex(ValueError,"Non-content digital paratext"):
                apply(SOURCE,REDIRECTS,injected,out,Path(folder)/"report.json")
            self.assertFalse(out.exists())
            self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),original)

    def test_scholarly_uses_of_generic_words_are_not_flagged(self):
        reject_digital_paratext("The editor compared ancient manuscript notes and copyright law.", "TEST")
        for notice in ("Bibliography Information", "Popular Articles",
                       "Share Tweet Save", "<footer>", "Proud member of"):
            with self.subTest(notice=notice):
                with self.assertRaisesRegex(ValueError,"Non-content digital paratext"):
                    reject_digital_paratext("Text " + notice, "TEST")

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
