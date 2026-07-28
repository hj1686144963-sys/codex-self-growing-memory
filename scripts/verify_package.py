#!/usr/bin/env python3
"""Validate the distributable plugin package without installing it."""

from __future__ import annotations

import json
import hashlib
import py_compile
import re
import sys
import tempfile
from pathlib import Path

PLUGIN_NAME = "codex-self-growing-memory"
REQUIRED = [
    ".codex-plugin/plugin.json",
    "skills/codex-auto-memory/SKILL.md",
    "skills/codex-auto-memory/references/memory-policy.md",
    "scripts/install.py",
    "scripts/memory_hook.py",
    "scripts/verify.py",
    "scripts/rollback.py",
    "scripts/build_package.py",
    "assets/templates/global-agents-block.md",
    "assets/knowledge-base/START-HERE.md",
    "assets/knowledge-base/AGENTS.md",
    "assets/knowledge-base/08-System/防踩坑记录.md",
    "README.md",
    "SHARE-PROMPT.md",
]


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    checks = []
    for relative in REQUIRED:
        exists = (root / relative).is_file()
        checks.append({"check": f"file:{relative}", "ok": exists})

    try:
        manifest = json.loads(
            (root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        manifest_ok = (
            manifest.get("name") == PLUGIN_NAME
            and bool(re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", manifest.get("version", "")))
        )
    except (OSError, json.JSONDecodeError):
        manifest_ok = False
    checks.append({"check": "manifest", "ok": manifest_ok})

    install_text = (root / "scripts" / "install.py").read_text(encoding="utf-8")
    hooks_ok = all(
        token in install_text
        for token in ("SessionStart", "UserPromptSubmit", "SessionEnd", "merge_user_hooks")
    )
    checks.append({"check": "user_level_hooks_installer", "ok": hooks_ok})

    text_files = list(root.rglob("*.md")) + list(root.rglob("*.json"))
    todo_files = []
    for path in text_files:
        try:
            if "[TODO:" in path.read_text(encoding="utf-8"):
                todo_files.append(str(path.relative_to(root)))
        except OSError:
            pass
    checks.append({"check": "no_placeholders", "ok": not todo_files, "files": todo_files})

    compile_errors = []
    with tempfile.TemporaryDirectory(prefix="codex-memory-verify-") as temp_dir:
        for path in (root / "scripts").glob("*.py"):
            try:
                py_compile.compile(
                    str(path),
                    cfile=str(Path(temp_dir) / f"{path.stem}.pyc"),
                    doraise=True,
                )
            except py_compile.PyCompileError as error:
                compile_errors.append(f"{path.name}: {error}")
    checks.append({"check": "python_syntax", "ok": not compile_errors, "errors": compile_errors})

    checksum_path = root / "PACKAGE-CHECKSUMS.json"
    checksum_ok = True
    checksum_errors = []
    if checksum_path.is_file():
        try:
            manifest = json.loads(checksum_path.read_text(encoding="utf-8"))
            for item in manifest.get("files", []):
                path = root / item["path"]
                if not path.is_file():
                    checksum_errors.append(f"missing:{item['path']}")
                    continue
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest != item["sha256"]:
                    checksum_errors.append(f"changed:{item['path']}")
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
            checksum_errors.append(str(error))
        checksum_ok = not checksum_errors
    checks.append(
        {
            "check": "package_checksums",
            "ok": checksum_ok,
            "detail": "not built yet" if not checksum_path.exists() else "",
            "errors": checksum_errors,
        }
    )

    failed = [check for check in checks if not check["ok"]]
    print(
        json.dumps(
            {
                "status": "pass" if not failed else "fail",
                "plugin": PLUGIN_NAME,
                "checks": checks,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
