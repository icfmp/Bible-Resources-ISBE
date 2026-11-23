"""Negative gates for article-wide original 1915 image research."""
import copy
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from scripts.validate_1915_article_wide_review import load, validate

ROOT=Path(__file__).resolve().parents[1]

class ArticleWideVisualReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=load(ROOT/"workspace/reviews/1915-article-wide-prose-review-v1.json")
        cls.manifest=load(ROOT/"workspace/witnesses/print/1915-volume-witnesses.json")
        cls.root=ET.parse(ROOT/"workspace/witnesses/crosswire-2.2/ISBE.xml").getroot()

    def reject(self, fn):
        spec=copy.deepcopy(self.spec)
        fn(spec)
        with self.assertRaises(ValueError):
            validate(spec,self.manifest,self.root)

    def test_complete_source_inventory_and_evidence_scope(self):
        outcome=validate(self.spec,self.manifest,self.root)
        self.assertEqual((outcome["candidates"],outcome["article_body_one_original_page"],
                          outcome["english_prose_reviewed"],outcome["full_print_collations_certified"]),
                         (24,23,12,0))

    def test_reject_false_certification_and_publication(self):
        self.reject(lambda s:s.update(full_historical_collation_certified=True))
        self.reject(lambda s:s.update(publication_permitted=True))
        self.reject(lambda s:s["entries"][0].update(full_word_for_word_print_collation_certified=True))

    def test_reject_source_or_photo_identity_drift(self):
        self.reject(lambda s:s["entries"][0].update(source_article_xml_id="fiction"))
        self.reject(lambda s:s["entries"][0].update(canonical_visible_text_sha256="0"*64))
        self.reject(lambda s:s["entries"][0].update(page_image_sha256="invalid"))

    def test_reject_wrong_citation_and_digital_words(self):
        self.reject(lambda s:s["entries"][0].update(pdf_page=99999))
        self.reject(lambda s:s["entries"][0]["observations"][0].update(digital_exact="fabricated text"))

    def test_reject_uncollated_continuation_claim(self):
        row=next(i for i,x in enumerate(self.spec["entries"]) if x["source_key"]=="ZABUD")
        self.reject(lambda s:s["entries"][row].update(verified_continuation_pages=[]))
        self.reject(lambda s:s["entries"][row]["verified_continuation_pages"][0].update(image_sha256="0"))
        self.reject(lambda s:s["entries"][row].update(pending_continuation_pdf_pages=[329]))

    def test_reject_silent_coverage_inflation(self):
        row=next(i for i,x in enumerate(self.spec["entries"]) if x["source_key"]=="GAINSAY")
        self.reject(lambda s:s["entries"][row].update(source_text_read_through_entire_article=True,
            english_prose_linewise_comparison_completed=True,
            evidence_scope="whole_article_english_prose_pass",review_note="unverified"))

if __name__=="__main__":
    unittest.main()
