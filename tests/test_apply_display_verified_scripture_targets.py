"""Negative controls for display-attested navigation changes, without print claims."""
import copy
import unittest
import xml.etree.ElementTree as ET

from scripts.apply_display_verified_scripture_targets import (
    ID, LOCK, T, apply_changes, verified_decisions,
)


def fixture():
    row = {
        "source_key": "EXAMPLE",
        "source_unit_xml_id": "example-p1",
        "source_ref_xml_id": "example-r1",
        "original_visible": "f; Jud 1:27",
        "original_cRef": "Bible:Rev.1.2",
        "corrected_cRef": "Bible:Judg.1.27",
        "explicit_label_book": "Jud",
        "explicit_label_chapter": 1,
        "explicit_label_verse": 27,
        "printed_1915_certification": False,
        "approved_for_noncanonical_navigation_layer": True,
        "parallel_print_attested_article": "PRINTED EXAMPLE",
        "parallel_print_attested_ref_xml_id": "printed-r1",
        "digital_witness_urls": ["https://example.org/witness-a", "https://example.net/witness-b"],
    }
    spec = {
        "schema_version": 1,
        "canonical_source_sha256": LOCK,
        "preceding_editorial_layer": "1915_print_attested_31_plus_6_plus_12_plus_1",
        "evidence_level": "digital_display_parallel_print_mapping_not_taanach_print",
        "original_1915_folios_verified": False,
        "publication_permitted": False,
        "independent_human_peer_review": False,
        "decisions": [row],
    }
    original = {
        "canonical_sha256": LOCK,
        "canonical_modified": False,
        "cases": [{
            "ref_xml_id": "example-r1",
            "disposition": "unresolved_no_adequate_print_page",
            "proposed_cRef": None,
            "source_key": "EXAMPLE",
            "unit_xml_id": "example-p1",
            "visible": "f; Jud 1:27",
            "original_cRef": "Bible:Rev.1.2",
        }, {
            "ref_xml_id": "printed-r1",
            "source_key": "PRINTED EXAMPLE",
            "disposition": "visually_attested_candidate",
            "visible": "f; Jud 1:27",
            "proposed_cRef": "Bible:Judg.1.27",
            "source_image_jpeg_sha256": "a" * 64,
            "printed_reading": "Jgs 1 27 f",
        }],
    }
    xml = (
        '<TEI xmlns="http://www.tei-c.org/ns/1.0">'
        '<text><body><div n="EXAMPLE" xml:id="example-a1">'
        '<p xml:id="example-p1">Start <ref xml:id="example-r1" '
        'type="scripture" cRef="Bible:Rev.1.2">f; Jud 1:27</ref> end.</p>'
        '</div><div n="UNCHANGED" xml:id="other-a1">'
        '<p xml:id="other-p1">Unrelated.</p>'
        '</div></body></text></TEI>'
    )
    return spec, original, ET.fromstring(xml)


class DisplayOnlySourceGateTests(unittest.TestCase):
    def test_allows_unambiguous_label_with_uncertified_print(self):
        spec, original, _ = fixture()
        self.assertEqual(verified_decisions(spec, original), spec["decisions"])

    def test_changes_only_target_and_is_reversible(self):
        spec, original, root = fixture()
        rows = verified_decisions(spec, original)
        article = list(root.find(f"./{T}text/{T}body"))[0]
        unchanged = list(root.find(f"./{T}text/{T}body"))[1]
        before = ET.tostring(article)
        untouched = ET.tostring(unchanged)
        original_text = "".join(root.itertext())
        changed, operations = apply_changes(root, rows)
        self.assertEqual(changed, {"EXAMPLE"})
        self.assertEqual(len(operations), 1)
        self.assertEqual("".join(root.itertext()), original_text)
        self.assertEqual(ET.tostring(unchanged), untouched)
        ref = article.find(f".//{T}ref")
        self.assertEqual(ref.get("cRef"), "Bible:Judg.1.27")
        ref.set("cRef", "Bible:Rev.1.2")
        self.assertEqual(ET.tostring(article), before)

    def assert_rejected(self, mutate):
        spec, original, _ = fixture()
        mutate(spec, original)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            verified_decisions(spec, original)

    def test_rejects_pretended_print_certification(self):
        self.assert_rejected(lambda spec, _: spec.update(original_1915_folios_verified=True))
        self.assert_rejected(lambda spec, _: spec["decisions"][0].update(printed_1915_certification=True))

    def test_rejects_publication(self):
        self.assert_rejected(lambda spec, _: spec.update(publication_permitted=True))

    def test_rejects_missing_or_reused_digital_witnesses(self):
        self.assert_rejected(lambda spec, _: spec["decisions"][0].update(digital_witness_urls=["https://example.org/a"]))
        self.assert_rejected(lambda spec, _: spec["decisions"][0].update(digital_witness_urls=["https://example.org/a", "https://example.org/a"]))

    def test_rejects_unapproved_or_unresolved_mismatch(self):
        self.assert_rejected(lambda spec, _: spec["decisions"][0].update(approved_for_noncanonical_navigation_layer=False))
        self.assert_rejected(lambda _, original: original["cases"][0].update(proposed_cRef="Bible:Judg.1.27"))

    def test_rejects_uncorroborated_book_mapping(self):
        self.assert_rejected(lambda spec, _: spec["decisions"][0].update(corrected_cRef="Bible:Zech.1.27"))
        self.assert_rejected(lambda spec, _: spec["decisions"][0].update(parallel_print_attested_ref_xml_id="unknown"))
        self.assert_rejected(lambda spec, original: original["cases"][1].update(disposition="unresolved_no_adequate_print_page"))

    def test_rejects_visible_reference_mismatch(self):
        self.assert_rejected(lambda spec, _: spec["decisions"][0].update(original_visible="f; Rev 1:2"))
        self.assert_rejected(lambda spec, _: spec["decisions"][0].update(explicit_label_book="Rev"))
        self.assert_rejected(lambda spec, _: spec["decisions"][0].update(corrected_cRef="Bible:Judg.1.2"))

    def test_rejects_wrong_source_reference_at_application(self):
        spec, original, root = fixture()
        rows = verified_decisions(spec, original)
        ref = root.find(f".//{T}ref")
        ref.set("cRef", "Bible:Rev.1.3")
        with self.assertRaises(ValueError):
            apply_changes(root, rows)

    def test_rejects_changed_parent_context(self):
        spec, original, root = fixture()
        rows = verified_decisions(spec, original)
        root.find(f".//{T}p").set(ID, "unexpected-id")
        with self.assertRaises(ValueError):
            apply_changes(root, rows)


if __name__ == "__main__":
    unittest.main()
