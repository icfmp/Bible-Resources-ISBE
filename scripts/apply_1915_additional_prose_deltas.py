#!/usr/bin/env python3
"""Source-bound, exactly reversible 1915 printed phrase corrections in a NEW editorial TEI.

The original CrossWire ZIP/IMP/TEI, earlier editorial layers and historical
images remain unchanged. No whole-article certification or rights are implied.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.audit_tei_structure import analyze

T = '{http://www.tei-c.org/ns/1.0}'
ID = '{http://www.w3.org/XML/1998/namespace}id'
LOCK = 'a54c060420518db1c15bbf54264ed3652ec45e62f93c9af106c44d101add5e25'
ET.register_namespace('', 'http://www.tei-c.org/ns/1.0')


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def text_hash(s):
    return sha256(s.encode('utf-8')).hexdigest()


def articles(root):
    if root.tag != T + 'TEI':
        raise ValueError('Not a TEI P5 file')
    body = root.find(f'./{T}text/{T}body')
    if body is None or len(body) != 9380:
        raise ValueError('Expected 9380 source articles')
    all_ = {}
    for article in body:
        key = article.get('n')
        if not key or key in all_ or not article.get(ID):
            raise ValueError('Bad article index')
        all_[key] = article
    return all_


def validate_ledger(spec, original_root, research, witness):
    if (spec.get('schema_version') != 1
            or spec.get('canonical_tei_sha256') != LOCK
            or spec.get('prior_layer') != '1915_8_print_prose_delta_noncanonical'
            or spec.get('publication_permitted') is not False
            or spec.get('full_historical_collation_certified') is not False
            or spec.get('canonical_source_modified') is not False
            or spec.get('independent_human_peer_review') is not False):
        raise ValueError('Unsupported source or release permission')
    if (research.get('schema_version') != 2
            or research.get('canonical_tei_sha256') != LOCK
            or research.get('english_prose_read_through_count') != 24
            or research.get('full_historical_collation_certified') is not False
            or witness.get('canonical_tei_sha256') != LOCK):
        raise ValueError('Original 1915 witness/English research drift')
    orig = articles(original_root)
    visual = {r['source_key']: r for r in research['entries']}
    vols = {x['volume']: x for x in witness['volumes']}
    if len(visual) != 24 or len(vols) != 5:
        raise ValueError('Unexpected original witnesses')
    rows = spec.get('decisions')
    if not isinstance(rows, list) or len(rows) != 16:
        raise ValueError('Need 10 image-attested edits')
    keys = set()
    for d in rows:
        key = d.get('source_key')
        item = orig.get(key)
        evidence = visual.get(key)
        if (item is None or evidence is None
                or not evidence['english_prose_linewise_comparison_completed']
                or d.get('approved_for_separate_1915_tei') is not True
                or d.get('operation') != 'replace_single_exact_xml_text_slot'
                or d.get('source_article_xml_id') != item.get(ID)
                or d.get('source_article_xml_id') != evidence['source_article_xml_id']
                or d.get('canonical_article_visible_sha256') != evidence['canonical_visible_text_sha256']
                or d.get('volume') != evidence['volume']
                or d.get('pdf_page') != evidence['pdf_page']
                or d.get('original_pdf_sha256') != vols[evidence['volume']]['pdf_sha256']
                or d.get('jpeg_sha256') != evidence['page_image_sha256']
                or d.get('image_reading_not_full_corpus_certification') is not True
                or d.get('slot_kind') not in ('text', 'tail')
                or not isinstance(d.get('rationale'), str)
                or len(d['rationale']) < 45):
            raise ValueError('Missing exact 1915 source and source-slot evidence')
        before = d.get('original_visible')
        after = d.get('printed_visible')
        if (not isinstance(before, str) or len(before) < 5
                or not isinstance(after, str) or len(after) < 4
                or before == after or before.count('/APC') > 1):
            raise ValueError('Unsupported or ambiguous original print change')
        identity = (key, d.get('source_unit_xml_id'),
                    d.get('slot_owner_xml_id'), d.get('slot_kind'), before)
        if identity in keys:
            raise ValueError('Duplicate source replacement')
        keys.add(identity)
        matches = [p for p in item.iter(T + 'p')
                   if p.get(ID) == d.get('source_unit_xml_id')]
        if len(matches) != 1:
            raise ValueError('Unknown source paragraph')
        paragraph = matches[0]
        original_text = ''.join(paragraph.itertext())
        if (text_hash(original_text) != d.get('source_unit_text_sha256')
                or original_text.count(before) != 1):
            raise ValueError('Canonical original paragraph or exact quote changed')
        nodes = [n for n in paragraph.iter()
                 if n.get(ID) == d.get('slot_owner_xml_id')]
        if (len(nodes) != 1 or not getattr(nodes[0], d['slot_kind'])
                or getattr(nodes[0], d['slot_kind']).count(before) != 1):
            raise ValueError('Original exact slot absent or ambiguous')
        if text_hash(''.join(item.itertext())) != evidence['canonical_visible_text_sha256']:
            raise ValueError('Canonical article full-visible-content drift')
    return rows


def apply_exact(root, decisions):
    all_ = articles(root)
    snapshots = {key: ET.tostring(all_[key], encoding='utf-8')
                 for key in {d['source_key'] for d in decisions}}
    validated_paras = set()
    edits = []
    for d in decisions:
        item = all_[d['source_key']]
        if item.get(ID) != d['source_article_xml_id']:
            raise ValueError('Different source article')
        matches = [p for p in item.iter(T + 'p')
                   if p.get(ID) == d['source_unit_xml_id']]
        if len(matches) != 1:
            raise ValueError('Wrong paragraph')
        paragraph = matches[0]
        identity = (d['source_key'], d['source_unit_xml_id'])
        if identity not in validated_paras:
            if text_hash(''.join(paragraph.itertext())) != d['source_unit_text_sha256']:
                raise ValueError('Prior editorial paragraph differs from canonical source')
            validated_paras.add(identity)
        nodes = [n for n in paragraph.iter()
                 if n.get(ID) == d['slot_owner_xml_id']]
        if len(nodes) != 1:
            raise ValueError('Missing exact slot owner')
        node = nodes[0]
        attribute = d['slot_kind']
        previous = getattr(node, attribute)
        old = d['original_visible']
        new = d['printed_visible']
        if previous is None or previous.count(old) != 1:
            raise ValueError('Duplicate or missing exact old text')
        if previous.count(new):
            raise ValueError('Proposed new text is already in the prior slot')
        setattr(node, attribute, previous.replace(old, new, 1))
        edits.append((node, attribute, previous, d))
    after_snapshots = {key: ET.tostring(all_[key], encoding='utf-8')
                       for key in snapshots}
    for node, attribute, previous, _ in reversed(edits):
        setattr(node, attribute, previous)
    if any(ET.tostring(all_[key], encoding='utf-8') != xml
           for key, xml in snapshots.items()):
        raise ValueError('An article was not perfectly reversible')
    for node, attribute, previous, d in edits:
        setattr(node, attribute,
                previous.replace(d['original_visible'], d['printed_visible'], 1))
    if any(ET.tostring(all_[key], encoding='utf-8') != xml
           for key, xml in after_snapshots.items()):
        raise ValueError('Final editorial changes differ after reversal check')
    return ({d['source_key'] for d in decisions},
            [{'source_key': d['source_key'],
              'source_unit_xml_id': d['source_unit_xml_id'],
              'original_visible': d['original_visible'],
              'printed_visible': d['printed_visible'],
              'original_page': d['pdf_page'],
              'original_jpeg_sha256': d['jpeg_sha256'],
              'individually_reversible': True}
             for d in decisions])


def run(source, prior, prior_report, prior_validator, ledger, output,
        report, derived_manifest, derived_fidelity):
    paths = [Path(x).resolve() for x in (source, prior, output)]
    if len(set(paths)) != 3:
        raise ValueError('Do not edit earlier edition or canonical source')
    if digest(source) != LOCK:
        raise ValueError('Original CrossWire TEI changed')
    previous = read(prior_report)
    prior_sha = digest(prior)
    if (previous.get('revised_sha256') != prior_sha
            or previous.get('article_count') != 9380
            or previous.get('corrected_prose_fragments') != 8
            or previous.get('publication_permitted') is not False
            or previous.get('original_crosswire_unchanged') is not True):
        raise ValueError('Incorrect previous eight-print-correction baseline')
    validator = read(prior_validator)
    if (validator.get('expected_candidate_sha256') != prior_sha
            or validator.get('noncanonical_review_only') is not True):
        raise ValueError('Earlier editorial stage validation identity mismatch')
    spec = read(ledger)
    research = read('workspace/reviews/1915-article-wide-prose-review-v2.json')
    source_root = ET.parse(source).getroot()
    decisions = validate_ledger(
        spec, source_root, research,
        read('workspace/witnesses/print/1915-volume-witnesses.json'))
    root = ET.parse(prior).getroot()
    baseline_articles = articles(root)
    old_nodes = {key: ET.tostring(article, encoding='utf-8')
                 for key, article in baseline_articles.items()}
    old_ids = [n.get(ID) for a in baseline_articles.values()
               for n in a.iter() if n.get(ID)]
    changed, changes = apply_exact(root, decisions)
    if any(ET.tostring(article, encoding='utf-8') != old_nodes[key]
           for key, article in baseline_articles.items() if key not in changed):
        raise ValueError('Unapproved article was changed')
    dest = Path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(dest, encoding='utf-8', xml_declaration=True)
    after = articles(ET.parse(dest).getroot())
    new_ids = [n.get(ID) for a in after.values()
               for n in a.iter() if n.get(ID)]
    if list(after) != list(baseline_articles) or new_ids != old_ids:
        raise ValueError('Original article IDs/order or XML node IDs changed')
    if any(ET.tostring(a, encoding='utf-8') != old_nodes[key]
           for key, a in after.items() if key not in changed):
        raise ValueError('Unrelated saved article changed')
    profile = analyze(dest)
    if profile['profile_rule_findings'] or profile['duplicate_xml_ids']:
        raise ValueError('Strict TEI profile was violated')
    result = {
        'canonical_sha256': LOCK, 'previous_editorial_sha256': prior_sha,
        'revised_sha256': digest(dest), 'article_count': len(after),
        'additional_print_fragments_corrected': len(changes),
        'affected_articles': sorted(changed),
        'unaffected_articles': len(after) - len(changed),
        'original_xml_ids_preserved': len(new_ids),
        'canonical_source_unchanged': True,
        'previous_editorial_layer_unchanged': True,
        'full_historical_collation_certified': False,
        'independent_human_peer_review': False,
        'publication_permitted': False,
        'changes': changes,
    }
    derived = {**validator,
               'expected_candidate_sha256': result['revised_sha256'],
               'noncanonical_review_only': True,
               'review_delta_ledger': str(ledger)}
    fidelity = {
        'candidate_sha256': result['revised_sha256'],
        'article_parity': 'PASS', 'serialized_profile_check': 'PASS',
        'publication_permitted': False, 'noncanonical': True,
        'independent_human_peer_review': False,
        'additional_reviewed_print_fragments': len(changes),
    }
    for file, data in ((report, result), (derived_manifest, derived),
                       (derived_fidelity, fidelity)):
        out = Path(file)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n',
                       encoding='utf-8')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, default=Path('workspace/witnesses/crosswire-2.2/ISBE.xml'))
    for name in ('prior', 'prior-report', 'prior-validator', 'ledger',
                 'output', 'report', 'derived-manifest', 'derived-fidelity'):
        p.add_argument('--' + name, type=Path, required=True)
    args = p.parse_args()
    result = run(args.source, args.prior, args.prior_report,
                 args.prior_validator, args.ledger, args.output,
                 args.report, args.derived_manifest, args.derived_fidelity)
    print(json.dumps({
        'additional_print_fragments_corrected': result['additional_print_fragments_corrected'],
        'affected_articles': result['affected_articles'],
        'full_historical_collation_certified': False,
        'publication_permitted': False,
    }, indent=2))


if __name__ == '__main__':
    main()
