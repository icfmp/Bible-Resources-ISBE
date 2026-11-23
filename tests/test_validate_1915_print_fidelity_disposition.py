"""Strict original source-image fail-closed decisions, not printed-glyph certifications."""
import copy
from pathlib import Path
import unittest
from scripts.validate_1915_print_fidelity_disposition import load,validate

ROOT=Path(__file__).resolve().parents[1]

class OriginalPrint24DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decisions=load(ROOT/"workspace/reviews/1915-all24-print-fidelity-disposition-v1.json")
        cls.visual=load(ROOT/"workspace/reviews/1915-article-wide-prose-review-v2.json")
        cls.printlayer=load(ROOT/"workspace/reviews/1915-all24-print-layer-whole-article-comparison-v1.json")
    def rejection(self,change):
        data=copy.deepcopy(self.decisions)
        change(data)
        with self.assertRaises(ValueError):
            validate(data,self.visual,self.printlayer)
    def test_all_24_exact_print_reproductions_rejected_but_never_falsely_collated(self):
        r=validate(self.decisions,self.visual,self.printlayer)
        self.assertEqual(r["original_print_fidelity_rejected"],24)
        self.assertEqual(r["entire_original_print_glyph_collations_completed"],0)
        self.assertFalse(r["publication_permitted"])
    def test_no_unauthorized_release_or_promotion_to_full_text_certification(self):
        self.rejection(lambda d:d.update(publication_permitted=True))
        self.rejection(lambda d:d.update(print_identical_fidelity_approved=24))
        self.rejection(lambda d:d.update(full_original_1915_print_word_for_word_collation_certified=24))
        self.rejection(lambda d:d["decisions"][0].update(print_identical_fidelity=True))
    def test_forged_source_image_and_article_ids_fail(self):
        self.rejection(lambda d:d["decisions"][0].update(original_page_jpeg_sha256="0"*64))
        self.rejection(lambda d:d["decisions"][0].update(source_article_xml_id="invented"))
        self.rejection(lambda d:d["decisions"][0].update(complete_digital_article_sha256="1"*64))
        self.rejection(lambda d:d["decisions"][0].update(complete_source_pdf_text_layer_sha256="2"*64))
    def test_no_automatic_reconstruction_follows_from_a_fidelity_fail(self):
        self.rejection(lambda d:d["decisions"][0].update(automatic_text_change_authorized=True))
        self.rejection(lambda d:d["decisions"][0].update(
            further_original_script_punctuation_reference_collation_needed_to_reconstruct=False))
        self.rejection(lambda d:d["decisions"].pop())
if __name__=="__main__":
    unittest.main()
