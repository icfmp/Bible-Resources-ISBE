import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rebuild_tei import build, XMLID


CORPUS = """$$$GEMATRIA
<entryFree n="GEMATRIA"><p>See <ref target="ISBE:NUMBERS">NUMBERS</ref> for numeric symbolism.</p></entryFree>
$$$NUMBERS, BOOK OF
<entryFree n="NUMBERS, BOOK OF"><p>Israel's wanderings.</p></entryFree>
$$$NUMBER, LINGUISTICS
<entryFree n="NUMBER, LINGUISTICS"><p>A different topic.</p></entryFree>"""


def original_ref():
    root, _, _ = build(CORPUS)
    source = next(x for x in root.iter() if x.tag.endswith("div") and x.get("n") == "GEMATRIA")
    return next(x.get(XMLID) for x in source.iter() if x.get("target") == "ISBE:NUMBERS")


class ReviewedOccurrenceTests(unittest.TestCase):
    def decision(self):
        return {"source_article": "GEMATRIA", "ref_id": original_ref(),
                "original_target": "NUMBERS", "destination_article": "NUMBERS, BOOK OF",
                "basis": "Explicitly reviewed contextual evidence from the source article and index."}

    def test_occurrence_override_preserves_original_reference(self):
        root, _, report = build(CORPUS, occurrence_mappings=[self.decision()])
        source = next(x for x in root.iter() if x.tag.endswith("div") and x.get("n") == "GEMATRIA")
        target = next(x for x in root.iter() if x.tag.endswith("div") and x.get("n") == "NUMBERS, BOOK OF")
        ref = next(x for x in source.iter() if x.get("n") == "ISBE:NUMBERS")
        self.assertEqual(ref.get("target"), "#" + target.get(XMLID))
        self.assertEqual(report["resolved_reviewed_occurrence_count"], 1)
        self.assertEqual(report["unresolved_link_occurrences"], 0)

    def test_explicit_paragraph_anchor_is_accepted_and_original_is_retained(self):
        pristine, _, _ = build(CORPUS)
        article = next(x for x in pristine.iter()
                       if x.tag.endswith("div") and x.get("n") == "NUMBERS, BOOK OF")
        paragraph_id = next(x.get(XMLID) for x in article.iter() if x.tag.endswith("p"))
        row = self.decision()
        row["destination_element_id"] = paragraph_id
        fixed, _, report = build(CORPUS, occurrence_mappings=[row])
        source = next(x for x in fixed.iter() if x.tag.endswith("div") and x.get("n") == "GEMATRIA")
        ref = next(x for x in source.iter() if x.get("n") == "ISBE:NUMBERS")
        self.assertEqual(ref.get("target"), "#" + paragraph_id)
        self.assertEqual(report["resolved_reviewed_occurrence_count"], 1)

    def test_anchor_must_belong_to_chosen_article(self):
        row = self.decision()
        row["destination_element_id"] = "isbe-id-that-does-not-exist"
        with self.assertRaisesRegex(ValueError, "not in designated article"):
            build(CORPUS, occurrence_mappings=[row])

    def test_article_level_fallback_is_explicitly_reported(self):
        row = self.decision()
        row["destination_precision"] = "article_fallback"
        _, _, report = build(CORPUS, occurrence_mappings=[row])
        self.assertEqual(report["imprecise_article_fallback_count"], 1)
        self.assertEqual(report["resolved_reviewed_occurrences"][0]["destination_precision"],
                         "article_fallback")

    def test_fallback_rejects_false_claim_of_precise_anchor(self):
        row = self.decision()
        row["destination_precision"] = "article_fallback"
        row["destination_element_id"] = "pretend-subsection"
        with self.assertRaisesRegex(ValueError, "fallback cannot include"):
            build(CORPUS, occurrence_mappings=[row])

    def test_source_target_change_fails_loudly(self):
        row = self.decision()
        row["original_target"] = "CHANGED"
        with self.assertRaisesRegex(ValueError, "source target changed"):
            build(CORPUS, occurrence_mappings=[row])

    def test_destination_must_exist(self):
        row = self.decision()
        row["destination_article"] = "NOT-IN-INDEX"
        with self.assertRaisesRegex(ValueError, "Unknown article"):
            build(CORPUS, occurrence_mappings=[row])


if __name__ == "__main__":
    unittest.main()
