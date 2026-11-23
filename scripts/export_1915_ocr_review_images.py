#!/usr/bin/env python3
"""Prepare transient, SHA-locked printed-page research JPEGs for OCR anomalies.

Render only a few numbered pages referenced by exact original 1915 PDF OCR
diagnostic records. This produces NOT FOR PUBLICATION, short-lived internal
evidence to be visually compared with the source image. No article or source
transcription is copied or amended. Never mark print collation complete.
"""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from scripts.audit_1915_article_ocr_word_counts import digest, LOCK


def selected_pages(report, witness, limit=32, include_near_size_end=False):
    if (report.get("schema_version") != 8
            or report.get("canonical_tei_sha256") != LOCK
            or report.get("print_pdf_sha256") != witness["pdf_sha256"]
            or report.get("volume") != witness["volume"]
            or report.get("ocr_not_original_print_certification") is not True
            or report.get("publication_permitted") is not False):
        raise ValueError("Anomalies require an exact source-locked OCR report")
    candidates = report.get("content_candidate_diagnostics")
    if not isinstance(candidates, list) or len(candidates) != report.get(
            "content_candidate_diagnostic_count"):
        raise ValueError("Malformed or partial article review evidence")
    if not candidates:
        raise ValueError("No OCR anomalies for image review")
    pages = defaultdict(list)
    allowed_categories = {
        "similar_length_low_phrase_overlap",
        "long_ocr_span_source_phrases_present",
    }
    seen = set()
    for case in candidates:
        key = case["source_key"]
        if key in seen or case["review_queue"] not in allowed_categories:
            raise ValueError("Duplicated or unsupported research category")
        seen.add(key)
        if (case["candidate_ocr_span_not_an_original_print_certification"] is not True
                or case["print_page_images_directly_compared"] is not False
                or case["publication_permitted"] is not False):
            raise ValueError("Unreviewed OCR source illegally promoted to print proof")
        start = case["initial_heading_scan_pdf_page_1_based"]
        end = case["next_known_heading_scan_pdf_page_1_based"]
        if not (isinstance(start, int) and isinstance(end, int)
                and 1 <= start <= end <= witness["pages"]):
            raise ValueError("Unverified printed PDF page location")
        picks = [(start, "candidate_heading")]
        # Optional original-page boundary research for similar-length cases.
        # The next heading page is only a candidate continuation image; it is
        # NOT proof that the article extends to that page or is fully read.
        if (include_near_size_end
                and case["review_queue"] == "similar_length_low_phrase_overlap"
                and end > start):
            picks.append((end, "following_heading_possible_continuation"))
        if case["review_queue"] == "long_ocr_span_source_phrases_present":
            window = case["unique_fourgram_overlap_footprint"]
            if window:
                picks.extend([
                    (window["window_first_scan_pdf_page_1_based"], "unique_source_match_start"),
                    (window["window_last_scan_pdf_page_1_based"], "unique_source_match_end"),
                ])
            # Verify the far end of an abnormally long printed OCR span.
            picks.append((end, "following_heading"))
        for page, purpose in picks:
            if not (start <= page <= end):
                raise ValueError("Page witness proposed outside article boundary")
            descriptor = {
                "source_key": key, "article_xml_id": case["article_xml_id"],
                "evidence_role": purpose,
                "still_requires_human_image_collation": True,
            }
            if descriptor not in pages[page]:
                pages[page].append(descriptor)
    if len(pages) > limit or not pages:
        raise ValueError(f"Too many/zero transient source-page JPEGs: {len(pages)}")
    return dict(sorted(pages.items()))


def export_research_images(pdf, witness_manifest, volume_report, output_folder,
                           max_size=2200, max_pages=32,
                           include_near_size_end=False):
    witness_source = json.loads(Path(witness_manifest).read_text(encoding="utf-8"))
    if witness_source.get("canonical_tei_sha256") != LOCK:
        raise ValueError("Original printed witness source lock differs")
    report = json.loads(Path(volume_report).read_text(encoding="utf-8"))
    volume = report.get("volume")
    witness, = [v for v in witness_source["volumes"]
                if v["volume"] == volume]
    actual = digest(pdf)
    if actual != witness["pdf_sha256"]:
        raise ValueError("Downloaded original printed 1915 PDF SHA-256 mismatch")
    pages = selected_pages(report, witness, max_pages,
                           include_near_size_end=include_near_size_end)
    output = Path(output_folder)
    output.mkdir(parents=True, exist_ok=True)
    rendered = []
    for page, cases in pages.items():
        prefix = output / f"original-1915-volume-{volume}-pdf-page-{page:04d}"
        subprocess.run([
            "pdftoppm", "-f", str(page), "-l", str(page),
            "-singlefile", "-jpeg", "-scale-to", str(max_size),
            "-jpegopt", "quality=82", str(pdf), str(prefix),
        ], check=True, capture_output=True, timeout=90)
        image = prefix.with_suffix(".jpg")
        if not image.is_file() or not 12_000 < image.stat().st_size < 3_000_000:
            raise ValueError("Unexpected facsimile page size / missing JPEG")
        img_sha = sha256(image.read_bytes()).hexdigest()
        rendered.append({
            "source_pdf_page_1_based": page,
            "research_jpeg_filename": image.name,
            "research_jpeg_sha256": img_sha,
            "jpeg_size_bytes": image.stat().st_size,
            "cases": cases,
            "printed_page_fully_collated": False,
        })
    manifest = {
        "schema_version": 1,
        "original_1915_volume": volume,
        "historical_pdf_sha256": actual,
        "original_canonical_tei_sha256": LOCK,
        "source": witness_source["bibliographic_citation"],
        "source_pdf_page_count": witness["pages"],
        "render_method": "pdftoppm JPEG scale-to=2200 transient internal research",
        "page_images_rendered": len(rendered),
        "publication_permitted": False,
        "historical_source_print_content_certified": False,
        "temporary_internal_evidence_only": True,
        "pages": rendered,
    }
    (output / "research-image-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf", required=True, type=Path)
    p.add_argument("--ocr-report", required=True, type=Path)
    p.add_argument("--volume-manifest", type=Path,
                   default=Path("sources/print/1915-volume-witnesses.json"))
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--include-near-size-end-page", action="store_true",
                   help="Render next-heading scan page too for same-size low-overlap candidates")
    a = p.parse_args()
    manifest = export_research_images(
        a.pdf, a.volume_manifest, a.ocr_report, a.output_dir,
        include_near_size_end=a.include_near_size_end_page,
    )
    print(json.dumps({
        "original_1915_volume": manifest["original_1915_volume"],
        "page_images_rendered": manifest["page_images_rendered"],
        "source_pdf_sha256": manifest["historical_pdf_sha256"],
        "pages": [x["source_pdf_page_1_based"] for x in manifest["pages"]],
        "publication_permitted": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
