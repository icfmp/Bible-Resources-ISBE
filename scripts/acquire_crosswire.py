#!/usr/bin/env python3
"""Acquire CrossWire's original ISBE package without changing archive bytes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile

SOURCE = "https://www2.crosswire.org/ftpmirror/pub/sword/raw/packages/ISBE.zip"
DEST = Path("sources/crosswire/isbe-2.2")
ARCHIVE = DEST / "ISBE.zip"
MANIFEST = DEST / "MANIFEST.json"
MAX_SIZE = 100 * 1024 * 1024


def run():
    DEST.mkdir(parents=True, exist_ok=True)
    if ARCHIVE.exists() or MANIFEST.exists():
        if not (ARCHIVE.exists() and MANIFEST.exists()):
            raise RuntimeError("Partial previous acquisition: inspect before retry")
        recorded = json.loads(MANIFEST.read_text(encoding="utf-8"))
        actual = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
        if recorded["archive_sha256"] != actual:
            raise RuntimeError("Existing immutable archive hash mismatch")
        print("Existing archive verified", actual)
        return
    request = Request(SOURCE, headers={"User-Agent": "Bible-Resources-ISBE provenance acquisition"})
    tmp = DEST / "ISBE.zip.part"
    sha = hashlib.sha256()
    length = 0
    try:
        with urlopen(request, timeout=120) as response, tmp.open("wb") as out:
            while chunk := response.read(1024 * 1024):
                length += len(chunk)
                if length > MAX_SIZE:
                    raise RuntimeError("Unexpected upstream archive size")
                sha.update(chunk)
                out.write(chunk)
        if not zipfile.is_zipfile(tmp):
            raise RuntimeError("CrossWire download is not a ZIP archive")
        with zipfile.ZipFile(tmp) as z:
            bad = z.testzip()
            if bad:
                raise RuntimeError(f"Corrupted ZIP member: {bad}")
            names = z.namelist()
            if not any(x.lower().endswith("isbe.conf") for x in names):
                raise RuntimeError("ISBE SWORD configuration is missing")
            if not any(x.startswith("modules/") for x in names):
                raise RuntimeError("SWORD module data is missing")
            if any(x.startswith("/") or ".." in Path(x).parts for x in names):
                raise RuntimeError("Unsafe ZIP member path")
        tmp.rename(ARCHIVE)
        metadata = {
            "source": "CrossWire SWORD raw module package",
            "module": "ISBE",
            "expected_module_version": "2.2",
            "download_url": SOURCE,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "archive_filename": "ISBE.zip",
            "archive_bytes": length,
            "archive_sha256": sha.hexdigest(),
            "zip_file_count": len(names),
            "zip_members": names,
            "license_evidence_url": "https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=ISBE",
            "redistribution_review": "PENDING_INDEPENDENT_REVIEW",
            "notes": "Exact CrossWire archive preserved; contents not yet editorially checked against print."
        }
        MANIFEST.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
        print("Downloaded and validated", length, sha.hexdigest(), len(names))
    finally:
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    run()
