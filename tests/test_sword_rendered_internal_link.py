"""Actual rendered libSWORD TEIHTMLHREF link work/key parser regression."""
import unittest
from scripts.audit_sword_rendered_internal_link import verify, links, matches_sword_key

SAMPLE={
 "source_article":"ARK",
 "destination_article":"ARK OF BULRUSHES",
 "original_xml_target":"#historical-id",
 "native_link_target":"BRISBE1915:ARK OF BULRUSHES"
}

class SwordRenderedLinkTests(unittest.TestCase):
    def test_matches_explicit_work_and_encoded_spaces(self):
        html='<p>See <a href="sword://BRISBE1915/ARK%20OF%20BULRUSHES">ARK OF BULRUSHES</a></p>'
        result=verify(SAMPLE,"BRISBE1915",html)
        self.assertEqual(result["native_sword_href"],"sword://BRISBE1915/ARK%20OF%20BULRUSHES")
        self.assertTrue(result["native_sword_dictionary_link_resolves_to_expected_module"])
        self.assertFalse(result["gui_reader_click_verified"])
    def test_rejects_original_invalid_self_work(self):
        html='<a href="sword://self/ARK%20OF%20BULRUSHES">ARK OF BULRUSHES</a>'
        with self.assertRaisesRegex(ValueError,"cannot navigate"):
            verify(SAMPLE,"BRISBE1915",html)
    def test_rejects_wrong_key_in_valid_module(self):
        html='<a href="sword://BRISBE1915/ARK%20OF%20THE%20COVENANT">wrong key</a>'
        with self.assertRaisesRegex(ValueError,"cannot navigate"):
            verify(SAMPLE,"BRISBE1915",html)
    def test_colon_inside_entry_key_is_preserved(self):
        self.assertTrue(matches_sword_key("sword://BRISBE1915/A%3AB%20C","BRISBE1915","A:B C"))
    def test_html_entity_and_whitespace_not_a_fake_href(self):
        self.assertEqual(links('<a href="sword://BRISBE1915/ARK%20OF%20BULRUSHES?bad=1">test</a>'),
                         ["sword://BRISBE1915/ARK%20OF%20BULRUSHES?bad=1"])
        self.assertFalse(matches_sword_key("sword://BRISBE1915/ARK%20OF%20BULRUSHES?bad=1",
                                           "BRISBE1915","ARK OF BULRUSHES"))

if __name__=="__main__":
    unittest.main()
