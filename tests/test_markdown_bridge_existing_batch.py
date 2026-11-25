"""Existing patch reconstruction check for Markdown bridge."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import apply_translation_batches as batches
from scripts.export_tei_markdown_corpus import export
from scripts.markdown_translation_bridge import compile_draft
from scripts.translation_markdown_layout import template
from scripts.validate_translation_identity import TEI, read_body, sha256
from tests.test_export_tei_markdown_corpus import specimen

class Compatibility(unittest.TestCase):
    def test_existing_patcher_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            source=root/'en.xml'
            specimen(source)
            sha=sha256(source)
            archive=root/'source.zip'
            export(source,archive,report=root/'manifest.json',
                   expected_sha=sha,expected_count=2)
            md=template(archive,'A',expected_sha=sha)
            for old,new in [('# A\n','# TITRE\n'),('In the ','Dans le '),
                            (' and in ',' et en '),(' is written.',' est écrit.'),
                            ("Original editor's note.",'Note française.')]:
                md=md.replace(old,new,1)
            data,report=compile_draft(archive,md,expected_sha=sha)
            file=root/'fr.json'
            file.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
            with patch.object(batches,'SOURCE_SHA256',sha), patch.object(batches,'SOURCE_COUNT',2):
                result=batches.apply(source,[file],output=root/'fr.xml',
                                     report_path=root/'report.json')
            self.assertEqual(result['complete_unreviewed_drafts'],1)
            _,body=read_body(root/'fr.xml')
            article=list(body)[0]
            scripture=next(n for n in article.iter() if n.tag==TEI+'ref')
            self.assertEqual(scripture.get('cRef'),'Jn.1.1')
            self.assertEqual(scripture.text,'Joh 1:1')
            self.assertIn('Dans le λόγος et en Joh 1:1 est écrit.',
                          ''.join(article.itertext()))
