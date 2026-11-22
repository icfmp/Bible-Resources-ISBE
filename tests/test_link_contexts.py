import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_link_contexts import scan


class ContextAuditTests(unittest.TestCase):
    def test_preserves_unresolved_link_context_without_guessing(self):
        xml = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
        <div type="entry" xml:id="entry-one" n="ABIGAIL (1)">
          <p xml:id="p-one">See <ref xml:id="r-one" target="ISBE:ABIGAIL">ABIGAIL</ref>.</p>
        </div></body></text></TEI>"""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "master.xml")
            path.write_text(xml, encoding="utf-8")
            result = scan(path)
        self.assertEqual(result["total_unresolved_occurrences"], 1)
        occurrence = result["occurrences"][0]
        self.assertEqual(occurrence["article_key"], "ABIGAIL (1)")
        self.assertEqual(occurrence["original_target"], "ABIGAIL")
        self.assertIsNone(occurrence["candidate_key"])
        self.assertEqual(occurrence["kind"], "requires_review")
        self.assertIn("See ABIGAIL", occurrence["context"])


if __name__ == "__main__":
    unittest.main()
