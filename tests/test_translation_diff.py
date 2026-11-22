import sys
import tempfile
import unittest
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from translation_diff import compare, digest, read_tree


class DiffTests(unittest.TestCase):
    def test_segment_changes(self):
        old = {"a": {"one": digest("Original"), "two": digest("Kept")}}
        new = {"a": {"one": digest("Modernized"), "two": digest("Kept"),
                     "three": digest("New")}}
        result = compare(old, new)
        self.assertEqual(result["totals"],
                         {"added": 1, "removed": 0, "changed": 1, "unchanged": 1})
        self.assertEqual([x["status"] for x in result["segments"]],
                         ["changed", "added", "unchanged"])

    def test_reject_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.json").write_text(json.dumps({
                "id": "a", "segments": [{"id": "x", "text": "1"},
                                      {"id": "x", "text": "2"}]}))
            with self.assertRaisesRegex(ValueError, "Duplicate segment"):
                read_tree(d)

    def test_removed_segment(self):
        result = compare({"a": {"x": digest("gone")}}, {"a": {}})
        self.assertEqual(result["totals"]["removed"], 1)


if __name__ == "__main__":
    unittest.main()
