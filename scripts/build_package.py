#!/usr/bin/env python3
"""Build a checksum-manifested, shareable plugin ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PLUGIN_NAME = "codex-self-growing-memory"
VERSION = "1.1.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the shareable plugin archive.")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def included_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".zip"}:
            continue
        if path.name == "PACKAGE-CHECKSUMS.json":
            continue
        files.append(path)
    return sorted(files, key=lambda item: str(item.relative_to(root)))


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    files = included_files(root)
    manifest = {
        "plugin": PLUGIN_NAME,
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files": [
            {
                "path": str(path.relative_to(root)),
                "size": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in files
        ],
    }
    checksum_path = root / "PACKAGE-CHECKSUMS.json"
    checksum_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    output = (
        args.output.expanduser().resolve()
        if args.output
        else root.parent / f"{PLUGIN_NAME}-{VERSION}.zip"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in included_files(root) + [checksum_path]:
            arcname = Path(root.name) / path.relative_to(root)
            archive.write(path, arcname)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(
        json.dumps(
            {
                "status": "built",
                "archive": str(output),
                "size": output.stat().st_size,
                "sha256": digest,
                "files": len(manifest["files"]) + 1,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
