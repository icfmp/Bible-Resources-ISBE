import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from translation_diff import compare, read_tei

NS = "http://www.tei-c.org/ns/1.0"


class TranslationDiffTests(unittest.TestCase):
    def test_changed_unit_does_not_invalidate_other_unit(self):
        with tempfile.TemporaryDirectory() as d:
            old = Path(d, "old.xml")
            new = Path(d, "new.xml")
            def make(word):
                return (
                    f'<TEI xmlns="{NS}"><text><body><div type="entry" xml:id="a">'
                    f'<head xml:id="a-head">A</head><p xml:id="a-p1">{word}</p>'
                    f'<p xml:id="a-p2">Unchanged</p></div></body></text></TEI>')
            old.write_text(make("Old"), encoding="utf-8")
            new.write_text(make("New"), encoding="utf-8")
            report = compare(read_tei(old), read_tei(new))
            self.assertEqual(report["totals"]["changed"], 1)
            self.assertEqual(report["totals"]["unchanged"], 2)

    def test_duplicate_article_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "bad.xml")
            p.write_text(
                f'<TEI xmlns="{NS}"><text><body>'
                '<div type="entry" xml:id="a"><p xml:id="p1">One</p></div>'
                '<div type="entry" xml:id="a"><p xml:id="p2">Two</p></div>'
                '</body></text></TEI>', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate article"):
                read_tei(p)

    def test_removed_block(self):
        old = {"a": {"p": "hash"}}
        new = {"a": {}}
        self.assertEqual(compare(old, new)["totals"]["removed"], 1)


if __name__ == "__main__":
    unittest.main()
