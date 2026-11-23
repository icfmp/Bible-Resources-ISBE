"""Negative and positive source-lock tests for ten exact 1915 printed prose repairs."""
import copy
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from scripts.apply_1915_additional_prose_deltas import (
    T, apply_exact, articles, read, validate_ledger
)

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'workspace/reviews/1915-additional-exact-print-deltas-v1.json'
SOURCE = ROOT / 'cleaned/en/ISBE.xml'


class Additional1915ProseDeltasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = read(LEDGER)
        cls.research = read(ROOT / 'workspace/reviews/1915-article-wide-prose-review-v2.json')
        cls.witness = read(ROOT / 'sources/print/1915-volume-witnesses.json')
        cls.source = ET.parse(SOURCE).getroot()

    def rejects(self, changed):
        data = copy.deepcopy(self.spec)
        changed(data)
        with self.assertRaises(ValueError):
            validate_ledger(data, self.source, self.research, self.witness)

    def test_ten_individual_print_attestations_have_exact_original_source(self):
        rows = validate_ledger(self.spec, self.source, self.research, self.witness)
        self.assertEqual(len(rows), 10)
        self.assertEqual({r['source_key'] for r in rows},
                         {'ABIDE', 'BUSINESS', 'GAINSAY', 'MEADOW', 'REPAIR', 'YEA'})
        self.assertFalse(self.spec['publication_permitted'])
        self.assertFalse(self.spec['full_historical_collation_certified'])
        meadow = next(r for r in rows if r['source_key'] == 'MEADOW')
        self.assertIn('[AV “paper reeds”]', meadow['printed_visible'])
        self.assertNotIn('(AV “paper reeds”)', meadow['printed_visible'])
        business = next(r for r in rows if r['source_key'] == 'BUSINESS')
        self.assertIn('ἐν τοῖς τοῦ πατρός μου', business['printed_visible'])

    def test_real_full_inventory_edit_and_reversal_preserve_all_untouched_entries(self):
        root = ET.parse(SOURCE).getroot()
        before = articles(root)
        ga_orig = ET.tostring(before['GAINSAY'], encoding='utf-8')
        unaffected = ET.tostring(before['WATERCOURSE'], encoding='utf-8')
        prior_count = len(before)
        changed, records = apply_exact(root, self.spec['decisions'])
        self.assertEqual(len(records), 10)
        self.assertEqual(len(changed), 6)
        self.assertEqual(len(articles(root)), prior_count)
        self.assertEqual(ET.tostring(articles(root)['WATERCOURSE'], encoding='utf-8'),
                         unaffected)
        self.assertNotEqual(ET.tostring(articles(root)['GAINSAY'], encoding='utf-8'),
                            ga_orig)
        ga = ''.join(articles(root)['GAINSAY'].itertext())
        self.assertNotIn('/APC', ga)
        self.assertIn('Esther 9:13', ga,
                      'Ambiguous printed Ad Est 13:9 navigation must not be silently re-targeted')
        self.assertIn('ἐν τοῖς τοῦ πατρός μου',
                      ''.join(articles(root)['BUSINESS'].itertext()))

    def test_reject_changes_to_canonicity_scholarly_approval_or_source(self):
        self.rejects(lambda d: d.update(publication_permitted=True))
        self.rejects(lambda d: d.update(full_historical_collation_certified=True))
        self.rejects(lambda d: d.update(canonical_source_modified=True))
        self.rejects(lambda d: d.update(independent_human_peer_review=True))

    def test_reject_wrong_page_hash_ref_slot_and_fabricated_phrases(self):
        self.rejects(lambda d: d['decisions'][0].update(jpeg_sha256='0'*64))
        self.rejects(lambda d: d['decisions'][0].update(original_pdf_sha256='1'*64))
        self.rejects(lambda d: d['decisions'][0].update(source_unit_xml_id='invented'))
        self.rejects(lambda d: d['decisions'][0].update(slot_owner_xml_id='invented'))
        self.rejects(lambda d: d['decisions'][0].update(source_unit_text_sha256='0'*64))
        self.rejects(lambda d: d['decisions'][0].update(original_visible='nonexistent source text'))

    def test_reject_global_rewrite_and_duplicate_source_operations(self):
        self.rejects(lambda d: d['decisions'][0].update(operation='global_regex_replace'))
        self.rejects(lambda d: d['decisions'][0].update(approved_for_separate_1915_tei=False))
        self.rejects(lambda d: d['decisions'].__setitem__(1, d['decisions'][0]))
        self.rejects(lambda d: d['decisions'].pop())


if __name__ == '__main__':
    unittest.main()
