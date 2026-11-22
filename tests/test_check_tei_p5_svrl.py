import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_tei_p5_svrl import check


class OfficialGateTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        def store(name, content):
            path = self.root / name
            path.write_text(content, encoding="utf-8")
            return path
        self.rng = store("tei_all.rng", "<grammar/>")
        self.sch = store("tei_all.isosch",
                         '<schema xmlns="http://purl.oclc.org/dsdl/schematron" '
                         'queryBinding="xslt2"><pattern id="test"/></schema>')
        self.candidate = store("candidate.xml", "<TEI/>")
        self.source_report = store("fidelity.json", json.dumps({
            "candidate_sha256": self.hash(self.candidate),
            "article_parity": "PASS",
            "serialized_profile_check": "PASS",
        }))
        self.svrl = store("good.svrl",
                          '<schematron-output xmlns="http://purl.oclc.org/dsdl/svrl">'
                          '<active-pattern/><fired-rule/></schematron-output>')
        self.invalid = store("bad.svrl",
                             '<schematron-output xmlns="http://purl.oclc.org/dsdl/svrl">'
                             '<active-pattern/><fired-rule/><failed-assert/>'
                             '</schematron-output>')
        self.manifest = store("manifest.json", json.dumps({"official_tei_p5": {
            "version": "4.12.0",
            "relax_ng": {"url": "https://example.test/tei.rng", "sha256": self.hash(self.rng)},
            "schematron": {"url": "https://example.test/tei.sch",
                           "sha256": self.hash(self.sch), "expected_patterns": 1},
        }}))
        self.report = self.root / "official.json"

    @staticmethod
    def hash(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def execute(self):
        return check(
            manifest_path=self.manifest, candidate_path=self.candidate,
            rng_path=self.rng, schematron_path=self.sch,
            svrl_path=self.svrl, negative_svrl_path=self.invalid,
            source_report_path=self.source_report, output_path=self.report,
        )

    def test_records_real_positive_and_negative_controls(self):
        result = self.execute()
        self.assertEqual(result["official_schematron"], "PASS")
        self.assertEqual(result["negative_control"], "PASS")
        self.assertEqual(result["candidate_sha256"], self.hash(self.candidate))
        self.assertTrue(self.report.is_file())

    def test_unpinned_rng_fails_closed(self):
        self.rng.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "RELAX NG bytes"):
            self.execute()
        self.assertFalse(self.report.exists())

    def test_empty_schematron_validation_fails_closed(self):
        self.svrl.write_text(
            '<schematron-output xmlns="http://purl.oclc.org/dsdl/svrl"/>',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "did not execute"):
            self.execute()

    def test_negative_schematron_control_must_detect_error(self):
        self.invalid.write_bytes(self.svrl.read_bytes())
        with self.assertRaisesRegex(ValueError, "did not reject"):
            self.execute()

    def test_reject_drift_from_pinned_validated_candidate(self):
        metadata = json.loads(self.manifest.read_text(encoding="utf-8"))
        metadata["expected_candidate_sha256"] = "0" * 64
        self.manifest.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "pinned validated candidate"):
            self.execute()

    def test_candidate_mismatch_fails_closed(self):
        self.candidate.write_text("<TEI>changed</TEI>", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs from fidelity"):
            self.execute()


if __name__ == "__main__":
    unittest.main()
