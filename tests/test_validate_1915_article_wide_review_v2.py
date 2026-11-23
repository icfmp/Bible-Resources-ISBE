"""Tests for cumulative 24-article print-image English-prose research, without false certification."""
import copy
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from scripts.validate_1915_article_wide_review_v2 import (
    load, validate_extension
)

ROOT = Path(__file__).resolve().parents[1]

class ArticleWideProseReviewV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior_path=ROOT/"workspace/reviews/1915-article-wide-prose-review-v1.json"
        cls.prior_bytes=cls.prior_path.read_bytes()
        cls.previous=load(cls.prior_path)
        cls.current=load(ROOT/"workspace/reviews/1915-article-wide-prose-review-v2.json")
        cls.manifest=load(ROOT/"sources/print/1915-volume-witnesses.json")
        cls.root=ET.parse(ROOT/"cleaned/en/ISBE.xml").getroot()

    def rejects(self, fn):
        item=copy.deepcopy(self.current)
        fn(item)
        with self.assertRaises(ValueError):
            validate_extension(self.previous,item,self.root,self.manifest,self.prior_bytes)

    def test_twenty_four_source_bound_prose_passes_but_zero_whole_print_certifications(self):
        result=validate_extension(self.previous,self.current,self.root,
                                  self.manifest,self.prior_bytes)
        self.assertEqual((result["review_candidates"],result["reviewed_english_total"],
                          result["complete_original_script_punctuation_reference_collations"],
                          result["new_excerpt_observations"]), (24,24,0,5))
        self.assertFalse(result["publication_permitted"])

    def test_cannot_mutate_previous_page_image_or_canonical_text(self):
        self.rejects(lambda j:j["entries"][0].update(page_image_sha256="0"*64))
        self.rejects(lambda j:j["entries"][0].update(canonical_visible_text_characters=3))
        self.rejects(lambda j:j["entries"][0].update(source_article_xml_id="invented"))

    def test_cannot_spuriously_pass_unfinished_print_collar(self):
        self.rejects(lambda j:j.update(full_historical_collation_certified=True))
        self.rejects(lambda j:j.update(publication_permitted=True))
        self.rejects(lambda j:j["entries"][3].update(full_word_for_word_print_collation_certified=True))
        self.rejects(lambda j:j["entries"][3].update(original_script_punctuation_and_markup_verified=True))

    def test_cannot_forge_source_print_excerpt_or_approve_automatic_changes(self):
        self.rejects(lambda j:j["entries"][3]["new_article_wide_findings"][0].update(
            digital_exact="an invented unsourced passage"))
        self.rejects(lambda j:j["entries"][3]["new_article_wide_findings"][0].update(
            text_correction_approved=True))

    def test_cannot_discard_prior_review_decisions_or_promote_without_witness(self):
        self.rejects(lambda j:j["entries"][0].update(review_note="historical full collation done"))
        self.rejects(lambda j:j["entries"][3].update(
            english_prose_linewise_comparison_completed=False))
        self.rejects(lambda j:j.update(previous_review_git_blob_sha1="0"*40))

    def test_cannot_drop_any_of_24_source_articles(self):
        self.rejects(lambda j:j["entries"].pop())
        self.rejects(lambda j:j["entries"].reverse())

if __name__=="__main__":
    unittest.main()
