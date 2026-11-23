#!/usr/bin/env python3
"""Render original 1915 printed pages for HUMAN visual collation.

Outputs a bounded, explicitly delimited JPEG evidence preview to the research
workflow log. Image inspection is required before print-verification flags can
be changed. Never modifies source witness or canonical TEI.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import textwrap


def render_pages(pdf, volume, pages, witness_manifest, max_size=2000):
    manifest = json.loads(Path(witness_manifest).read_text(encoding="utf-8"))
    witness, = [v for v in manifest["volumes"] if v["volume"] == str(volume)]
    digest = hashlib.sha256(Path(pdf).read_bytes()).hexdigest()
    if digest != witness["pdf_sha256"]:
        raise ValueError("Historical scanned PDF sha256 differs from approved provenance")
    if not pages or len(pages) > 4 or len(pages) != len(set(pages)):
        raise ValueError("Expected 1–4 distinct source pages")
    for page in pages:
        if not 1 <= page <= witness["pages"]:
            raise ValueError(f"PDF page outside source printed volume: {page}")
    with tempfile.TemporaryDirectory() as folder:
        for page in pages:
            base = Path(folder) / f"original-1915-{volume}-{page}"
            subprocess.run([
                "pdftoppm", "-f", str(page), "-l", str(page),
                "-singlefile", "-jpeg", "-scale-to", str(max_size),
                "-jpegopt", "quality=67", str(pdf), str(base)
            ], check=True, capture_output=True, timeout=90)
            image = base.with_suffix(".jpg").read_bytes()
            if not 12_000 < len(image) < 1_250_000:
                raise ValueError(f"Unexpected scan JPEG size {len(image)}")
            pic_hash = hashlib.sha256(image).hexdigest()
            print(f"PRINT_IMAGE_START volume={volume} pdf_page={page} "
                  f"original_pdf_sha256={digest} jpeg_sha256={pic_hash} "
                  f"bytes={len(image)}", flush=True)
            payload = base64.b64encode(image).decode("ascii")
            for segment in textwrap.wrap(payload, 192):
                print("B64:" + segment, flush=True)
            print(f"PRINT_IMAGE_END volume={volume} pdf_page={page}", flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", required=True)
    p.add_argument("--volume", required=True)
    p.add_argument("--pages", required=True, help="Comma-separated 1-based PDF page indexes")
    p.add_argument("--manifest", default="workspace/witnesses/print/1915-volume-witnesses.json")
    a = p.parse_args()
    pages = [int(x.strip()) for x in a.pages.split(",")]
    render_pages(a.pdf, a.volume, pages, a.manifest)


if __name__=="__main__":
    main()
